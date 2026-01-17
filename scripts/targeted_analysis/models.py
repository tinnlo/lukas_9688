"""Data models for targeted video analysis pipeline."""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from loguru import logger


# =============================================================================
# Shared Utilities
# =============================================================================

def sanitize_gemini_output(text: str, required_first_line: Optional[str] = None) -> str:
    """
    Clean Gemini CLI output by removing meta-lines and collapsing excessive empty lines.

    Args:
        text: Raw Gemini output
        required_first_line: Optional expected first line (e.g., "## Shot List")

    Returns:
        Cleaned markdown with max 1 consecutive empty line
    """
    META_LINE_PREFIXES = (
        "Loaded cached credentials.",
        "Server ",
        "Here is",
        "***Note:",
        "I will",
        "I'll",
    )

    lines = text.split('\n')
    cleaned_lines = []
    empty_line_count = 0

    for line in lines:
        # Skip meta-lines
        if any(line.strip().startswith(prefix) for prefix in META_LINE_PREFIXES):
            continue

        # Track empty lines to collapse them (max 1 consecutive empty line)
        if not line.strip():
            empty_line_count += 1
            if empty_line_count == 1:
                cleaned_lines.append(line)
        else:
            empty_line_count = 0
            cleaned_lines.append(line)

    # Ensure first line matches expected header if specified
    if required_first_line and cleaned_lines and not cleaned_lines[0].strip().startswith(required_first_line):
        cleaned_lines.insert(0, required_first_line)

    # Trim leading/trailing empty lines
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    return '\n'.join(cleaned_lines)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class VideoMetadata:
    """Video metadata extracted from TikTok URL (Phase 1)."""

    video_id: str
    url: str
    creator: str
    title: str
    duration: float  # seconds
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    music: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def save_to_file(self, file_path: Path):
        """Save metadata to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TranscriptSegment:
    """A single segment of transcribed audio."""

    start: float  # seconds
    end: float    # seconds
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TranscriptData:
    """Transcription data from hybrid approach (Phase 2)."""

    text: str  # Full transcript
    language: str  # Detected language (de, en, etc.)
    source: str  # 'tiktok_captions', 'whisper_transcription', or 'none'
    confidence: float = 0.0
    segments: List[TranscriptSegment] = field(default_factory=list)
    segment_count: int = 0

    def __post_init__(self):
        """Calculate segment count after initialization."""
        self.segment_count = len(self.segments)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'language': self.language,
            'source': self.source,
            'confidence': self.confidence,
            'segment_count': self.segment_count,
            'segments': [seg.to_dict() for seg in self.segments]
        }

    def save_to_file(self, file_path: Path):
        """Save transcript to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptData':
        """Create from dictionary."""
        segments = [
            TranscriptSegment(**seg) for seg in data.get('segments', [])
        ]
        return cls(
            text=data['text'],
            language=data['language'],
            source=data['source'],
            confidence=data.get('confidence', 0.0),
            segments=segments
        )


@dataclass
class AnalysisResult:
    """Combined analysis result from Phase 3."""

    video_id: str
    structural_analysis: str  # Phase 3A markdown
    content_analysis: str     # Phase 3B markdown
    strategic_analysis: str   # Phase 3C markdown
    character_descriptions: str  # Phase 3D markdown
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_combined_analysis(self) -> str:
        """Get all analyses combined into single markdown."""
        return f"""# Targeted Video Analysis
**Video ID:** {self.video_id}
**Analysis Date:** {self.analysis_timestamp}

---

# Part 1: Structural Analysis | 结构分析

{self.structural_analysis}

---

# Part 2: Content Analysis | 内容分析

{self.content_analysis}

---

# Part 3: Strategic Analysis | 策略分析

{self.strategic_analysis}

---

# Part 4: Character Descriptions | 角色描述

{self.character_descriptions}

"""

    def save_combined(self, output_path: Path):
        """Save combined analysis to markdown file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.get_combined_analysis())

    def save_character_descriptions(self, output_path: Path):
        """Save character descriptions to separate file (optional, deprecated)."""
        # Character descriptions are now integrated into main analysis.md
        # This method kept for backwards compatibility but not used by default
        logger.warning("save_character_descriptions is deprecated - characters now in analysis.md")
        return


@dataclass
class ReplicationScript:
    """Replication script output from Phase 4."""

    video_id: str
    product_name: str
    script_content: str  # Full markdown with YAML frontmatter
    duration: str  # MM:SS format
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def save_to_file(self, output_path: Path):
        """Save replication script to markdown file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.script_content)


@dataclass
class AIVideoPrompt:
    """Single shot prompt for AI video generation."""

    shot_number: int
    shot_name: str  # e.g., "Hook", "Problem Reveal"
    time_range: str  # e.g., "00:00-00:03"
    duration: str  # e.g., "3s"
    prompt_text: str  # Full prompt for Veo/Sora

    def to_markdown_block(self) -> str:
        """Convert to markdown code block format."""
        return f"""## Shot {self.shot_number}: {self.shot_name} ({self.time_range})

```veo-prompt
{self.prompt_text}
```
"""


@dataclass
class AIVideoPrompts:
    """Collection of AI video prompts for all shots (Phase 5)."""

    video_id: str
    product_name: str
    prompts: List[AIVideoPrompt]
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_markdown(self) -> str:
        """Convert all prompts to markdown document."""
        header = f"""# AI Video Generation Prompts | AI视频生成提示词

**Video ID:** {self.video_id}
**Product:** {self.product_name}
**Generated:** {self.generation_timestamp}
**Total Shots:** {len(self.prompts)}

---

**Instructions for Use:**
1. Copy each code block separately
2. Paste into Veo 3.1 or Sora interface
3. Adjust parameters as needed for your specific use case
4. Generate videos shot by shot

---

"""
        prompt_blocks = '\n\n'.join([p.to_markdown_block() for p in self.prompts])

        footer = f"""

---

**Notes:**
- Each prompt is optimized for AI video generation models
- Maintain consistency in character appearance across shots
- Adjust lighting and color grading to match reference video
- Review generated videos for quality before final assembly

**Generated by:** TikTok Targeted Video Analysis Skill v1.0.0
"""

        return header + prompt_blocks + footer

    def save_to_file(self, output_path: Path):
        """Save prompts to markdown file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_markdown())


@dataclass
class ProcessingStatus:
    """Track processing status for checkpoints."""

    video_id: str
    video_url: str
    product_name: str
    phase_1_complete: bool = False  # Metadata extraction
    phase_2_complete: bool = False  # Frame + audio extraction
    phase_3_complete: bool = False  # Analysis
    phase_4_complete: bool = False  # Replication script
    phase_5_complete: bool = False  # AI prompts
    error_message: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def mark_phase_complete(self, phase: int):
        """Mark a phase as complete."""
        if phase == 1:
            self.phase_1_complete = True
        elif phase == 2:
            self.phase_2_complete = True
        elif phase == 3:
            self.phase_3_complete = True
        elif phase == 4:
            self.phase_4_complete = True
        elif phase == 5:
            self.phase_5_complete = True
            self.completed_at = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Check if all phases are complete."""
        return all([
            self.phase_1_complete,
            self.phase_2_complete,
            self.phase_3_complete,
            self.phase_4_complete,
            self.phase_5_complete
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def save_to_file(self, file_path: Path):
        """Save status to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingStatus':
        """Create from dictionary."""
        return cls(**data)
