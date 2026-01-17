"""
Replication Script Generator (Phase 4).

Generates a single replication script that 100% copies structure/hook/timing
with slightly varied dialogue.
"""

import subprocess
from pathlib import Path
from datetime import datetime
from loguru import logger

from ..models import AnalysisResult, VideoMetadata, ReplicationScript


def generate_replication_script(
    analysis: AnalysisResult,
    metadata: VideoMetadata,
    product_name: str
) -> ReplicationScript:
    """
    Generate replication script using Gemini (Phase 4).

    Args:
        analysis: Combined analysis from Phase 3
        metadata: Video metadata
        product_name: Product name for script

    Returns:
        ReplicationScript object
    """
    logger.info("=== PHASE 4: REPLICATION SCRIPT GENERATION ===")

    # Context from analysis (truncated to fit)
    structural_context = analysis.structural_analysis[:800]
    content_context = analysis.content_analysis[:800]
    strategic_context = analysis.strategic_analysis[:600]

    # Format duration as MM:SS
    duration_mm = int(metadata.duration // 60)
    duration_ss = int(metadata.duration % 60)
    duration_str = f"{duration_mm:02d}:{duration_ss:02d}"

    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""You are creating a TikTok video script that replicates the analyzed video's structure.

**Original Video:**
- Creator: {metadata.creator}
- Duration: {metadata.duration:.0f}s
- Views: {metadata.views or 'N/A'}

**Product to Promote:**
{product_name}

**Analysis Context:**

STRUCTURAL:
{structural_context}...

CONTENT:
{content_context}...

STRATEGIC:
{strategic_context}...

---

**CRITICAL INSTRUCTION:**
- 100% COPY the structure, hook timing, visual sequence, and shot composition
- SLIGHTLY VARY the dialogue/voiceover - use DIFFERENT WORDS for same meaning
- Example: "Das nervt mich" → "Das stört mich wirklich" (same sentiment, different wording)
- Keep same emotional beats, pacing, and CTA timing

---

**Task: Generate complete Obsidian-ready script**

Output EXACT format:

```markdown
---
cover: ""
caption: >-
  [Punchy German caption with 2-3 hashtags appended at end, space-separated]
published: {today}
duration: "{duration_str}"
sales:
  - yes
link: ""
tags:
  - "#produkttest"
  - "#tiktokshop"
  - "#deutschlandtest"
  - "#[product-related-tag]"
  - "#[interest-tag]"
product: "{product_name}"
source_notes:
  - "targeted_analysis/YYYYMMDD/{metadata.video_id}/analysis.md"
---

# Replication Script | 复制脚本

[1-2 sentence concept description matching original video's approach]

## Structure | 结构 ({int(metadata.duration)}s)

- **Hook | 开场钩子:** [Description] (0-3s)
- **Problem/Reveal | 问题揭示:** [Description] (3-8s)
- **Solution/Demo | 解决方案演示:** [Description] (8-20s)
- **Benefits | 优势效果:** [Description] (20-30s)
- **CTA | 行动号召:** [Description] (30-{int(metadata.duration)}s)

## Visual Strategy | 视觉策略

| Seconds | 秒数 | Visual | 画面 | Purpose | 目的 |
|:--------|:-----|:-------|:------|:--------|:------|
| 00-03 | 0-3秒 | [Exact shot from structural analysis] | [精确镜头描述] | Hook | 吸引注意 |
| 03-08 | 3-8秒 | [Exact shot from structural analysis] | [精确镜头描述] | Problem reveal | 展示问题 |
| 08-15 | 8-15秒 | [Exact shot from structural analysis] | [精确镜头描述] | Solution demo | 方案演示 |
| 15-25 | 15-25秒 | [Exact shot from structural analysis] | [精确镜头描述] | Benefits | 优势展示 |
| 25-{int(metadata.duration)} | 25-{int(metadata.duration)}秒 | [Exact shot from structural analysis] | [精确镜头描述] | CTA | 行动号召 |

## Voiceover | 旁白

> with ElevenLabs v3 (alpha) grammar

### DE (German Voiceover | 德语旁白 | {int(metadata.duration)}s)

[tone] German line 1 (slightly varied from original).
[tone] German line 2.
[tone] German line 3.
...

**Rules | 规则:**
- Use ElevenLabs v3 tone markers: [confident], [bright], [warm], [firm], [soft], [curious], [matter-of-fact]
- Match original's pacing and emotion
- Slightly different wording, same meaning
- No pause cues

### ZH (Chinese Translation | 中文翻译 | {int(metadata.duration)}s)

[tone] Chinese translation line 1.
[tone] Chinese translation line 2.
[tone] Chinese translation line 3.
...

## Replication Notes | 复制说明

### What Was Copied 100% | 完全复制的元素

- **[Element 1]:** [Structural element 1] | [结构元素1中文说明]
- **[Element 2]:** [Structural element 2] | [结构元素2中文说明]
- **[Element 3]:** [Timing element] | [时间元素中文说明]
- **[Element 4]:** [Visual composition] | [视觉构图中文说明]

### What Was Adapted | 调整的元素

- **Dialogue | 对话:** [How it was varied] | [如何调整对话]
- **Product | 产品:** [How {product_name} replaces original] | [如何替换产品]

### Production Requirements | 制作要求

- **Equipment | 设备:** [From strategic analysis] | [设备中文说明]
- **Talent | 演员:** [From character descriptions] | [演员中文说明]
- **Budget | 预算:** [Estimate] | [预算估算]

---

**Generated | 生成时间:** {today}
**Ready for | 准备就绪用于:** Video Production | 视频制作
```

**Output MUST be valid Markdown with proper YAML frontmatter.**
"""

    # Call Gemini
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        prompt
    ]

    logger.info("Calling Gemini for replication script...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            check=True
        )

        script_content = result.stdout

        # Remove meta-lines and extract from code block if wrapped
        lines = script_content.split('\n')

        # Check if content is wrapped in markdown code block
        in_code_block = False
        extracted_lines = []
        for line in lines:
            if line.strip().startswith('```markdown') or line.strip().startswith('```yaml'):
                in_code_block = True
                continue
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                continue
            elif not line.strip().startswith(("Loaded", "Server", "Here is", "I will", "To create")):
                if in_code_block or line.strip().startswith('---'):
                    extracted_lines.append(line)

        script_content = '\n'.join(extracted_lines)

        # Ensure starts with ---
        if not script_content.strip().startswith('---'):
            script_content = '---\n' + script_content

        script = ReplicationScript(
            video_id=metadata.video_id,
            product_name=product_name,
            script_content=script_content,
            duration=duration_str
        )

        logger.success(f"Replication script generated ({len(script_content)} chars)")
        logger.success("✅ PHASE 4 COMPLETE")
        return script

    except subprocess.CalledProcessError as e:
        logger.warning(f"Trying flash model: {e.stderr[:100]}")
        cmd[4] = "gemini-3-flash-preview"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=True)
            script_content = '\n'.join([l for l in result.stdout.split('\n') if not l.strip().startswith(("Loaded", "Server"))])
            if not script_content.strip().startswith('---'):
                script_content = '---\n' + script_content
            script = ReplicationScript(
                video_id=metadata.video_id,
                product_name=product_name,
                script_content=script_content,
                duration=duration_str
            )
            logger.success("Replication script generated (fallback)")
            logger.success("✅ PHASE 4 COMPLETE")
            return script
        except Exception as e2:
            raise RuntimeError(f"Script generation failed: {e2}")
