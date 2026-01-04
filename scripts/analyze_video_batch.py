#!/usr/bin/env python3
"""
Batch TikTok Video Analyzer with FFmpeg + Hybrid Transcription + Gemini

Workflow:
1. FFmpeg extracts keyframes (every 3s) + audio from each video
2. Hybrid transcription: TikTok captions (yt-dlp) → Whisper fallback
3. Gemini analyzes frames + transcript → writes video_N_analysis.md
4. Gemini synthesizes all reports → writes video_synthesis.md

Usage:
    python analyze_video_batch.py <product_id>
"""

import json
import subprocess
import sys
from pathlib import Path

# Import faster-whisper for audio transcription (fallback)
from faster_whisper import WhisperModel


def get_tiktok_captions(video_url: str) -> dict:
    """
    Extract captions from TikTok using yt-dlp.

    Returns:
        dict with 'source', 'language', 'language_probability', 'duration', 'full_text', 'segments'
        Returns None if no captions available
    """
    # Download subtitles directly to temp file
    temp_dir = Path("/tmp/tiktok_subs")
    temp_dir.mkdir(exist_ok=True)

    cmd_download = [
        "yt-dlp",
        "--write-subs", "--write-auto-subs",
        "--sub-lang", "de,en,ru,es,fr,ja,ko,pt,zh-Hans,zh-Hant",
        "--sub-format", "vtt",  # TikTok provides VTT format
        "--skip-download",
        "--convert-subs", "srt",  # Convert to SRT for easier parsing
        "-o", str(temp_dir / "%(id)s.%(ext)s"),
        video_url
    ]

    try:
        subprocess.run(cmd_download, capture_output=True, timeout=60, check=False)

        # Find any SRT subtitle files
        srt_files = list(temp_dir.glob("*.srt"))

        if not srt_files:
            return None

        # Read the first available subtitle file
        for sub_file in srt_files:
            try:
                with open(sub_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse SRT format
                segments = []
                full_text = []

                # Split by double newlines (subtitle blocks)
                blocks = content.strip().split('\n\n')

                for block in blocks:
                    lines = block.strip().split('\n')
                    if len(lines) < 3:
                        continue

                    # Line 1: sequence number (skip)
                    # Line 2: timestamp
                    # Line 3+: text

                    try:
                        timestamp_line = lines[1]
                        text_lines = lines[2:]

                        # Parse timestamp: "00:00:00,000 --> 00:00:03,000"
                        start_str, end_str = timestamp_line.split(' --> ')

                        def parse_srt_time(time_str):
                            """Convert SRT timestamp to seconds"""
                            h, m, s = time_str.replace(',', '.').split(':')
                            return int(h) * 3600 + int(m) * 60 + float(s)

                        start_time = parse_srt_time(start_str)
                        end_time = parse_srt_time(end_str)
                        text = ' '.join(text_lines).strip()

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
                        f.unlink()

                    return {
                        "source": "tiktok_captions",
                        "language": "unknown",  # Will be detected from content
                        "language_probability": 1.0,
                        "duration": segments[-1]["end"] if segments else 0,
                        "full_text": " ".join(full_text),
                        "segments": segments
                    }

            except Exception:
                continue

        return None

    except Exception:
        return None


def detect_language_from_text(text: str) -> tuple:
    """
    Simple language detection from text content.
    Returns (language_code, confidence)
    """
    text_lower = text.lower()

    # German indicators
    german_words = ['und', 'der', 'die', 'das', 'ist', 'nicht', 'für', 'mit', 'sie', 'ich',
                    'bitte', 'danke', 'guten', 'tag', 'haben', 'sein', 'werden', 'können']
    german_count = sum(1 for word in german_words if word in text_lower)

    # Russian indicators (Cyrillic)
    russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    russian_ratio = russian_chars / len(text) if text else 0

    # English indicators
    english_words = ['the', 'is', 'and', 'to', 'of', 'a', 'in', 'for', 'that', 'with',
                     'you', 'this', 'are', 'it', 'on']
    english_count = sum(1 for word in english_words if word in text_lower.split())

    if russian_ratio > 0.3:
        return ('ru', 0.9)
    elif german_count > 3:
        return ('de', 0.8)
    elif english_count > 3:
        return ('en', 0.8)
    else:
        return ('unknown', 0.5)


def transcribe_audio_fallback(audio_path: Path) -> dict:
    """
    Transcribe audio using faster-whisper (fallback when captions not available).

    Returns:
        dict with 'language', 'language_probability', 'duration', 'full_text', and 'segments'
    """
    # Use base model for speed
    model = WhisperModel("base", device="cpu", compute_type="int8")

    # Transcribe with auto language detection
    segments, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
        word_timestamps=True
    )

    # Build result
    result = {
        "source": "whisper_transcription",
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "full_text": "",
        "segments": []
    }

    all_text = []
    for segment in segments:
        seg_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        }
        result["segments"].append(seg_data)
        all_text.append(segment.text.strip())

    result["full_text"] = " ".join(all_text)

    return result


def get_transcript(video_url: str = None, audio_path: Path = None) -> dict:
    """
    Get transcript using hybrid approach:
    1. Try yt-dlp for TikTok captions (fastest)
    2. Fall back to Whisper transcription
    3. Return None if both fail

    Args:
        video_url: TikTok video URL (for yt-dlp)
        audio_path: Path to audio file (for Whisper fallback)

    Returns:
        dict with transcript data or None
    """
    # Try TikTok captions first
    if video_url:
        transcript = get_tiktok_captions(video_url)
        if transcript and transcript.get("segments"):
            # Detect language from caption content
            lang, confidence = detect_language_from_text(transcript["full_text"])
            transcript["language"] = lang
            transcript["language_probability"] = confidence
            return transcript

    # Fall back to Whisper
    if audio_path and audio_path.exists():
        return transcribe_audio_fallback(audio_path)

    # Both failed
    return None


def extract_keyframes_and_audio(video_path: Path, output_dir: Path, interval: int = 3):
    """
    Extract keyframes every N seconds and audio track using FFmpeg.

    Args:
        video_path: Path to video file
        output_dir: Output directory for frames and audio
        interval: Extract frame every N seconds

    Returns:
        Tuple of (frames_dir, audio_path, video_duration, frame_count)
    """
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Get video duration
    cmd_duration = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    result = subprocess.run(cmd_duration, capture_output=True, text=True)
    duration = float(result.stdout.strip())

    # Extract keyframes every N seconds
    cmd_frames = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",
        str(frames_dir / "frame_%03d.jpg"),
        "-y"
    ]
    subprocess.run(cmd_frames, check=True, capture_output=True)

    # Extract audio (skip gracefully if no audio stream)
    audio_path = output_dir / "audio.mp3"
    cmd_audio = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "libmp3lame",
        "-q:a", "2",
        str(audio_path),
        "-y"
    ]
    try:
        subprocess.run(cmd_audio, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        audio_path = None

    # Count extracted frames
    frame_count = len(list(frames_dir.glob("frame_*.jpg")))

    return frames_dir, audio_path, duration, frame_count


def analyze_video_with_gemini(
    video_path: Path,
    frames_dir: Path,
    transcript: dict,
    duration: float,
    frame_count: int,
    metadata: dict,
    product_name: str
):
    """
    Analyze video using gemini-cli with extracted frames and transcript.

    Args:
        video_path: Path to original video
        frames_dir: Directory with extracted frames
        transcript: Dict with transcribed audio
        duration: Video duration in seconds
        frame_count: Number of frames extracted
        metadata: Video metadata from tabcut_data.json

    Returns:
        Analysis markdown content
    """
    # Get all frame files
    frame_files = sorted(frames_dir.glob("frame_*.jpg"))

    # Format transcript with timestamps
    transcript_text = ""
    if transcript and transcript.get("segments"):
        lang = transcript.get("language", "unknown").upper()
        transcript_text = f"""
**Language Detected:** {lang} (Confidence: {transcript.get('language_probability', 0):.2f})

**Original Transcript:**
```
"""
        for seg in transcript["segments"]:
            start_min, start_sec = divmod(int(seg["start"]), 60)
            timestamp = f"[{start_min:02d}:{start_sec:02d}]"
            transcript_text += f"{timestamp} {seg['text']}\n"

        transcript_text += "```\n\n**中文翻译:**\n```\n"
        transcript_text += "[Please translate the above transcript to Chinese line by line]\n```\n"
    else:
        transcript_text = "**No voiceover detected** - Background music or silent\n"

    # Build gemini prompt
    prompt = f"""Analyze this TikTok ad video in EXTREME DETAIL for market intelligence with BILINGUAL output (English + Chinese):

**VIDEO:** {video_path.name}
**PRODUCT:** {product_name}
**TARGET MARKET:** Germany (TikTok Shop DE)

**PERFORMANCE METADATA:**
- Creator: @{metadata.get('creator_username', 'Unknown')}
- Followers: {metadata.get('creator_followers', 'N/A')}
- Rank: #{metadata.get('rank', 'N/A')}
- Sales: {metadata.get('estimated_sales', 'N/A')} units
- Revenue: {metadata.get('estimated_revenue', 'N/A')}
- Views: {metadata.get('total_views', 'N/A')}
- Published: {metadata.get('publish_date', 'N/A')}
- Duration: {duration:.0f} seconds

**EXTRACTED CONTENT:**
- Keyframes: {frame_count} frames (extracted every 3 seconds)
- Transcript: {transcript.get('language', 'unknown')} voiceover with {len(transcript.get('segments', []))} segments

**YOUR TASK:**

Analyze the keyframe images and the provided transcript to create a comprehensive market intelligence report.

## 2. Voiceover/Dialogue Transcript | 旁白/对话文本

{transcript_text}

## 3. Hook/Opening Strategy (First 3 Seconds) | 开场策略(前3秒)

- **Hook Type | 钩子类型:** [Problem-Solution/Pricing-FOMO/Educational/Feature-Led/Pattern-Interrupt/Unboxing/Testimonial]
- **Hook Description | 策略描述:** [Specific strategy used in first 3 seconds]
- **Visual + Audio Combination | 视觉+音频组合:** [How visuals and audio work together]
- **Effectiveness | 有效性:** [Why this hook works/doesn't work]

## 4. Shot-by-Shot Storyboard | 分镜脚本

Analyze ALL {frame_count} keyframes to identify distinct shots/scenes:

| Shot | Time (MM:SS-MM:SS) | Visual Action | Voiceover | Purpose |
|:-----|:-------------------|:--------------|:----------|:--------|
| 1 | 00:00-00:03 | [Describe frame_001.jpg] | [VO at this time] | Hook |
| 2 | 00:03-00:06 | [Describe frame_002.jpg] | [VO at this time] | Problem/Feature |
| ... | ... | ... | ... | ... |

## 5. Visual Elements Catalog | 视觉元素目录

- **Graphics/Text Overlays | 文字叠加:** [What text appears on screen]
- **Product Showcase | 产品展示:** [How product is displayed]
- **Transitions | 转场:** [Fast cuts/slow reveals/etc.]
- **Color Grading | 调色:** [Bright/saturated/natural/etc.]
- **Lighting | 灯光:** [Natural/studio/ring light/etc.]

## 6. Music/Audio Analysis | 音乐/音频分析

- **Genre:** [Type of background music]
- **Mood:** [Energetic/calm/urgent/playful]
- **Audio Quality:** [Human voice/TTS/music-only]
- **Sync:** [How audio matches visual cuts]

## 7. Key Selling Points

Identify which product features are emphasized:

1. [Feature 1] - Time allocation: ~Xs - Presentation: [Demo/claim/testimonial]
2. [Feature 2] - Time allocation: ~Xs - Presentation: [...]
3. [Feature 3] - ...

## 8. Creative Strategy & Execution

- **Production Style:** [UGC/Professional/Hybrid]
- **Germany Market Fit:** [Cultural alignment, language appropriateness]
- **Authenticity:** [How genuine vs scripted it feels]
- **Viral Elements:** [What makes it shareable]

## 9. Call-to-Action Analysis

- **CTA Type:** [Verbal/Visual/Text overlay]
- **Timing:** [When CTA appears in video]
- **Urgency/Incentive:** [FOMO/discount/limited stock]
- **Strength Rating:** X/10 - [Reasoning]

## 10. Target Audience Inference

- **Demographics:** [Age range, gender, location]
- **Psychographics:** [Interests, values, pain points addressed]
- **Language Signals:** [What language cues reveal about audience]

## 11. Effectiveness Rating (7-Dimension Breakdown)

| Dimension | Score | Reasoning |
|:----------|:------|:----------|
| **Hook Strength** | X/10 | [Why this score] |
| **Pacing & Retention** | X/10 | [Why this score] |
| **Visual Quality** | X/10 | [Why this score] |
| **Trust Signals** | X/10 | [Why this score] |
| **Value Clarity** | X/10 | [Why this score] |
| **CTA Effectiveness** | X/10 | [Why this score] |
| **Overall Effectiveness** | **X.X/10** | [Average + overall assessment] |

**Performance Context:** With {metadata.get('total_views', 'N/A')} views and {metadata.get('estimated_sales', 'N/A')} sales, this video achieved [conversion rate]% conversion.

## 12. Replication Insights

- **Production Budget:** [Low/Medium/High]
- **Equipment Needed:** [Phone/camera, mic, lighting, editing software]
- **Key Success Factor:** [Most critical element to copy]
- **Reproducible Elements:** [What can be easily replicated]

## 13. Recommendations (DO/DON'T/OPPORTUNITY)

**DO:**
1. [Specific actionable recommendation]
2. [Specific actionable recommendation]
3. [Specific actionable recommendation]

**DON'T:**
1. [Mistake to avoid based on weaknesses observed]
2. [Mistake to avoid]
3. [Mistake to avoid]

**OPPORTUNITY:**
1. [Untapped angle or improvement]
2. [Untapped angle or improvement]
3. [Untapped angle or improvement]

---

**CRITICAL REQUIREMENTS:**
- Base analysis on ACTUAL frames provided
- Use the transcript provided above (already transcribed by Whisper)
- Provide specific timestamps and visual descriptions
- ALL section headers must be bilingual (English | 中文)
- Voiceover transcripts MUST include Chinese translation
- Focus on actionable market intelligence
- Maintain bilingual format throughout (English + Chinese)
"""

    # Build gemini-cli command with files
    # Only pass frame images (transcript is in the prompt)
    cmd = ["gemini", "-o", "text"]

    # Add all frame images
    for frame_file in frame_files:
        cmd.append(str(frame_file))

    # Add the prompt last
    cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=True,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"# Analysis Failed: Timeout\n\nVideo: {video_path.name}"
    except subprocess.CalledProcessError as e:
        return f"# Analysis Failed: {e}\n\nVideo: {video_path.name}\n\nError: {e.stderr}"


def analyze_all_videos(product_id: str):
    """
    Analyze all videos for a product.

    Args:
        product_id: Product ID (e.g., "1729479916562717270")
    """
    base_dir = Path(__file__).parent.parent
    product_dir = base_dir / "product_list" / product_id
    ref_video_dir = product_dir / "ref_video"
    tabcut_json = product_dir / "tabcut_data.json"
    fastmoss_json = product_dir / "fastmoss_data.json"

    def _load_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)

    def _score_data(data: dict) -> tuple:
        product_name = (data.get("product_info", {}) or {}).get("product_name") or ""
        product_ok = bool(product_name.strip()) and product_name.strip() not in {"Unknown Product", "undefined", "None"}

        top_videos = data.get("top_videos", []) or []
        with_url = sum(
            1 for v in top_videos
            if (v.get("video_url") or v.get("url") or "").strip()
        )
        with_local = sum(
            1 for v in top_videos
            if (v.get("local_path") or "").strip()
        )
        return (1 if product_ok else 0, with_url, with_local, len(top_videos))

    # Load metadata (prefer the richer one if both exist)
    tabcut_data = _load_json(tabcut_json) if tabcut_json.exists() else None
    fastmoss_data = _load_json(fastmoss_json) if fastmoss_json.exists() else None

    if tabcut_data and fastmoss_data:
        tabcut_score = _score_data(tabcut_data)
        fastmoss_score = _score_data(fastmoss_data)
        metadata = fastmoss_data if fastmoss_score > tabcut_score else tabcut_data
    else:
        metadata = tabcut_data or fastmoss_data

    if not metadata:
        print(f"❌ No metadata JSON found for {product_id} (expected tabcut_data.json or fastmoss_data.json)")
        return

    product_name = metadata.get("product_info", {}).get("product_name") or "Unknown Product"

    # Get all videos
    videos = sorted(ref_video_dir.glob("video_*.mp4"))

    if not videos:
        print(f"❌ No videos found in {ref_video_dir}")
        return

    print(f"\n🎬 Found {len(videos)} videos to analyze\n")

    # Analyze each video
    for i, video_path in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] Analyzing {video_path.name}...")

        # Find metadata for this video (match by filename first, then fall back to index)
        video_metadata = {}
        video_url = None
        top_videos = metadata.get("top_videos", []) or []

        for top_video in top_videos:
            local_path = (top_video.get("local_path") or "").strip()
            if local_path and video_path.name in local_path:
                video_metadata = top_video
                video_url = top_video.get("video_url") or top_video.get("url")
                break

        if not video_metadata and 0 <= (i - 1) < len(top_videos):
            video_metadata = top_videos[i - 1] or {}
            video_url = video_metadata.get("video_url") or video_metadata.get("url")

        # Extract frames and audio
        output_dir = ref_video_dir / f"video_{i}_analysis_temp"
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"  ├─ Extracting keyframes and audio...")
        frames_dir, audio_path, duration, frame_count = extract_keyframes_and_audio(
            video_path, output_dir, interval=3
        )
        print(f"  ├─ Extracted {frame_count} frames + audio ({duration:.0f}s)")

        # Get transcript using hybrid approach (TikTok captions first, then Whisper)
        transcript = get_transcript(video_url=video_url, audio_path=audio_path)

        if transcript:
            source = transcript.get("source", "unknown")
            lang = transcript.get("language", "unknown")
            conf = transcript.get("language_probability", 0)
            print(f"  ├─ Transcript: {source} - {lang} (confidence: {conf:.2f})")
        else:
            print(f"  ├─ No transcript available - marking as music/silent")
            transcript = {
                "source": "none",
                "language": "unknown",
                "language_probability": 0.0,
                "duration": duration,
                "full_text": "",
                "segments": []
            }

        # Analyze with gemini
        print(f"  ├─ Analyzing with gemini-cli...")
        analysis_md = analyze_video_with_gemini(
            video_path,
            frames_dir,
            transcript,
            duration,
            frame_count,
            video_metadata,
            product_name
        )

        # Save analysis
        analysis_path = ref_video_dir / f"video_{i}_analysis.md"
        analysis_path.write_text(analysis_md)
        print(f"  └─ ✅ Saved: {analysis_path.name}\n")

        # Keep temp dir for now (don't delete until all videos analyzed)
        # The audio/frames are needed for potential re-analysis
        # import shutil
        # shutil.rmtree(output_dir)

    print(f"✅ All {len(videos)} videos analyzed!\n")
    print("📊 Next step: Run synthesis to create video_synthesis.md")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_video_batch.py <product_id>")
        print("Example: python analyze_video_batch.py 1729479916562717270")
        sys.exit(1)

    product_id = sys.argv[1]
    analyze_all_videos(product_id)


if __name__ == "__main__":
    main()
