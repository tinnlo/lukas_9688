#!/usr/bin/env python3
"""
Targeted TikTok Video Analysis - Single Video Entry Point

Analyzes a user-provided TikTok URL through 5 phases:
1. Metadata extraction + video download
2. Frame + audio extraction + transcription
3. Comprehensive analysis (structural, content, strategic, character)
4. Replication script generation
5. AI video prompts generation

Usage:
    python analyze_targeted_video.py \
        --url "https://www.tiktok.com/@user/video/123456" \
        --product-name "Product Name" \
        --output-dir "targeted_analysis/20260114"
"""

import argparse
import sys
from pathlib import Path
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from targeted_analysis import metadata_extractor, frame_processor
from targeted_analysis.analyzers import (
    analyze_structural,
    analyze_content,
    analyze_strategic,
    analyze_character
)
from targeted_analysis.generators import (
    generate_replication_script,
    generate_ai_video_prompts
)
from targeted_analysis.models import AnalysisResult, ProcessingStatus


def setup_logging(output_dir: Path):
    """Setup logging to file and console."""
    logger.remove()  # Remove default handler

    # Console: INFO level
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # File: DEBUG level
    log_file = output_dir / "analysis.log"
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB"
    )

    logger.info(f"Logging to: {log_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a targeted TikTok video for replication"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="TikTok video URL"
    )
    parser.add_argument(
        "--product-name",
        required=True,
        help="Product name for script generation"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory (e.g., targeted_analysis/20260114)"
    )
    parser.add_argument(
        "--skip-phases",
        help="Comma-separated phases to skip (e.g., 1,2 to skip metadata and extraction)"
    )

    args = parser.parse_args()

    # Parse skip phases
    skip_phases = set()
    if args.skip_phases:
        skip_phases = {int(p.strip()) for p in args.skip_phases.split(',')}

    # Extract video ID and setup output directory
    video_id = metadata_extractor.extract_video_id(args.url)
    output_dir = Path(args.output_dir) / video_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    setup_logging(output_dir)

    logger.info("=" * 70)
    logger.info("TARGETED VIDEO ANALYSIS - SINGLE VIDEO")
    logger.info("=" * 70)
    logger.info(f"URL: {args.url}")
    logger.info(f"Video ID: {video_id}")
    logger.info(f"Product: {args.product_name}")
    logger.info(f"Output: {output_dir}")
    logger.info("=" * 70)

    # Initialize status tracking
    status = ProcessingStatus(
        video_id=video_id,
        video_url=args.url,
        product_name=args.product_name
    )

    try:
        # ===== PHASE 1: METADATA EXTRACTION =====
        if 1 not in skip_phases:
            metadata, video_path = metadata_extractor.extract_metadata_and_download(
                url=args.url,
                output_dir=output_dir,
                product_name=args.product_name
            )
            status.mark_phase_complete(1)
        else:
            logger.info("⏭️  PHASE 1 SKIPPED")
            # Load existing metadata
            metadata_path = output_dir / "metadata.json"
            import json
            with open(metadata_path, 'r') as f:
                from targeted_analysis.models import VideoMetadata
                metadata = VideoMetadata.from_dict(json.load(f))
            video_path = output_dir / "video.mp4"

        # ===== PHASE 2: FRAME + AUDIO EXTRACTION =====
        if 2 not in skip_phases:
            frames_dir, audio_path, duration, frame_count, transcript = \
                frame_processor.extract_frames_audio_and_transcribe(
                    video_path=video_path,
                    video_url=args.url,
                    output_dir=output_dir
                )
            status.mark_phase_complete(2)
        else:
            logger.info("⏭️  PHASE 2 SKIPPED")
            # Load existing data
            frames_dir = output_dir / "frames"
            audio_path = output_dir / "audio.mp3"
            duration = metadata.duration
            frame_count = len(list(frames_dir.glob("frame_*.jpg")))
            import json
            from targeted_analysis.models import TranscriptData
            with open(output_dir / "transcript.json", 'r') as f:
                transcript = TranscriptData.from_dict(json.load(f))

        # ===== PHASE 3: COMPREHENSIVE ANALYSIS =====
        if 3 not in skip_phases:
            logger.info("=" * 70)
            logger.info("PHASE 3: COMPREHENSIVE ANALYSIS (4 parts)")
            logger.info("=" * 70)

            # 3A: Structural
            structural_analysis = analyze_structural(
                frames_dir, metadata, transcript, duration, frame_count
            )

            # 3B: Content
            content_analysis = analyze_content(
                frames_dir, metadata, transcript, structural_analysis, duration
            )

            # 3C: Strategic
            strategic_analysis = analyze_strategic(
                metadata, transcript, structural_analysis, content_analysis
            )

            # 3D: Character
            character_analysis = analyze_character(
                frames_dir, metadata, duration, transcript
            )

            # Combine and save
            analysis = AnalysisResult(
                video_id=video_id,
                structural_analysis=structural_analysis,
                content_analysis=content_analysis,
                strategic_analysis=strategic_analysis,
                character_descriptions=character_analysis
            )

            analysis.save_combined(output_dir / "analysis.md")
            # Character descriptions now integrated into analysis.md (not separate file)

            logger.success("✅ PHASE 3 COMPLETE - Analysis saved")
            status.mark_phase_complete(3)
        else:
            logger.info("⏭️  PHASE 3 SKIPPED")
            # Load existing analysis
            with open(output_dir / "analysis.md", 'r') as f:
                combined = f.read()
            with open(output_dir / "character_descriptions.md", 'r') as f:
                chars = f.read()
            # Parse (simplified)
            analysis = AnalysisResult(
                video_id=video_id,
                structural_analysis=combined.split("# Part 1:")[1].split("# Part 2:")[0] if "# Part 1:" in combined else "",
                content_analysis=combined.split("# Part 2:")[1].split("# Part 3:")[0] if "# Part 2:" in combined else "",
                strategic_analysis=combined.split("# Part 3:")[1] if "# Part 3:" in combined else "",
                character_descriptions=chars
            )

        # ===== PHASE 4: REPLICATION SCRIPT =====
        if 4 not in skip_phases:
            replication_script = generate_replication_script(
                analysis=analysis,
                metadata=metadata,
                product_name=args.product_name
            )

            script_path = output_dir / "replication_script.md"
            replication_script.save_to_file(script_path)
            logger.success(f"Replication script saved: {script_path}")
            status.mark_phase_complete(4)
        else:
            logger.info("⏭️  PHASE 4 SKIPPED")
            # Load existing script
            with open(output_dir / "replication_script.md", 'r') as f:
                from targeted_analysis.models import ReplicationScript
                replication_script = ReplicationScript(
                    video_id=video_id,
                    product_name=args.product_name,
                    script_content=f.read(),
                    duration=f"{int(metadata.duration // 60):02d}:{int(metadata.duration % 60):02d}"
                )

        # ===== PHASE 5: AI VIDEO PROMPTS =====
        if 5 not in skip_phases:
            ai_prompts = generate_ai_video_prompts(
                script=replication_script,
                analysis=analysis,
                product_name=args.product_name
            )

            prompts_path = output_dir / "ai_video_prompts.md"
            ai_prompts.save_to_file(prompts_path)
            logger.success(f"AI video prompts saved: {prompts_path}")
            status.mark_phase_complete(5)
        else:
            logger.info("⏭️  PHASE 5 SKIPPED")

        # ===== COMPLETION =====
        status.save_to_file(output_dir / "processing_status.json")

        logger.info("=" * 70)
        logger.success("✅ ALL PHASES COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Output directory: {output_dir}")
        logger.info("Generated files:")
        logger.info(f"  - metadata.json")
        logger.info(f"  - video.mp4")
        logger.info(f"  - frames/ ({frame_count} frames)")
        logger.info(f"  - transcript.json")
        logger.info(f"  - analysis.md (includes character descriptions)")
        logger.info(f"  - replication_script.md")
        logger.info(f"  - ai_video_prompts.md")
        logger.info(f"  - processing_status.json")
        logger.info(f"  - analysis.log")
        logger.info("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"❌ ANALYSIS FAILED: {e}")
        status.error_message = str(e)
        status.save_to_file(output_dir / "processing_status.json")
        logger.exception(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
