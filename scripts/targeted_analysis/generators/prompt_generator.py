"""
AI Video Prompt Generator (Phase 5).

Converts replication script into shot-by-shot prompts for Veo 3.1/Sora
in markdown code blocks for easy copy-paste.
"""

import subprocess
from loguru import logger

from ..models import ReplicationScript, AnalysisResult, AIVideoPrompts, AIVideoPrompt


def generate_ai_video_prompts(
    script: ReplicationScript,
    analysis: AnalysisResult,
    product_name: str
) -> AIVideoPrompts:
    """
    Generate AI video generation prompts using Gemini (Phase 5).

    Args:
        script: Replication script from Phase 4
        analysis: Analysis result from Phase 3
        product_name: Product name

    Returns:
        AIVideoPrompts object with shot-by-shot prompts
    """
    logger.info("=== PHASE 5: AI VIDEO PROMPTS GENERATION ===")

    # Extract context from script and analysis
    script_preview = script.script_content[:1500]  # First 1500 chars
    structural_context = analysis.structural_analysis[:600]
    character_context = analysis.character_descriptions[:600]

    prompt = f"""You are generating AI video generation prompts for Veo 3.1 / Sora.

**Replication Script:**
{script_preview}...

**Structural Analysis:**
{structural_context}...

**Character Descriptions:**
{character_context}...

---

**Task: Create shot-by-shot prompts in markdown code blocks**

For EACH shot in the Visual Strategy table, generate a detailed prompt that includes:

1. **Camera specs:** Angle (close-up/medium/wide), movement (static/pan/handheld/tracking), lens equivalent
2. **Subject details:** Appearance from character descriptions, specific action, emotion
3. **Lighting & color:** Natural/artificial, direction, shadows, color palette
4. **Background:** Environment, depth, elements
5. **Duration:** Exact seconds from script
6. **Audio cues:** When VO starts/stops, music timing

**Output Format:**

```markdown
# AI Video Generation Prompts | AI视频生成提示词

**Product | 产品:** {product_name}
**Total Shots | 总镜头数:** [X]

---

## Shot 1: Hook | 开场钩子 (00:00-00:03)

```veo-prompt
Close-up shot, handheld camera (iPhone-style, 28mm equivalent). Female subject,
mid-30s, white chunky knit sweater, on residential balcony. Cold winter morning,
visible breath in air. Natural overcast lighting, soft shadows. Background: blurred
cityscape with apartment buildings, depth of field f/2.8. Color palette: cool tones
(blues, grays, muted whites). Camera: Slight handheld shake for authenticity, minimal
stabilization. Subject looks directly at camera with frustrated expression, eyebrows
furrowed. Duration: 3 seconds.

Audio: German voiceover begins at 00:00 - "[First line from DE voiceover]" [Frustrated tone]
Music: None (silent start)
```

## Shot 2: Problem Reveal | 问题揭示 (00:03-00:08)

```veo-prompt
[Detailed prompt for shot 2 following same format...]
```

## Shot 3: [Name] | [中文名称] (MM:SS-MM:SS)

```veo-prompt
[Detailed prompt for shot 3...]
```

[Continue for ALL shots in the script...]

---

**Notes:**
- Each prompt is standalone and detailed
- Character appearance MUST match across all shots
- Lighting and color grading should be consistent
- Audio cues help synchronize generation

**Ready for copy-paste into Veo 3.1 or Sora interface.**
```

**CRITICAL:**
- One prompt per shot
- All prompts in ```veo-prompt code blocks
- Include camera, subject, lighting, audio for EVERY prompt
- Be specific enough for consistent generation across shots
"""

    # Call Gemini
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        prompt
    ]

    logger.info("Calling Gemini for AI video prompts...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=240,
            check=True
        )

        prompts_content = result.stdout
        # Minimal sanitization
        lines = [l for l in prompts_content.split('\n') if not l.strip().startswith(("Loaded", "Server"))]
        prompts_content = '\n'.join(lines)

        # Parse prompts into AIVideoPrompt objects
        # Simple parsing: find all ```veo-prompt blocks
        import re
        shot_pattern = r'## Shot (\d+): (.+?) \((.+?)\)\s*```veo-prompt\s*(.+?)```'
        matches = re.findall(shot_pattern, prompts_content, re.DOTALL)

        prompt_objects = []
        for match in matches:
            shot_num, shot_name, time_range, prompt_text = match
            # Extract duration from time_range (e.g., "00:00-00:03")
            duration = time_range.split('-')[1].split(':')[-1] + 's'

            prompt_obj = AIVideoPrompt(
                shot_number=int(shot_num),
                shot_name=shot_name,
                time_range=time_range,
                duration=duration,
                prompt_text=prompt_text.strip()
            )
            prompt_objects.append(prompt_obj)

        if not prompt_objects:
            # Fallback: create placeholder structure
            logger.warning("Could not parse prompts, using raw output")
            prompt_objects = [
                AIVideoPrompt(
                    shot_number=1,
                    shot_name="Complete Video",
                    time_range=f"00:00-{script.duration}",
                    duration=script.duration,
                    prompt_text=prompts_content[:1000]
                )
            ]

        ai_prompts = AIVideoPrompts(
            video_id=script.video_id,
            product_name=product_name,
            prompts=prompt_objects
        )

        logger.success(f"AI video prompts generated ({len(prompt_objects)} shots)")
        logger.success("✅ PHASE 5 COMPLETE")
        return ai_prompts

    except subprocess.CalledProcessError as e:
        logger.warning(f"Trying flash model: {e.stderr[:100]}")
        cmd[4] = "gemini-3-flash-preview"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=240, check=True)
            prompts_content = '\n'.join([l for l in result.stdout.split('\n') if not l.strip().startswith(("Loaded", "Server"))])

            # Parse prompts
            import re
            shot_pattern = r'## Shot (\d+): (.+?) \((.+?)\)\s*```veo-prompt\s*(.+?)```'
            matches = re.findall(shot_pattern, prompts_content, re.DOTALL)

            prompt_objects = []
            for match in matches:
                shot_num, shot_name, time_range, prompt_text = match
                duration = time_range.split('-')[1].split(':')[-1] + 's'
                prompt_obj = AIVideoPrompt(
                    shot_number=int(shot_num),
                    shot_name=shot_name,
                    time_range=time_range,
                    duration=duration,
                    prompt_text=prompt_text.strip()
                )
                prompt_objects.append(prompt_obj)

            if not prompt_objects:
                prompt_objects = [
                    AIVideoPrompt(
                        shot_number=1,
                        shot_name="Complete Video",
                        time_range=f"00:00-{script.duration}",
                        duration=script.duration,
                        prompt_text=prompts_content[:1000]
                    )
                ]

            ai_prompts = AIVideoPrompts(
                video_id=script.video_id,
                product_name=product_name,
                prompts=prompt_objects
            )

            logger.success(f"AI video prompts generated (fallback, {len(prompt_objects)} shots)")
            logger.success("✅ PHASE 5 COMPLETE")
            return ai_prompts

        except Exception as e2:
            raise RuntimeError(f"AI prompt generation failed: {e2}")
