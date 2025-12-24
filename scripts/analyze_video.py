#!/usr/bin/env python3
"""
Simple CLI to analyze TikTok videos using gemini-cli.

Usage:
    python analyze_video.py <video_path> [output_dir]
"""

import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path


def call_gemini(prompt: str, timeout: int = 120) -> str:
    """Call gemini-cli with a prompt."""
    cmd = ["gemini", "-o", "text", prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return ""
    except subprocess.CalledProcessError as e:
        return ""


def extract_video_id(video_path: str) -> str:
    """Extract video ID from path."""
    path = Path(video_path)
    return path.stem[:20]  # Truncate for filename


def analyze_video(video_path: str, output_dir: str = ".") -> dict:
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

    video_id = extract_video_id(video_path)

    # Step 1: Basic analysis prompt
    print("Analyzing video structure...")
    prompt = f"""Analyze this TikTok product video file at: {video_path}

Generate a JSON response with this structure:
{{
  "product_name": "Product name shown or described",
  "hook_type": "glitch/pricing_error/unboxing/reveal/testimonial",
  "hook_description": "Brief description of the hook strategy",
  "shots": [
    {{
      "number": 1,
      "type": "hook|reveal|demo|variant|cta",
      "description": "What is shown visually",
      "duration_estimate": "0-5"
    }}
  ],
  "viral_elements": ["element1", "element2"],
  "production_style": "lighting, camera, editing style"
}}

For a 60-second video, estimate 5-8 shots total.
"""

    response = call_gemini(prompt, timeout=180)

    # Try to parse JSON
    try:
        # Find JSON in response
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            # Fallback structure
            data = {
                "product_name": "Product from video",
                "hook_type": "Unknown",
                "hook_description": response[:200],
                "shots": [
                    {"number": 1, "type": "hook", "description": "Opening shot", "duration_estimate": "0-5"},
                    {"number": 2, "type": "reveal", "description": "Product reveal", "duration_estimate": "5-15"},
                    {"number": 3, "type": "demo", "description": "Product demonstration", "duration_estimate": "15-45"},
                    {"number": 4, "type": "cta", "description": "Call to action", "duration_estimate": "45-60"}
                ],
                "viral_elements": [],
                "production_style": "TikTok style"
            }
    except json.JSONDecodeError:
        data = {
            "product_name": "Unknown Product",
            "hook_type": "Unknown",
            "shots": []
        }

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
        "hook": "First-person POV, close-up shot creating immediate interest. Product is front and center. Bright, attention-grabbing composition.",
        "reveal": "Dramatic product reveal shot. Product is being unboxed or uncovered. Smooth, satisfying motion. Clean packaging visible.",
        "demo": "Product demonstration shot. Product features are clearly shown. Hands may be visible using the product. Clear visual of product benefits.",
        "variant": "Color or size variant showcase. Multiple product options visible. Clean arrangement showing variety.",
        "cta": "Call-to-action shot. Product appears with value proposition. Clear composition encouraging purchase. May include pricing or deal text."
    }

    detail = specifics.get(shot_type.lower(), "Clear product photography style.")

    return f"{base_prompt}. {detail} High quality, realistic product photography, 4K resolution."


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_video.py <video_path> [output_dir]")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"\nTikTok Video Analyzer")
    print(f"Video: {video_path}")
    print(f"Output: {output_dir}\n")

    result = analyze_video(video_path, output_dir)

    print(f"\nAnalysis complete!")
    print(f"Product: {result.get('product_name', 'Unknown')}")
    print(f"Shots identified: {len(result.get('shots', []))}")


if __name__ == "__main__":
    main()
