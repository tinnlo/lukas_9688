#!/usr/bin/env python3
"""
Video Frame Extractor using FFmpeg.

Extracts frames from video files at specified intervals or timestamps.
"""

import asyncio
import json
import math
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from loguru import logger


class ExtractionMode(Enum):
    """Frame extraction modes."""
    UNIFORM = "uniform"  # Extract frames at uniform intervals
    SCENES = "scenes"  # Detect scene changes and extract keyframes
    KEYFRAMES = "keyframes"  # Extract only I-frames (keyframes)


@dataclass
class FrameInfo:
    """Information about an extracted frame."""
    index: int
    timestamp: float  # Seconds from video start
    path: Path
    is_key_frame: bool = False
    scene_change: bool = False


class FrameExtractor:
    """
    Extract frames from videos using FFmpeg.

    Requirements:
        - ffmpeg installed and available in PATH
    """

    def __init__(
        self,
        output_dir: Path,
        fps: Optional[float] = None,
        max_frames: int = 50,
        quality: int = 2
    ):
        """
        Initialize frame extractor.

        Args:
            output_dir: Directory to save extracted frames
            fps: Frames per second to extract (None = automatic)
            max_frames: Maximum number of frames to extract
            quality: JPEG quality (1-31, lower is better)
        """
        self.output_dir = Path(output_dir)
        self.fps = fps
        self.max_frames = max_frames
        self.quality = quality

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_video_info(self, video_path: Path) -> dict:
        """
        Get video metadata using FFprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(video_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            data = json.loads(result.stdout)

            # Parse frame rate
            stream = data.get('streams', [{}])[0]
            r_frame_rate = stream.get('r_frame_rate', '30/1')
            num, denom = map(int, r_frame_rate.split('/'))
            fps = num / denom if denom != 0 else 30

            # Get duration
            duration = float(
                data.get('format', {}).get('duration', 0) or
                stream.get('duration', 0)
            )

            return {
                'width': stream.get('width'),
                'height': stream.get('height'),
                'fps': fps,
                'duration': duration,
                'frame_count': int(duration * fps) if duration > 0 else 0
            }

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Failed to get video info: {e}")
            return {}

    def extract_uniform_frames(
        self,
        video_path: Path,
        output_pattern: str = "frame_%03d.jpg"
    ) -> List[FrameInfo]:
        """
        Extract frames at uniform intervals.

        Args:
            video_path: Path to video file
            output_pattern: Output filename pattern

        Returns:
            List of FrameInfo objects
        """
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not in PATH")

        video_info = self.get_video_info(video_path)
        duration = video_info.get('duration', 0)

        if duration == 0:
            raise ValueError(f"Could not determine video duration: {video_path}")

        # Calculate FPS for extraction to get max_frames
        if self.fps is None:
            extract_fps = min(self.max_frames / duration, 5)  # Max 5 fps
        else:
            extract_fps = self.fps

        output_path = self.output_dir / output_pattern

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vf', f'fps={extract_fps:.2f}',
            '-q:v', str(self.quality),
            '-vsync', 'vfr',
            str(output_path),
            '-y'
        ]

        logger.info(f"Extracting frames at {extract_fps:.2f} fps...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=max(60, int(duration * 10)),
                check=True
            )

            # Find all extracted frames
            frames = []
            for frame_file in sorted(self.output_dir.glob("frame_*.jpg")):
                # Extract index from filename
                match = re.search(r'frame_(\d+)', frame_file.name)
                if match:
                    index = int(match.group(1))
                    # Calculate timestamp based on extraction fps
                    timestamp = index / extract_fps
                    frames.append(FrameInfo(
                        index=index,
                        timestamp=timestamp,
                        path=frame_file
                    ))

            logger.info(f"Extracted {len(frames)} frames")
            return frames

        except subprocess.TimeoutExpired:
            logger.error(f"Frame extraction timed out for {video_path}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise

    def detect_scene_changes(
        self,
        video_path: Path,
        threshold: float = 0.3,
        min_scene_length: float = 1.0
    ) -> List[float]:
        """
        Detect scene changes using FFmpeg's select filter.

        Args:
            video_path: Path to video file
            threshold: Scene change threshold (0-1)
            min_scene_length: Minimum seconds between scenes

        Returns:
            List of scene change timestamps
        """
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not in PATH")

        # Use FFmpeg's select filter to detect scene changes
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-filter:v', f'select=\'gt(scene,{threshold})\',showinfo',
            '-f', 'null',
            '-'
        ]

        logger.debug(f"Detecting scenes with threshold {threshold}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=max(60, int(self.get_video_info(video_path).get('duration', 0) * 10)),
                check=False
            )

            # Parse showinfo output for timestamps
            scene_times = []
            pattern = r'pts_time:(\d+\.\d+)'

            for line in result.stderr.split('\n'):
                if 'pts_time' in line:
                    match = re.search(pattern, line)
                    if match:
                        time = float(match.group(1))
                        scene_times.append(time)

            # Filter by minimum scene length
            filtered_times = []
            last_time = -min_scene_length

            for t in sorted(scene_times):
                if t - last_time >= min_scene_length:
                    filtered_times.append(t)
                    last_time = t

            logger.info(f"Detected {len(filtered_times)} scene changes")
            return filtered_times

        except subprocess.TimeoutExpired:
            logger.error("Scene detection timed out")
            return []
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            return []

    def extract_keyframes_at_scenes(
        self,
        video_path: Path,
        scene_times: List[float],
        output_prefix: str = "scene"
    ) -> List[FrameInfo]:
        """
        Extract single keyframe at each scene timestamp.

        Args:
            video_path: Path to video file
            scene_times: List of scene timestamps
            output_prefix: Prefix for output files

        Returns:
            List of FrameInfo objects
        """
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not in PATH")

        frames = []

        for i, timestamp in enumerate(scene_times):
            output_path = self.output_dir / f"{output_prefix}_{i:03d}.jpg"

            # Extract single frame at timestamp
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', str(video_path),
                '-frames:v', '1',
                '-q:v', str(self.quality),
                '-vsync', 'vfr',
                str(output_path),
                '-y'
            ]

            try:
                subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=10,
                    check=True
                )

                frames.append(FrameInfo(
                    index=i,
                    timestamp=timestamp,
                    path=output_path,
                    is_key_frame=True,
                    scene_change=True
                ))

            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to extract frame at {timestamp}s: {e}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout extracting frame at {timestamp}s")

        logger.info(f"Extracted {len(frames)} scene keyframes")
        return frames

    def extract_with_audio(
        self,
        video_path: Path,
        audio_output: str = "audio.mp3"
    ) -> Path:
        """
        Extract audio from video.

        Args:
            video_path: Path to video file
            audio_output: Output filename

        Returns:
            Path to extracted audio file
        """
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not in PATH")

        output_path = self.output_dir / audio_output

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',
            '-acodec', 'libmp3lame',
            '-q:a', '2',
            str(output_path),
            '-y'
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                timeout=max(60, int(self.get_video_info(video_path).get('duration', 0) * 2)),
                check=True
            )
            logger.info(f"Extracted audio to {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e}")
            raise

    def cleanup_temp_frames(self, keep_patterns: Optional[List[str]] = None) -> None:
        """
        Remove temporary frame files, keeping only keyframes.

        Args:
            keep_patterns: List of filename patterns to keep
        """
        if keep_patterns is None:
            keep_patterns = ["scene_", "keyframe_"]

        for frame_file in self.output_dir.glob("frame_*.jpg"):
            should_keep = any(pattern in frame_file.name for pattern in keep_patterns)
            if not should_keep:
                frame_file.unlink()

        logger.debug("Cleaned up temporary frames")
