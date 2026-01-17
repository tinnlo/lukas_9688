"""
Content Analysis (Phase 3B).

Analyzes hook, dialogue, music, and product embedding strategy.
"""

import subprocess
from pathlib import Path
from loguru import logger

from ..models import VideoMetadata, TranscriptData, sanitize_gemini_output


def analyze_content(
    frames_dir: Path,
    metadata: VideoMetadata,
    transcript: TranscriptData,
    structural_analysis: str,  # Pass from Phase 3A for context
    duration: float
) -> str:
    """
    Perform content analysis using Gemini (Phase 3B).

    Args:
        frames_dir: Directory with extracted frames
        metadata: Video metadata
        transcript: Transcription data
        structural_analysis: Output from Phase 3A (for context)
        duration: Video duration

    Returns:
        Content analysis markdown
    """
    logger.info("=== Phase 3B: Content Analysis ===")

    # Get frame files
    frame_files = sorted(frames_dir.glob("frame_*.jpg"))

    # Build transcript with timestamps
    transcript_with_timestamps = ""
    for i, seg in enumerate(transcript.segments):
        timestamp = f"[{int(seg.start):02d}:{int(seg.start % 60):02d}]"
        transcript_with_timestamps += f"{timestamp} {seg.text}\n"

    if not transcript_with_timestamps:
        transcript_with_timestamps = "(No transcript available - music/silent video)"

    # Load hook patterns reference
    hook_patterns_file = Path(__file__).parent.parent.parent.parent / "doc" / "Tiktok_Golden_3_seconds.md"
    hook_patterns = ""
    if hook_patterns_file.exists():
        with open(hook_patterns_file, 'r', encoding='utf-8') as f:
            hook_patterns = f.read()[:1000]  # First 1000 chars

    prompt = f"""You are analyzing TikTok video content for exact replication.

**Video Info:**
- Duration: {duration:.1f}s
- Creator: {metadata.creator}
- Views: {metadata.views or 'N/A'}
- Language: {transcript.language}

**Transcript with Timestamps:**
{transcript_with_timestamps}

**Hook Pattern Reference (8 Core Types for German TikTok):**
{hook_patterns}

**Context from Structural Analysis:**
{structural_analysis[:500]}...

---

**Task: Comprehensive content breakdown**

**CRITICAL: Output EVERYTHING in BILINGUAL format - English first, then Chinese translation**

Output in Markdown with bilingual headers (English | 中文):

## Hook Dissection | 开场剖析 (First 3 Seconds | 前3秒)

- **Hook Type | 钩子类型:** [Match to one of the 8 patterns above] | [匹配以上8种模式之一]
- **Visual Hook | 视觉钩子:** [What viewer sees in first 3s] | [观众前3秒看到的]
- **Audio Hook | 音频钩子:** [First words or sound] | [第一句话或声音]
- **Combined Effect | 综合效果:** [Why it works together] | [为什么有效]
- **Effectiveness Rating | 效果评级:** [1-10] [Reasoning] | [理由]

## Voiceover Analysis | 旁白分析

Annotate transcript with emotion markers | 标注旁白情绪标记:

[00:00] [Frustrated tone | 沮丧语气] "Das nervt mich schon lange." | "这已经困扰我很久了。"
[00:03] [Curious tone | 好奇语气] "Aber dann habe ich das gefunden." | "但是后来我发现了这个。"
[00:08] [Excited tone | 兴奋语气] "Und es funktioniert wirklich!" | "真的有效！"

**Include | 包含:**
- Emotion/delivery for each line | 每句的情绪/表达方式
- Pacing notes (fast/medium/slow) | 节奏笔记（快/中/慢）
- Emphasis words | 强调词

## Music/Audio Strategy | 音乐/音频策略

- **Music Genre | 音乐类型:** [Style] | [风格]
- **Mood | 情绪:** [Emotion] | [情感]
- **Music Start Point | 音乐开始点:** [Timestamp] | [时间戳]
- **Sync Points | 同步点:** [Where music hits match visuals] | [音乐与视觉的配合点]
- **Volume Balance | 音量平衡:** [VO vs music ratio] | [旁白与音乐比例]

## Product Embedding Timeline | 产品植入时间线

| Timestamp | 时间戳 | How Product Appears | 产品出现方式 | Purpose | 目的 |
|-----------|---------|---------------------|-------------|--------|------|
| 00:05 | 5秒 | Hand holding, close-up | 手持特写 | First reveal | 首次展示 |
| 00:12 | 12秒 | In-use demonstration | 使用演示 | Proof | 证明 |
| 00:25 | 25秒 | Packaging shot | 包装镜头 | Brand emphasis | 品牌强调 |

**Analysis | 分析:**
- Total product screen time | 产品总出镜时间: [X seconds]
- Key selling moments | 关键销售时刻
- Branding visibility strategy | 品牌可见性策略

**Be specific and detailed for exact replication. | 内容需详细具体，便于精确复制。**
"""

    # Build gemini CLI command
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        *[str(f) for f in frame_files],
        prompt
    ]

    logger.info("Calling Gemini for content analysis...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=True
        )

        analysis = result.stdout
        analysis = sanitize_gemini_output(analysis)

        logger.success(f"Content analysis complete ({len(analysis)} chars)")
        return analysis

    except subprocess.CalledProcessError as e:
        # Fallback to flash
        logger.warning(f"Trying flash model: {e.stderr[:100]}")
        cmd[4] = "gemini-3-flash-preview"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            analysis = sanitize_gemini_output(result.stdout)
            logger.success("Content analysis complete (fallback)")
            return analysis
        except Exception as e2:
            raise RuntimeError(f"Content analysis failed: {e2}")
