#!/usr/bin/env python3
"""
Single TikTok Video Analyzer - Test script for debugging

Usage:
    python analyze_single_video.py <product_id> <video_number>
    Example: python analyze_single_video.py 1729479916562717270 2
"""

import json
import subprocess
import sys
import re
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
    print(f"  ├─ Fetching captions from TikTok (yt-dlp)...")

    # Use yt-dlp to get subtitles in JSON format
    cmd = [
        "yt-dlp",
        "--write-subs", "--write-auto-subs",
        "--sub-lang", "en,de,ru,es,fr,ja,ko,pt,zh-Hans,zh-Hant",
        "--sub-format", "json",
        "--skip-download",
        "--print", "%(subtitles,%(ext)s)s",
        video_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

        # Check if we got any subtitles
        if not result.stdout or "None" in result.stdout or "youtube" not in result.stdout.lower():
            print(f"  ├─ No captions found on TikTok")
            return None

        # Parse the output to get subtitle file path
        # yt-dlp will download subtitle files, we need to read them
        # Let's use a simpler approach - download and read
    except Exception as e:
        print(f"  ├─ yt-dlp error: {e}")
        return None

    # Alternative: Download subtitles directly to temp file
    temp_dir = Path("/tmp/tiktok_subs")
    temp_dir.mkdir(exist_ok=True)

    cmd_download = [
        "yt-dlp",
        "--write-subs", "--write-auto-subs",
        "--sub-lang", "en,de,ru,es,fr,ja,ko,pt,zh-Hans,zh-Hant",
        "--sub-format", "json",
        "--skip-download",
        "-o", str(temp_dir / "%(id)s.%(ext)s"),
        video_url
    ]

    try:
        subprocess.run(cmd_download, capture_output=True, timeout=60, check=False)

        # Find any JSON subtitle files
        json_files = list(temp_dir.glob("*.json"))

        if not json_files:
            print(f"  ├─ No caption files downloaded")
            return None

        # Read the first available subtitle file
        import json as json_mod
        for sub_file in json_files:
            try:
                with open(sub_file, 'r') as f:
                    sub_data = json_mod.load(f)

                if 'events' not in sub_data:
                    continue

                # Convert JSON3 format to our transcript format
                segments = []
                full_text = []

                for event in sub_data['events']:
                    if 'segs' not in event:
                        continue

                    text = ''.join([seg.get('utf8', '') for seg in event['segs']]).strip()
                    if not text:
                        continue

                    start_time = event.get('tStartMs', 0) / 1000.0
                    duration = event.get('dDurationMs', 0) / 1000.0
                    end_time = start_time + duration

                    segments.append({
                        "start": start_time,
                        "end": end_time,
                        "text": text
                    })
                    full_text.append(text)

                if segments:
                    # Detect language from content
                    content_sample = " ".join(full_text[:5])

                    # Clean up temp files
                    for f in json_files:
                        f.unlink()

                    return {
                        "source": "tiktok_captions",
                        "language": "unknown",  # Will be detected from content
                        "language_probability": 1.0,
                        "duration": segments[-1]["end"] if segments else 0,
                        "full_text": " ".join(full_text),
                        "segments": segments
                    }

            except Exception as e:
                continue

        print(f"  ├─ No valid captions found")
        return None

    except Exception as e:
        print(f"  ├─ Error downloading captions: {e}")
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
    print(f"  ├─ Transcribing audio with faster-whisper...")

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

    print(f"  ├─ Detected language: {result['language']} (confidence: {result['language_probability']:.2f})")
    print(f"  ├─ Transcript length: {len(result['segments'])} segments")

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
            print(f"  ├─ Using TikTok captions (language: {lang}, {len(transcript['segments'])} segments)")
            return transcript

    # Fall back to Whisper
    if audio_path and audio_path.exists():
        print(f"  ├─ Falling back to Whisper transcription...")
        return transcribe_audio_fallback(audio_path)

    # Both failed
    print(f"  ├─ No transcript available")
    return None


def extract_keyframes_and_audio(video_path: Path, output_dir: Path, interval: int = 3):
    """
    Extract keyframes every N seconds and audio track using FFmpeg.
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

    # Extract audio
    audio_path = output_dir / "audio.mp3"
    cmd_audio = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "libmp3lame",
        "-q:a", "2",
        str(audio_path),
        "-y"
    ]
    subprocess.run(cmd_audio, check=True, capture_output=True)

    # Count extracted frames
    frame_count = len(list(frames_dir.glob("frame_*.jpg")))

    return frames_dir, audio_path, duration, frame_count


def analyze_video_with_gemini(
    video_path: Path,
    frames_dir: Path,
    transcript: dict,
    duration: float,
    frame_count: int,
    metadata: dict
):
    """
    Analyze video using gemini-cli with extracted frames and transcript.
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
**PRODUCT:** MINISO MS156 AI Translator Earbuds
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

- **Genre | 风格:** [Type of background music]
- **Mood | 情绪:** [Energetic/calm/urgent/playful]
- **Audio Quality | 音频质量:** [Human voice/TTS/music-only]
- **Sync | 同步:** [How audio matches visual cuts]

## 7. Key Selling Points | 核心卖点

Identify which product features are emphasized:

1. [Feature 1] - Time allocation: ~Xs - Presentation: [Demo/claim/testimonial]
2. [Feature 2] - Time allocation: ~Xs - Presentation: [...]
3. [Feature 3] - ...

## 8. Creative Strategy & Execution | 创意策略与执行

- **Production Style | 制作风格:** [UGC/Professional/Hybrid]
- **Germany Market Fit | 德国市场适配:** [Cultural alignment, language appropriateness]
- **Authenticity | 真实性:** [How genuine vs scripted it feels]
- **Viral Elements | 传播元素:** [What makes it shareable]

## 9. Call-to-Action Analysis | 行动号召分析

- **CTA Type | CTA类型:** [Verbal/Visual/Text overlay]
- **Timing | 时机:** [When CTA appears in video]
- **Urgency/Incentive | 紧迫性/激励:** [FOMO/discount/limited stock]
- **Strength Rating | 强度评分:** X/10 - [Reasoning]

## 10. Target Audience Inference | 目标受众推断

- **Demographics | 人口统计:** [Age range, gender, location]
- **Psychographics | 心理特征:** [Interests, values, pain points addressed]
- **Language Signals | 语言信号:** [What language cues reveal about audience]

## 11. Effectiveness Rating (7-Dimension Breakdown) | 有效性评分(7维度分解)

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

## 12. Replication Insights | 复制要点

- **Production Budget | 制作预算:** [Low/Medium/High]
- **Equipment Needed | 所需设备:** [Phone/camera, mic, lighting, editing software]
- **Key Success Factor | 关键成功要素:** [Most critical element to copy]
- **Reproducible Elements | 可复制元素:** [What can be easily replicated]

## 13. Recommendations (DO/DON'T/OPPORTUNITY) | 建议(做/不做/机会)

**DO | 应该做:**
1. [Specific actionable recommendation]
2. [Specific actionable recommendation]
3. [Specific actionable recommendation]

**DON'T | 不应做:**
1. [Mistake to avoid based on weaknesses observed]
2. [Mistake to avoid]
3. [Mistake to avoid]

**OPPORTUNITY | 机会:**
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

    print(f"  ├─ Running gemini with {len(frame_files)} frames")
    print(f"  ├─ Transcript: {transcript.get('language', 'unknown')} with {len(transcript.get('segments', []))} segments")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"# Analysis Failed: Timeout\n\nVideo: {video_path.name}"
    except subprocess.CalledProcessError as e:
        error_msg = f"# Analysis Failed: {e}\n\nVideo: {video_path.name}\n\nStderr: {e.stderr}"
        print(f"  └─ ❌ Error: {e.stderr}")
        return error_msg


def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_single_video.py <product_id> <video_number>")
        print("Example: python analyze_single_video.py 1729479916562717270 2")
        sys.exit(1)

    product_id = sys.argv[1]
    video_num = int(sys.argv[2])

    base_dir = Path(__file__).parent.parent
    product_dir = base_dir / "product_list" / product_id
    ref_video_dir = product_dir / "ref_video"
    tabcut_json = product_dir / "tabcut_data.json"

    # Load metadata
    with open(tabcut_json) as f:
        tabcut_data = json.load(f)

    # Get specific video (with wildcard to match creator username)
    video_files = list(ref_video_dir.glob(f"video_{video_num}_*.mp4"))

    if not video_files:
        print(f"❌ Video not found: {ref_video_dir}/video_{video_num}_*.mp4")
        sys.exit(1)

    video_path = video_files[0]

    print(f"\n🎬 Analyzing video_{video_num}.mp4\n")

    # Find metadata for this video
    video_metadata = {}
    video_url = None
    for top_video in tabcut_data.get("top_videos", []):
        if str(video_num) in top_video.get("local_path", ""):
            video_metadata = top_video
            video_url = top_video.get("video_url") or top_video.get("url")
            break

    # Extract frames and audio
    output_dir = ref_video_dir / f"video_{video_num}_analysis_temp"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"  ├─ Extracting keyframes and audio...")
    frames_dir, audio_path, duration, frame_count = extract_keyframes_and_audio(
        video_path, output_dir, interval=3
    )
    print(f"  ├─ Extracted {frame_count} frames + audio ({duration:.0f}s)")

    # Get transcript using hybrid approach (TikTok captions first, then Whisper)
    transcript = get_transcript(video_url=video_url, audio_path=audio_path)

    # Handle no transcript case
    if not transcript or not transcript.get("segments"):
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
        video_metadata
    )

    # Save analysis
    analysis_path = ref_video_dir / f"video_{video_num}_analysis.md"
    analysis_path.write_text(analysis_md)
    print(f"  └─ ✅ Saved: {analysis_path}\n")


if __name__ == "__main__":
    main()
