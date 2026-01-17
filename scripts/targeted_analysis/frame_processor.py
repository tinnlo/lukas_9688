"""
Frame and audio extraction with transcription (Phase 2).

Extracts keyframes every 2 seconds, extracts audio, and transcribes using
hybrid approach (TikTok captions → Whisper fallback).
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None
    logger.warning("faster-whisper not installed. Audio transcription will fail.")

from .models import TranscriptData, TranscriptSegment


# Global Whisper model cache (singleton pattern for batch processing)
_WHISPER_MODEL = None


def get_whisper_model():
    """Get cached Whisper model (singleton pattern)."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper not installed")
        logger.info("Loading Whisper tiny model (cached for batch processing)...")
        _WHISPER_MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
        logger.success("Whisper model loaded")
    return _WHISPER_MODEL


def extract_keyframes_and_audio(
    video_path: Path,
    output_dir: Path,
    interval: int = 2
) -> Tuple[Path, Optional[Path], float, int]:
    """
    Extract keyframes every N seconds and audio track using FFmpeg.

    Args:
        video_path: Path to video file
        output_dir: Output directory for frames and audio
        interval: Extract frame every N seconds (default: 2s for targeted analysis)

    Returns:
        Tuple of (frames_dir, audio_path, video_duration, frame_count)
    """
    logger.info(f"Extracting keyframes (every {interval}s) and audio...")

    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Get video duration
    cmd_duration = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd_duration, capture_output=True, text=True, check=True)
    duration = float(result.stdout.strip())
    logger.debug(f"Video duration: {duration:.2f}s")

    # Extract keyframes every N seconds
    # Using 640px width (optimized for Gemini), quality 8 (sufficient for analysis)
    cmd_frames = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"scale=640:-1,fps=1/{interval}",  # Interval modified from 3s to 2s
        "-q:v", "8",  # Lower quality (sufficient for Gemini)
        str(frames_dir / "frame_%03d.jpg"),
        "-y",
    ]
    subprocess.run(cmd_frames, check=True, capture_output=True)

    # Extract audio (skip gracefully if no audio stream)
    audio_path = output_dir / "audio.mp3"
    cmd_audio = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        str(audio_path),
        "-y",
    ]
    try:
        subprocess.run(cmd_audio, check=True, capture_output=True)
        logger.success(f"Audio extracted: {audio_path.name}")
    except subprocess.CalledProcessError:
        logger.warning("No audio stream found in video")
        audio_path = None

    # Count extracted frames
    frame_count = len(list(frames_dir.glob("frame_*.jpg")))

    logger.success(
        f"Extracted {frame_count} frames ({duration:.1f}s ÷ {interval}s) and audio"
    )

    return frames_dir, audio_path, duration, frame_count


def get_tiktok_captions(video_url: str) -> Optional[dict]:
    """
    Extract captions from TikTok using yt-dlp (preferred method).

    Args:
        video_url: TikTok video URL

    Returns:
        dict with keys: source, language, full_text, segments
        Returns None if no captions available
    """
    logger.info("Attempting to fetch TikTok captions...")

    # Download subtitles to temp directory
    temp_dir = Path("/tmp/tiktok_targeted_subs")
    temp_dir.mkdir(exist_ok=True)

    cmd_download = [
        "yt-dlp",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang", "de,en,ru,es,fr,ja,ko,pt,zh-Hans,zh-Hant",
        "--sub-format", "vtt",
        "--skip-download",
        "--convert-subs", "srt",
        "-o", str(temp_dir / "%(id)s.%(ext)s"),
        video_url,
    ]

    try:
        subprocess.run(cmd_download, capture_output=True, timeout=60, check=False)

        # Find SRT subtitle files
        srt_files = list(temp_dir.glob("*.srt"))

        if not srt_files:
            logger.info("No TikTok captions found")
            return None

        # Parse first available subtitle file
        for sub_file in srt_files:
            try:
                with open(sub_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse SRT format
                segments = []
                full_text = []

                blocks = content.strip().split("\n\n")

                for block in blocks:
                    lines = block.strip().split("\n")
                    if len(lines) < 3:
                        continue

                    try:
                        timestamp_line = lines[1]
                        text_lines = lines[2:]

                        # Parse: "00:00:00,000 --> 00:00:03,000"
                        start_str, end_str = timestamp_line.split(" --> ")

                        def parse_srt_time(time_str):
                            h, m, s = time_str.replace(",", ".").split(":")
                            return int(h) * 3600 + int(m) * 60 + float(s)

                        start_time = parse_srt_time(start_str)
                        end_time = parse_srt_time(end_str)
                        text = " ".join(text_lines).strip()

                        if text:
                            segments.append({
                                "start": start_time,
                                "end": end_time,
                                "text": text
                            })
                            full_text.append(text)

                    except Exception:
                        continue

                if segments:
                    # Clean up temp files
                    for f in srt_files:
                        try:
                            f.unlink()
                        except:
                            pass

                    logger.success(f"TikTok captions extracted: {len(segments)} segments")

                    return {
                        "source": "tiktok_captions",
                        "language": "unknown",  # Will detect from content
                        "full_text": " ".join(full_text),
                        "segments": segments,
                    }

            except Exception as e:
                logger.debug(f"Failed to parse {sub_file.name}: {e}")
                continue

        return None

    except Exception as e:
        logger.debug(f"TikTok captions extraction failed: {e}")
        return None


def detect_language_from_text(text: str) -> Tuple[str, float]:
    """
    Simple language detection from text content.

    Args:
        text: Text to analyze

    Returns:
        Tuple of (language_code, confidence)
    """
    text_lower = text.lower()

    # German indicators
    german_words = ["und", "das", "der", "die", "ich", "nicht", "ist", "mit", "für"]
    german_count = sum(1 for word in german_words if word in text_lower)

    # Russian indicators
    russian_chars = sum(1 for char in text if '\u0400' <= char <= '\u04FF')

    # English indicators
    english_words = ["the", "and", "is", "to", "for", "this", "that", "with"]
    english_count = sum(1 for word in english_words if word in text_lower)

    # Determine language
    if russian_chars > len(text) * 0.1:
        return ("ru", 0.9)
    elif german_count >= 3:
        return ("de", 0.85)
    elif english_count >= 3:
        return ("en", 0.8)
    else:
        return ("unknown", 0.5)


def transcribe_audio_fallback(audio_path: Path) -> dict:
    """
    Transcribe audio using faster-whisper (fallback when captions not available).

    Args:
        audio_path: Path to audio file

    Returns:
        dict with keys: source, language, language_probability, full_text, segments
    """
    logger.info("Transcribing audio with Whisper (fallback method)...")

    # Get cached model
    model = get_whisper_model()

    # Transcribe with auto language detection (optimized for speed)
    segments, info = model.transcribe(
        str(audio_path),
        beam_size=1,  # Speed optimization
        vad_filter=True,
        word_timestamps=False,
    )

    # Build result
    result = {
        "source": "whisper_transcription",
        "language": info.language,
        "language_probability": info.language_probability,
        "full_text": "",
        "segments": [],
    }

    all_text = []
    for segment in segments:
        seg_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
        }
        result["segments"].append(seg_data)
        all_text.append(segment.text.strip())

    result["full_text"] = " ".join(all_text)

    logger.success(
        f"Whisper transcription complete: {len(result['segments'])} segments, "
        f"language={info.language} ({info.language_probability:.2f})"
    )

    return result


def get_transcript(
    video_url: Optional[str] = None,
    audio_path: Optional[Path] = None
) -> TranscriptData:
    """
    Get transcript using hybrid approach: TikTok captions → Whisper fallback → None.

    Args:
        video_url: TikTok video URL (for caption extraction)
        audio_path: Path to extracted audio (for Whisper fallback)

    Returns:
        TranscriptData object (may have source='none' if all methods fail)
    """
    logger.info("=== Transcript Extraction (Hybrid Approach) ===")

    # Method 1: Try TikTok captions first (fastest)
    if video_url:
        caption_result = get_tiktok_captions(video_url)
        if caption_result:
            # Detect language from text
            lang, confidence = detect_language_from_text(caption_result["full_text"])
            if lang != "unknown":
                caption_result["language"] = lang

            # Convert to TranscriptData
            segments = [
                TranscriptSegment(**seg) for seg in caption_result["segments"]
            ]
            return TranscriptData(
                text=caption_result["full_text"],
                language=caption_result["language"],
                source="tiktok_captions",
                confidence=confidence,
                segments=segments
            )

    # Method 2: Fallback to Whisper transcription
    if audio_path and audio_path.exists():
        try:
            whisper_result = transcribe_audio_fallback(audio_path)

            # Convert to TranscriptData
            segments = [
                TranscriptSegment(**seg) for seg in whisper_result["segments"]
            ]
            return TranscriptData(
                text=whisper_result["full_text"],
                language=whisper_result["language"],
                source="whisper_transcription",
                confidence=whisper_result["language_probability"],
                segments=segments
            )
        except Exception as e:
            logger.warning(f"Whisper transcription failed: {e}")

    # Method 3: No transcript available
    logger.warning("No transcript available (music-only or silent video)")
    return TranscriptData(
        text="",
        language="unknown",
        source="none",
        confidence=0.0,
        segments=[]
    )


def extract_frames_audio_and_transcribe(
    video_path: Path,
    video_url: str,
    output_dir: Path
) -> Tuple[Path, Optional[Path], float, int, TranscriptData]:
    """
    Complete Phase 2: Extract frames, audio, and transcribe.

    Args:
        video_path: Path to downloaded video
        video_url: Original TikTok URL (for caption extraction)
        output_dir: Output directory

    Returns:
        Tuple of (frames_dir, audio_path, duration, frame_count, transcript)
    """
    logger.info("=== PHASE 2: FRAME + AUDIO EXTRACTION + TRANSCRIPTION ===")

    # Step 1: Extract frames and audio
    frames_dir, audio_path, duration, frame_count = extract_keyframes_and_audio(
        video_path, output_dir, interval=2  # 2s for targeted analysis
    )

    # Step 2: Get transcript
    transcript = get_transcript(video_url=video_url, audio_path=audio_path)

    # Step 3: Save transcript to JSON
    transcript_path = output_dir / "transcript.json"
    transcript.save_to_file(transcript_path)
    logger.success(f"Transcript saved to: {transcript_path}")

    logger.success(f"✅ PHASE 2 COMPLETE")
    logger.info(f"   Frames: {frame_count} frames in {frames_dir}")
    logger.info(f"   Audio: {audio_path if audio_path else 'No audio'}")
    logger.info(f"   Transcript: {transcript.source} ({transcript.language}, {len(transcript.segments)} segments)")

    return frames_dir, audio_path, duration, frame_count, transcript
