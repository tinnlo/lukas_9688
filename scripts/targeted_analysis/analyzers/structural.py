"""
Structural Analysis (Phase 3A).

Analyzes shot-by-shot storyboard, camera specs, transitions, and visual composition.
"""

import subprocess
from pathlib import Path
from typing import List
from loguru import logger

from ..models import VideoMetadata, TranscriptData, sanitize_gemini_output


def analyze_structural(
    frames_dir: Path,
    metadata: VideoMetadata,
    transcript: TranscriptData,
    duration: float,
    frame_count: int
) -> str:
    """
    Perform structural analysis using Gemini (Phase 3A).

    Args:
        frames_dir: Directory with extracted frames
        metadata: Video metadata
        transcript: Transcription data
        duration: Video duration in seconds
        frame_count: Number of frames extracted

    Returns:
        Structural analysis markdown
    """
    logger.info("=== Phase 3A: Structural Analysis ===")

    # Build frame paths
    frame_files = sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_files:
        raise RuntimeError(f"No frames found in {frames_dir}")

    # Build prompt
    transcript_preview = transcript.text[:200] + "..." if len(transcript.text) > 200 else transcript.text

    prompt = f"""You are analyzing a TikTok video frame-by-frame for exact replication.

**Video Info:**
- Duration: {duration:.1f}s
- Frames: {frame_count} (every 2 seconds)
- Creator: {metadata.creator}
- Views: {metadata.views or 'N/A'}
- Transcript Source: {transcript.source}
- Language: {transcript.language}
- Transcript Preview: "{transcript_preview}"

**Task: Create a shot-by-shot storyboard**

**CRITICAL: Output EVERYTHING in BILINGUAL format - English first, then Chinese translation**

Output in Markdown with bilingual headers (English | 中文):

## Shot List | 镜头列表

| Shot # | 镜头号 | Time | 时间 | Duration | 时长 | Camera | 拍摄 | Action | 动作 | Audio | 音频 |
|--------|-------|------|-----|----------|-------|--------|------|--------|------|-------|------|
| 1 | 1 | 00:00-00:03 | 0-3秒 | 3s | 3秒 | Close-up, handheld | 近景手持 | Subject looks at camera | 主角看向镜头 | VO: "..." | 旁白..." |
| 2 | 2 | 00:03-00:08 | 3-8秒 | 5s | 5秒 | Medium, static | 中景固定 | Product reveal | 产品展示 | VO: "..." | 旁白..." |

**Instructions | 指令:**
- Identify shot changes (new angle/subject/composition) | 识别镜头变化
- Camera specs: Close-up/Medium/Wide, Static/Pan/Handheld/Tracking | 拍摄规格
- Include exact audio/VO snippets from transcript | 包含精确的旁白片段
- Use timestamps from frames (00:00, 00:02, 00:04, etc.) | 使用时间戳

## Transition Analysis | 转场分析

- **Shot 1→2 | 镜头1→2:** Hard cut at 00:03 | 00:03硬切
- **Shot 2→3 | 镜头2→3:** Dissolve at 00:08 | 00:08淡入淡出

## Text Overlays | 文字叠加

List ALL on-screen text with timestamps | 列出所有屏幕文字及时间戳:
- **[00:00]** "Tag 3" (top-left, white text | 左上角白色文字) | "第3天"
- **[00:05]** "Vorher" (center, bold, red | 居中粗体红色) | "之前"

## Visual Composition | 视觉构图

- **Framing | 构图:** Rule of thirds, subject positioning | 三分法，主体位置
- **Lighting | 灯光:** Natural/Artificial, direction, quality (soft/hard shadows) | 自然/人造，方向，质量
- **Color Grading | 调色:** Overall palette (warm/cool), dominant colors | 整体色调
- **Focal Points | 焦点:** Where eyes are drawn at key moments | 视线关注点

**Output must be detailed and specific for replication. | 输出必须详细具体，便于复制。**
"""

    # Build gemini CLI command
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        *[str(f) for f in frame_files],
        prompt
    ]

    logger.info(f"Calling Gemini with {len(frame_files)} frames...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=True
        )

        analysis = result.stdout
        analysis = sanitize_gemini_output(analysis, "## Shot List")

        logger.success(f"Structural analysis complete ({len(analysis)} chars)")
        return analysis

    except subprocess.TimeoutExpired:
        logger.error("Gemini timeout on structural analysis")
        raise RuntimeError("Structural analysis timed out")
    except subprocess.CalledProcessError as e:
        # Try fallback to flash model
        logger.warning(f"gemini-3-pro failed, trying flash model: {e.stderr}")
        cmd[4] = "gemini-3-flash-preview"  # Replace model name
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            analysis = sanitize_gemini_output(result.stdout, "## Shot List")
            logger.success(f"Structural analysis complete (fallback model)")
            return analysis
        except Exception as e2:
            logger.error(f"Structural analysis failed: {e2}")
            raise RuntimeError(f"Structural analysis failed: {e2}")
