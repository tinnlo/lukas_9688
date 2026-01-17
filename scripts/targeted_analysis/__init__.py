"""
Targeted TikTok Video Analysis Module

This module provides functionality for analyzing user-provided TikTok URLs
to extract comprehensive video intelligence for replication purposes.

Main components:
- metadata_extractor: Video ID extraction and metadata fetching (Phase 1)
- frame_processor: Frame extraction, audio processing, transcription (Phase 2)
- analyzers: Structural, content, strategic, character analysis (Phase 3)
- generators: Replication script and AI video prompts (Phases 4-5)
"""

__version__ = "1.0.0"
__author__ = "Claude Code"

from .models import (
    VideoMetadata,
    TranscriptData,
    AnalysisResult,
    ReplicationScript,
    AIVideoPrompt,
)

__all__ = [
    "VideoMetadata",
    "TranscriptData",
    "AnalysisResult",
    "ReplicationScript",
    "AIVideoPrompt",
]
