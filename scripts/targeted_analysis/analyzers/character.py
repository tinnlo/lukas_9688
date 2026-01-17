"""
Character Descriptions (Phase 3D).

Detailed casting guide for all people appearing in the video.
"""

import subprocess
from pathlib import Path
from loguru import logger

from ..models import VideoMetadata, TranscriptData, sanitize_gemini_output


def analyze_character(
    frames_dir: Path,
    metadata: VideoMetadata,
    duration: float,
    transcript: TranscriptData
) -> str:
    """
    Perform character description analysis using Gemini (Phase 3D).

    Args:
        frames_dir: Directory with extracted frames
        metadata: Video metadata
        duration: Video duration
        transcript: Transcription data

    Returns:
        Character descriptions markdown
    """
    logger.info("=== Phase 3D: Character Descriptions ===")

    # Get frame files - use absolute paths
    frame_files = [f.absolute() for f in sorted(frames_dir.glob("frame_*.jpg"))]

    if not frame_files:
        logger.warning(f"No frames found in {frames_dir}")
        return "## Character Count | 角色数量\n\nNo characters detected - frames not accessible."

    prompt = f"""You are creating a detailed casting guide for video replication.

**Video Info:**
- Duration: {duration:.1f}s
- Creator: {metadata.creator}
- Transcript Language: {transcript.language}

**Task: Describe ALL people appearing in the video for casting purposes**

**CRITICAL: Output EVERYTHING in BILINGUAL format - English first, then Chinese translation**

Output in Markdown with bilingual headers (English | 中文):

## Character Count | 角色数量

Total people in video | 视频总人数: [X]

## Character 1: [Role] | [角色] (e.g., "Main Host", "Product Demonstrator" | "主持人", "产品演示者")

**Physical Appearance | 外观特征:**
- Gender | 性别: [Male/Female/Other] | [男/女/其他]
- Age | 年龄: [Specific or range, e.g., "Mid-30s", "25-30"] | [具体或范围]
- Ethnicity | 种族: [If relevant for casting] | [如果与选角相关]
- Hair | 发型: [Color, length, style] | [颜色、长度、风格]
- Build | 体型: [Slim/Average/Athletic/Plus-size, approximate height] | [瘦/标准/健壮/丰满，大概身高]
- Distinctive features | 明显特征: [Glasses, tattoos, facial hair, etc.] | [眼镜、纹身、面部毛发等]

**Clothing | 服装:**
- Top | 上装: [Specific description with colors] | [具体颜色描述]
- Bottom | 下装: [Specific description] | [具体描述]
- Accessories | 配饰: [Jewelry, watches, etc.] | [珠宝、手表等]
- Style | 风格: [Casual/Business/Sporty/etc.] | [休闲/商务/运动等]

**Body Language | 肢体语言:**
- Posture | 姿态: [Relaxed/Confident/Energetic/etc.] | [放松/自信/活力等]
- Hand gestures | 手势: [Specific moments, e.g., "Points at 00:05"] | [具体时刻]
- Facial expressions | 面部表情: [Key moments] | [关键时刻]
- Movement | 动作: [Static/Active/Natural/Choreographed] | [静态/活跃/自然/编排]

**Vocal Characteristics | 声音特征:**
- Language | 语言: [{transcript.language}]
- Tone | 语调: [Warm/Authoritative/Friendly/Excited/etc.] | [温暖/权威/友好/兴奋等]
- Pace | 语速: [Fast/Medium/Slow words per minute] | [快/中/慢]
- Accent | 口音: [If notable] | [如果明显]
- Voice quality | 音质: [Deep/High/Raspy/Clear/etc.] | [低沉/高亢/沙哑/清晰等]

**Screen Time | 出镜时间:**
- Appears at | 出现于: [Timestamps] | [时间戳]
- Total time | 总时长: [Seconds] | [秒]

**Casting Notes | 选角说明:**
[Specific requirements or flexibility for replication] | [复制的具体要求或灵活性]

---

[Repeat for Character 2, 3, etc. if multiple people | 如果有多人，重复角色2、3等]

---

## Background People | 背景人物

[If any people appear in background, briefly describe] | [如果背景有人，简要描述]

**For replication: provide enough detail for accurate casting. | 用于复制：提供足够的详细信息以便准确选角。**
"""

    # Build gemini CLI command
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        *[str(f) for f in frame_files],
        prompt
    ]

    logger.info("Calling Gemini for character analysis...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=240,
            check=True
        )

        analysis = result.stdout
        analysis = sanitize_gemini_output(analysis)

        logger.success(f"Character analysis complete ({len(analysis)} chars)")
        return analysis

    except subprocess.CalledProcessError as e:
        logger.warning(f"Trying flash model: {e.stderr[:100]}")
        cmd[4] = "gemini-3-flash-preview"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=240, check=True)
            analysis = sanitize_gemini_output(result.stdout)
            logger.success("Character analysis complete (fallback)")
            return analysis
        except Exception as e2:
            raise RuntimeError(f"Character analysis failed: {e2}")
