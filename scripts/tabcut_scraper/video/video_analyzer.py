#!/usr/bin/env python3
"""
TikTok Video Analyzer Module.

Analyzes TikTok videos to extract key frames, generate storyboards,
and create AI image prompts for recreation.

This module integrates:
- FFmpeg for frame extraction
- Gemini AI for content analysis
- Vision AI for frame understanding
"""

import asyncio
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from loguru import logger

from .frame_extractor import FrameExtractor, FrameInfo


@dataclass
class ShotAnalysis:
    """Analysis of a single shot in the video."""
    index: int
    start_time: float
    end_time: float
    duration: float
    description: str
    key_frame_path: Path
    visual_elements: List[str] = field(default_factory=list)
    action_description: str = ""
    audio_transcript: str = ""
    shot_type: str = ""  # hook, reveal, demo, cta, etc.


@dataclass
class VideoAnalysis:
    """Complete analysis of a TikTok video."""
    video_id: str
    video_path: Path
    duration: float
    product_name: str = ""
    hook_strategy: str = ""
    viral_elements: List[str] = field(default_factory=list)
    shots: List[ShotAnalysis] = field(default_factory=list)
    key_frames: List[Path] = field(default_factory=list)
    production_notes: List[str] = field(default_factory=list)


class GeminiClient:
    """Wrapper for gemini-cli interactions."""

    def __init__(self, model: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            model: Model name to use (default: None = use default model)
        """
        self.model = model  # None uses gemini-cli default
        self._check_gemini()

    def _check_gemini(self) -> bool:
        """Check if gemini-cli is installed."""
        try:
            result = subprocess.run(
                ['gemini', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("gemini-cli not found. Some features may not work.")
            return False

    async def analyze_text(
        self,
        prompt: str,
        output_format: str = "text"
    ) -> str:
        """
        Send text prompt to Gemini.

        Args:
            prompt: Text prompt
            output_format: Output format (text or json)

        Returns:
            Response text
        """
        cmd = ['gemini', '-o', output_format]
        if self.model:
            cmd.extend(['-m', self.model])
        cmd.append(prompt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )

            if output_format == "json":
                try:
                    data = json.loads(result.stdout)
                    return json.dumps(data, indent=2)
                except json.JSONDecodeError:
                    # Try to extract JSON from output
                    match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                    if match:
                        return match.group(0)
                    return result.stdout

            return result.stdout

        except subprocess.TimeoutExpired:
            logger.error("Gemini request timed out")
            return ""
        except subprocess.CalledProcessError as e:
            logger.error(f"Gemini error: {e.stderr}")
            return ""


class TikTokVideoAnalyzer:
    """
    Main analyzer for TikTok videos.

    Workflow:
    1. Extract frames from video
    2. Detect scene changes
    3. Analyze key frames with vision AI
    4. Generate storyboard with Gemini
    5. Create AI image prompts
    """

    def __init__(
        self,
        output_dir: Path,
        gemini_model: Optional[str] = None
    ):
        """
        Initialize video analyzer.

        Args:
            output_dir: Base output directory for analysis results
            gemini_model: Gemini model to use
        """
        self.output_dir = Path(output_dir)
        self.gemini = GeminiClient(model=gemini_model)
        self.temp_dir = self.output_dir / ".tmp_frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def extract_video_id(self, video_path: Path) -> str:
        """
        Extract video ID from filename or path.

        Args:
            video_path: Path to video file

        Returns:
            Video ID string
        """
        # Try to extract from filename
        name = video_path.stem

        # Look for TikTok video ID pattern (alphanumeric, 8-12 chars)
        match = re.search(r'(\w{8,12})', name)
        if match:
            return match.group(1)

        # Fallback to filename
        return name

    async def extract_frames_and_detect_scenes(
        self,
        video_path: Path
    ) -> tuple[List[FrameInfo], dict]:
        """
        Extract frames and detect scene changes.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (key frames, video info)
        """
        extractor = FrameExtractor(
            output_dir=self.temp_dir,
            max_frames=50
        )

        # Get video info
        video_info = extractor.get_video_info(video_path)
        logger.info(f"Video: {video_info.get('width')}x{video_info.get('height')}, "
                   f"{video_info.get('duration'):.1f}s, {video_info.get('fps'):.1f} fps")

        # Detect scene changes
        scene_times = extractor.detect_scene_changes(
            video_path,
            threshold=0.3,
            min_scene_length=1.0
        )

        # Add start and end if needed
        if not scene_times or scene_times[0] > 0.5:
            scene_times = [0.0] + scene_times

        duration = video_info.get('duration', 0)
        if not scene_times or scene_times[-1] < duration - 1.0:
            scene_times.append(duration - 0.5)

        # Extract keyframes at scene changes
        keyframes = extractor.extract_keyframes_at_scenes(
            video_path,
            scene_times,
            output_prefix="keyframe"
        )

        return keyframes, video_info

    async def analyze_key_frame(self, frame_path: Path) -> Dict[str, Any]:
        """
        Analyze a single key frame using vision AI.

        Args:
            frame_path: Path to frame image

        Returns:
            Analysis dictionary with visual elements, actions, etc.
        """
        # This will be called by external vision AI (MCP tool)
        # For now, return placeholder
        return {
            "description": "Frame analysis pending",
            "visual_elements": [],
            "dominant_colors": [],
            "product_visible": False,
            "text_visible": [],
            "actions": []
        }

    async def generate_storyboard_analysis(
        self,
        video_path: Path,
        keyframes: List[FrameInfo],
        video_info: dict
    ) -> VideoAnalysis:
        """
        Generate complete storyboard analysis using Gemini.

        Args:
            video_path: Path to video file
            keyframes: List of extracted key frames
            video_info: Video metadata

        Returns:
            Complete VideoAnalysis object
        """
        video_id = self.extract_video_id(video_path)

        # Prepare analysis prompt for Gemini
        prompt = f"""Analyze this TikTok product video and create a marketing breakdown.

Video Information:
- Duration: {video_info.get('duration', 0):.1f} seconds
- Resolution: {video_info.get('width')}x{video_info.get('height')}
- Frames Extracted: {len(keyframes)}

Key Frames (timestamp - filename):
{chr(10).join(f"- {kf.timestamp:.1f}s - {kf.path.name}" for kf in keyframes)}

Please provide a JSON response with this structure:
{{
  "product_name": "Product name",
  "hook_strategy": "Description of the viral hook strategy used",
  "viral_elements": ["element1", "element2"],
  "shots": [
    {{
      "index": 1,
      "start_time": 0.0,
      "end_time": 3.5,
      "shot_type": "hook|reveal|demo|variant|cta",
      "description": "Visual description of what happens",
      "visual_elements": ["element1", "element2"],
      "action_description": "What action occurs",
      "audio_hint": "Likely voiceover or audio content"
    }}
  ],
  "production_notes": [
    "Lighting style",
    "Camera technique",
    "Pacing/editing style"
  ]
}}

Estimate shot boundaries based on the frame timestamps ({len(keyframes)} frames total).
"""

        response = await self.gemini.analyze_text(prompt, output_format="json")

        try:
            analysis_data = json.loads(response)

            shots = []
            for shot_data in analysis_data.get("shots", []):
                # Map to keyframe
                kf_idx = min(shot_data["index"] - 1, len(keyframes) - 1)
                keyframe = keyframes[kf_idx] if keyframes else None

                shots.append(ShotAnalysis(
                    index=shot_data["index"],
                    start_time=shot_data.get("start_time", 0.0),
                    end_time=shot_data.get("end_time", 0.0),
                    duration=shot_data.get("end_time", 0.0) - shot_data.get("start_time", 0.0),
                    description=shot_data.get("description", ""),
                    key_frame_path=keyframe.path if keyframe else Path(""),
                    visual_elements=shot_data.get("visual_elements", []),
                    action_description=shot_data.get("action_description", ""),
                    shot_type=shot_data.get("shot_type", "")
                ))

            return VideoAnalysis(
                video_id=video_id,
                video_path=video_path,
                duration=video_info.get('duration', 0),
                product_name=analysis_data.get("product_name", ""),
                hook_strategy=analysis_data.get("hook_strategy", ""),
                viral_elements=analysis_data.get("viral_elements", []),
                shots=shots,
                key_frames=[kf.path for kf in keyframes],
                production_notes=analysis_data.get("production_notes", [])
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            # Create basic analysis from keyframes
            shots = []
            for i, kf in enumerate(keyframes):
                shots.append(ShotAnalysis(
                    index=i + 1,
                    start_time=kf.timestamp,
                    end_time=keyframes[i + 1].timestamp if i + 1 < len(keyframes) else video_info.get('duration', 0),
                    duration=0,
                    description=f"Shot {i + 1}",
                    key_frame_path=kf.path
                ))

            return VideoAnalysis(
                video_id=video_id,
                video_path=video_path,
                duration=video_info.get('duration', 0),
                shots=shots,
                key_frames=[kf.path for kf in keyframes]
            )

    async def generate_image_prompts(
        self,
        analysis: VideoAnalysis
    ) -> str:
        """
        Generate AI image prompts for each shot.

        Args:
            analysis: Video analysis object

        Returns:
            Markdown formatted prompts
        """
        # First, analyze the first keyframe to establish unified scenario
        if analysis.key_frames:
            scenario_prompt = f"""Describe the visual setting and style of this TikTok product video frame in detail.

Focus on:
- Background (color, texture, environment)
- Lighting (type, direction, quality)
- Hands/person if visible (skin tone, manicure, clothing)
- Overall aesthetic (minimal, colorful, industrial, etc.)
- Product photography style

Keep it factual and descriptive for recreating the scene."""

        # Generate prompts using Gemini
        shots_data = []
        for shot in analysis.shots:
            shots_data.append({
                "index": shot.index,
                "shot_type": shot.shot_type,
                "description": shot.description,
                "visual_elements": shot.visual_elements,
                "action": shot.action_description
            })

        prompt = f"""Generate detailed AI image generation prompts for recreating this TikTok product video.

Product: {analysis.product_name}
Hook Strategy: {analysis.hook_strategy}

Shots to recreate:
{json.dumps(shots_data, indent=2)}

For each shot, create a detailed prompt that:
1. Maintains consistency with the unified scenario (same background, lighting, hands, etc.)
2. Describes the camera angle and composition
3. Specifies the visual elements in detail
4. Includes style descriptors (lighting, color, aesthetic)

Return as markdown with sections for each shot, following this format:

## Shot NN: [Shot Type] - [Brief Description]

**Reference:** shot_NN.jpg

**Prompt:**
> [Detailed prompt here]

Include a "Unified Scenario" section at the top describing the consistent visual style across all shots.
"""

        response = await self.gemini.analyze_text(prompt, output_format="text")
        return response

    def save_breakdown_report(self, analysis: VideoAnalysis) -> Path:
        """
        Save the breakdown markdown report.

        Args:
            analysis: Video analysis object

        Returns:
            Path to saved report
        """
        video_id = analysis.video_id
        output_path = self.output_dir / f"tiktok_breakdown_{video_id}.md"

        # Build markdown content
        content = f"""# TikTok Ad Analysis: {analysis.product_name or video_id}

## 1. Overview
**Video ID:** {video_id}
**Duration:** {analysis.duration:.1f} seconds
**Product:** {analysis.product_name or "Unknown"}
**Hook:** {analysis.hook_strategy or "Not analyzed"}

---

## 2. Viral Hook / Meme Strategy
{analysis.hook_strategy or "Analysis pending."}

"""

        if analysis.viral_elements:
            content += "\n**Key Viral Elements:**\n"
            for element in analysis.viral_elements:
                content += f"- {element}\n"

        content += "\n---\n\n## 3. Video Script & Storyboard\n\n"
        content += "| Shot | Time | Visual Action | Voiceover / Dialogue | Asset |\n"
        content += "| :--- | :--- | :--- | :--- | :--- |\n"

        for shot in analysis.shots:
            time_range = f"{shot.start_time:.0f} - {shot.end_time:.0f}"
            asset_name = shot.key_frame_path.name if shot.key_frame_path else ""
            content += f"| **{shot.index:02d}** | {time_range} | **{shot.description}** | | `{asset_name}` |\n"

        content += "\n---\n\n## 4. Production Notes\n"
        for note in analysis.production_notes:
            content += f"*   {note}\n"

        output_path.write_text(content)
        logger.info(f"Saved breakdown report to {output_path}")
        return output_path

    def save_image_prompts(self, analysis: VideoAnalysis, prompts: str) -> Path:
        """
        Save the image prompts markdown.

        Args:
            analysis: Video analysis object
            prompts: Generated prompts text

        Returns:
            Path to saved prompts
        """
        video_id = analysis.video_id
        output_path = self.output_dir / f"image_prompts_{video_id}.md"

        header = f"""# Image Generation Prompts: {analysis.product_name or video_id} ({video_id})

**Objective:** Generate consistent, high-fidelity visual assets for a TikTok product video.

---

"""
        content = header + prompts

        output_path.write_text(content)
        logger.info(f"Saved image prompts to {output_path}")
        return output_path

    async def analyze_video(self, video_path: Path) -> tuple[Path, Path]:
        """
        Complete analysis workflow for a TikTok video.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (breakdown_path, prompts_path)
        """
        logger.info(f"Starting analysis of {video_path.name}")

        # Step 1: Extract frames and detect scenes
        keyframes, video_info = await self.extract_frames_and_detect_scenes(video_path)

        # Step 2: Generate storyboard analysis
        analysis = await self.generate_storyboard_analysis(video_path, keyframes, video_info)

        # Step 3: Save breakdown report
        breakdown_path = self.save_breakdown_report(analysis)

        # Step 4: Generate and save image prompts
        prompts = await self.generate_image_prompts(analysis)
        prompts_path = self.save_image_prompts(analysis, prompts)

        # Step 5: Cleanup temp files
        self._cleanup()

        logger.info("Analysis complete!")
        return breakdown_path, prompts_path

    def _cleanup(self) -> None:
        """Remove temporary frame files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.debug("Cleaned up temporary frames")


async def analyze_video_cli(video_path: str, output_dir: str = ".") -> None:
    """
    CLI entry point for video analysis.

    Args:
        video_path: Path to video file
        output_dir: Output directory for reports
    """
    video = Path(video_path)
    output = Path(output_dir)

    analyzer = TikTokVideoAnalyzer(output_dir=output)

    breakdown_path, prompts_path = await analyzer.analyze_video(video)

    print(f"\n✓ Breakdown report: {breakdown_path}")
    print(f"✓ Image prompts: {prompts_path}")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Analyze TikTok videos")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("-o", "--output", default=".", help="Output directory")

    args = parser.parse_args()

    asyncio.run(analyze_video_cli(args.video, args.output))
