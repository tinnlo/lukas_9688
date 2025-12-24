#!/usr/bin/env python3
"""
TikTok Video Analyzer using gemini-cli MCP.

Analyzes TikTok videos to extract key frames, generate storyboards,
and create AI image prompts for recreation.

Usage:
    python analyze_video_mcp.py <video_path> [output_dir]
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional


# Try to import MCP tools
try:
    from mcp_gemini_cli_mcp_async import gemini_cli_execute
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: MCP not available, falling back to subprocess", file=sys.stderr)


class GeminiMCPClient:
    """Gemini client using MCP or subprocess fallback."""

    def __init__(self):
        self.available = HAS_MCP

    async def analyze(self, prompt: str, timeout: int = 120) -> str:
        """
        Send prompt to Gemini.

        Args:
            prompt: Text prompt
            timeout: Timeout in seconds

        Returns:
            Response text
        """
        if self.available:
            return await self._analyze_mcp(prompt, timeout)
        else:
            return await self._analyze_subprocess(prompt, timeout)

    async def _analyze_mcp(self, prompt: str, timeout: int) -> str:
        """Use MCP tool for analysis."""
        try:
            result = await gemini_cli_execute(
                query=prompt,
                output_format="text",
                timeout=timeout
            )
            return result
        except Exception as e:
            print(f"MCP error: {e}", file=sys.stderr)
            return ""

    async def _analyze_subprocess(self, prompt: str, timeout: int) -> str:
        """Fallback to subprocess."""
        import subprocess
        cmd = ["gemini", "-o", "text", prompt]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            return stdout.decode()
        except asyncio.TimeoutError:
            proc.kill()
            return ""
        except Exception as e:
            return ""


async def analyze_video_structure(video_path: str, client: GeminiMCPClient) -> dict:
    """
    Analyze video structure using Gemini.

    Args:
        video_path: Path to video file
        client: Gemini client

    Returns:
        Analysis data dictionary
    """
    video_name = Path(video_path).name

    prompt = f"""Analyze this TikTok product video: {video_path}

Generate a JSON response with this structure:
{{
  "product_name": "Product name shown or described",
  "hook_type": "glitch/pricing_error/unboxing/reveal/testimonial/problem_solution",
  "hook_description": "Brief description of the hook strategy",
  "shots": [
    {{
      "number": 1,
      "type": "hook|reveal|demo|variant|cta|problem|benefit",
      "description": "What is shown visually",
      "duration_estimate": "0-5"
    }}
  ],
  "viral_elements": ["element1", "element2"],
  "production_style": "lighting, camera, editing style description"
}}

For a {video_name} video, estimate 5-8 shots total.
Be specific about the product name and hook strategy.
"""

    response = await client.analyze(prompt, timeout=180)

    # Try to parse JSON
    try:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except (json.JSONDecodeError, Exception):
        pass

    # Fallback structure
    return {
        "product_name": "Product from video",
        "hook_type": "Unknown",
        "hook_description": response[:200] if response else "Analysis pending",
        "shots": [
            {"number": 1, "type": "hook", "description": "Opening shot", "duration_estimate": "0-5"},
            {"number": 2, "type": "reveal", "description": "Product reveal", "duration_estimate": "5-15"},
            {"number": 3, "type": "demo", "description": "Product demonstration", "duration_estimate": "15-45"},
            {"number": 4, "type": "cta", "description": "Call to action", "duration_estimate": "45-60"}
        ],
        "viral_elements": [],
        "production_style": "TikTok style"
    }


def generate_breakdown_markdown(data: dict, video_id: str) -> str:
    """Generate the breakdown markdown report."""
    content = f"""# TikTok Ad Analysis: {data.get('product_name', video_id)}

## 1. Overview
**Product:** {data.get('product_name', 'Unknown')}
**Hook Type:** {data.get('hook_type', 'Unknown')}
**Hook:** {data.get('hook_description', 'Not analyzed')}

---

## 2. Viral Hook / Meme Strategy
{data.get('hook_description', 'Analysis pending.')}

"""

    if data.get('viral_elements'):
        content += "\n**Key Viral Elements:**\n"
        for element in data['viral_elements']:
            content += f"- {element}\n"

    content += "\n---\n\n## 3. Video Script & Storyboard\n\n"
    content += "| Shot | Type | Time | Visual Action | Voiceover / Dialogue |\n"
    content += "| :--- | :--- | :--- | :--- | :--- |\n"

    for shot in data.get('shots', []):
        shot_num = f"**{shot.get('number', '?'):02d}**"
        shot_type = shot.get('type', '')
        duration = shot.get('duration_estimate', '')
        description = shot.get('description', '')
        content += f"| {shot_num} | {shot_type} | {duration} | **{description}** | |\n"

    content += "\n---\n\n## 4. Production Notes\n"
    content += f"*   {data.get('production_style', 'Standard TikTok production')}\n"

    return content


def generate_image_prompts(data: dict, video_id: str) -> str:
    """Generate the image prompts markdown."""
    product = data.get('product_name', 'Product')

    content = f"""# Image Generation Prompts: {product} ({video_id})

**Objective:** Generate consistent, high-fidelity visual assets for a TikTok product video.

---

## Unified Scenario

Based on the video analysis, maintain these visual elements across all shots:

*   **Style:** TikTok product aesthetic - clean, bright, engaging
*   **Lighting:** Soft, diffused lighting (ring light or natural window light)
*   **Background:** Clean, uncluttered surface that highlights the product
*   **Product Presentation:** Product is clearly visible, well-lit, and the focal point

---

"""

    for shot in data.get('shots', []):
        shot_num = shot.get('number', 1)
        shot_type = shot.get('type', 'shot').title()
        description = shot.get('description', '')

        content += f"""## Shot {shot_num:02d}: {shot_type}

**Reference:** shot_{shot_num:02d}.jpg

**Prompt:**
> {generate_prompt_for_shot(shot_type, description, product)}

---

"""

    return content


def generate_prompt_for_shot(shot_type: str, description: str, product: str) -> str:
    """Generate a detailed prompt for a specific shot type."""
    base_prompt = f"TikTok product video frame, {description}"

    specifics = {
        "Hook": "First-person POV or direct address to camera. Immediate engagement. Energy and enthusiasm.",
        "Reveal": "Dramatic product reveal. Product being unboxed or uncovered. Satisfying motion.",
        "Demo": "Product demonstration. Features clearly shown. Hands using the product.",
        "Variant": "Color or size options displayed. Multiple product arrangements.",
        "Cta": "Call-to-action with product. Value proposition visible. Purchase encouragement.",
        "Problem": "Showing a problem the product solves. Relatable scenario.",
        "Benefit": "Highlighting product benefits. Visual demonstration of results."
    }

    detail = specifics.get(shot_type, "Clear product photography style.")

    return f"{base_prompt}. {detail} High quality, realistic product photography, 4K resolution."


async def analyze_video(video_path: str, output_dir: str = ".") -> dict:
    """
    Analyze a TikTok video and generate reports.

    Args:
        video_path: Path to video file
        output_dir: Output directory for reports

    Returns:
        Analysis results dictionary
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    video_id = Path(video_path).stem[:20]  # Truncate for filename

    client = GeminiMCPClient()

    # Step 1: Analyze video structure
    print("Analyzing video structure...")
    data = await analyze_video_structure(video_path, client)

    # Step 2: Generate breakdown report
    print("Generating breakdown report...")
    breakdown = generate_breakdown_markdown(data, video_id)

    breakdown_path = output / f"tiktok_breakdown_{video_id}.md"
    breakdown_path.write_text(breakdown)
    print(f"Saved: {breakdown_path}")

    # Step 3: Generate image prompts
    print("Generating image prompts...")
    prompts = generate_image_prompts(data, video_id)

    prompts_path = output / f"image_prompts_{video_id}.md"
    prompts_path.write_text(prompts)
    print(f"Saved: {prompts_path}")

    return data


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_video_mcp.py <video_path> [output_dir]")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"\nTikTok Video Analyzer (MCP)")
    print(f"Video: {video_path}")
    print(f"Output: {output_dir}\n")

    result = asyncio.run(analyze_video(video_path, output_dir))

    print(f"\nAnalysis complete!")
    print(f"Product: {result.get('product_name', 'Unknown')}")
    print(f"Shots identified: {len(result.get('shots', []))}")
    print(f"Hook type: {result.get('hook_type', 'Unknown')}")


if __name__ == "__main__":
    main()
