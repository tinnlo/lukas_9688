#!/usr/bin/env python3
"""
Adaptive Audio Trimmer - Social Media Edition

Automatically removes long pauses in voiceover recordings while preserving
natural speech rhythm. Perfect for creating punchy TikTok/Instagram content.

Features:
- Auto-detects silence threshold based on recording environment
- Removes silences > 0.33s, replaces with tight 0.1s gaps
- Filters out mouth clicks and breaths (< 200ms segments)
- Preserves original audio quality
- Batch processing support

Usage Examples:
  # Basic usage (auto-detect threshold)
  python3 audio_trimmer.py "voiceover.mp3"

  # Manual threshold for noisy outdoor recording
  python3 audio_trimmer.py "outdoor.mp3" --threshold -35

  # Custom gap duration
  python3 audio_trimmer.py "speech.mp3" --gap 0.15

  # Batch process entire directory
  python3 audio_trimmer.py "/path/to/audio_files/" --recursive

  # Verbose mode to see all segments
  python3 audio_trimmer.py "file.mp3" -v

Author: Created for TikTok content workflow
License: MIT
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import math


def check_ffmpeg_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if ffmpeg is installed and accessible.

    Returns:
        Tuple of (is_installed, path_or_error_message)
    """
    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path:
        return True, ffmpeg_path

    error_msg = """
╔════════════════════════════════════════════════════════════════╗
║                    ffmpeg NOT FOUND                            ║
╚════════════════════════════════════════════════════════════════╝

This script requires ffmpeg to process audio files.

Installation instructions:
  
  macOS (Homebrew):
    brew install ffmpeg
  
  Linux (Ubuntu/Debian):
    sudo apt-get install ffmpeg
  
  Linux (Fedora):
    sudo dnf install ffmpeg
  
  Windows (Chocolatey):
    choco install ffmpeg

After installation, restart your terminal and try again.
"""
    return False, error_msg


def check_dependencies():
    """Check all required dependencies and provide helpful error messages."""
    # Check ffmpeg first
    ffmpeg_ok, ffmpeg_info = check_ffmpeg_installed()

    if not ffmpeg_ok:
        print(ffmpeg_info, file=sys.stderr)
        sys.exit(1)

    # Check pydub
    try:
        import pydub
    except ImportError:
        print(
            """
╔════════════════════════════════════════════════════════════════╗
║                    pydub NOT INSTALLED                         ║
╚════════════════════════════════════════════════════════════════╝

Please install the required Python package:

  pip3 install pydub

Or install all requirements:

  pip3 install -r scripts/requirements.txt
""",
            file=sys.stderr,
        )
        sys.exit(1)

    return ffmpeg_info


def auto_detect_threshold(
    audio_segment, sample_duration_ms: int = 500, verbose: bool = False
) -> float:
    """
    Analyze audio to determine optimal silence threshold.

    Examines the first 500ms to detect ambient noise floor and sets
    threshold 12dB above it. Clamps to reasonable bounds for natural pacing.

    Args:
        audio_segment: pydub AudioSegment to analyze
        sample_duration_ms: Duration of sample to analyze (default: 500ms)
        verbose: Print detection details

    Returns:
        Silence threshold in dBFS (typically -50 to -45)
    """
    from pydub import AudioSegment

    # Take sample from beginning
    sample = audio_segment[:sample_duration_ms]

    # Calculate RMS (root mean square) amplitude
    rms = sample.rms

    if rms == 0:
        # Completely silent sample, use conservative default
        if verbose:
            print("  ⚠ Sample appears silent, using default threshold -45dB")
        return -45.0

    # Convert to dBFS (decibels relative to full scale)
    max_amplitude = audio_segment.max_possible_amplitude
    rms_db = 20 * math.log10(rms / max_amplitude)

    # Add 12dB margin above noise floor (more conservative = less aggressive trimming)
    threshold = rms_db + 12

    # Clamp to reasonable bounds for natural speech rhythm
    # -50dB: very quiet studio recordings
    # -40dB: normal indoor/moderate outdoor (adaptive range)
    # Note: For very noisy outdoor (cafe/street), use manual --threshold -35 or -30
    threshold = max(-50, min(-40, threshold))

    if verbose:
        # Provide context about detected environment
        if threshold <= -48:
            environment = "studio/very quiet"
        elif threshold <= -44:
            environment = "quiet indoor"
        elif threshold <= -40:
            environment = "normal/moderate noise"
        else:
            environment = "adaptive"
        print(
            f"  Noise floor: {rms_db:.1f}dB → Threshold: {threshold:.1f}dB ({environment})"
        )

    return threshold


def get_audio_format(file_path: str) -> str:
    """Detect audio format from file extension."""
    ext = Path(file_path).suffix.lower()

    format_map = {
        ".mp3": "mp3",
        ".wav": "wav",
        ".m4a": "m4a",
        ".aac": "aac",
        ".ogg": "ogg",
        ".flac": "flac",
    }

    return format_map.get(ext, "mp3")


def get_audio_bitrate(file_path: str) -> str:
    """
    Extract bitrate from audio file.

    Returns:
        Bitrate string like "192k" or "128k"
    """
    import subprocess

    try:
        # Use ffprobe to get bitrate
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=bit_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            bitrate_bps = int(result.stdout.strip())
            bitrate_kbps = bitrate_bps // 1000
            return f"{bitrate_kbps}k"
    except Exception:
        pass

    # Default fallback
    return "192k"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def generate_output_path(input_path: str, suffix: str = "_trimmed") -> str:
    """Generate output file path with suffix before extension."""
    path = Path(input_path)
    output_name = f"{path.stem}{suffix}{path.suffix}"
    return str(path.parent / output_name)


def process_single_file(
    input_path: str,
    threshold: Optional[float] = None,
    min_silence: float = 0.33,
    gap: float = 0.1,
    min_segment: float = 0.2,
    output_suffix: str = "_trimmed",
    verbose: bool = False,
    quiet: bool = False,
) -> Dict:
    """
    Process a single audio file to remove long silences.

    Args:
        input_path: Path to input audio file
        threshold: Manual silence threshold in dB (None = auto-detect)
        min_silence: Minimum silence duration to detect (seconds)
        gap: Replacement gap duration (seconds)
        min_segment: Minimum speech segment to keep (seconds)
        output_suffix: Suffix for output filename
        verbose: Show detailed progress
        quiet: Suppress all output except errors

    Returns:
        Dictionary with processing results
    """
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent

    # Validate input file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not os.path.isfile(input_path):
        raise ValueError(f"Input path is not a file: {input_path}")

    # Detect format
    audio_format = get_audio_format(input_path)

    if not quiet:
        print(f"\nProcessing: {Path(input_path).name}")

    # Load audio file
    if verbose:
        print(f"  Loading {audio_format.upper()} file...")

    try:
        if audio_format == "mp3":
            audio = AudioSegment.from_mp3(input_path)
        elif audio_format == "wav":
            audio = AudioSegment.from_wav(input_path)
        else:
            audio = AudioSegment.from_file(input_path, format=audio_format)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file: {e}")

    original_duration = len(audio) / 1000.0  # Convert to seconds

    # Get original quality parameters
    original_bitrate = get_audio_bitrate(input_path)

    # Determine silence threshold
    if threshold is not None:
        silence_threshold = threshold
        if verbose:
            print(f"  Using manual threshold: {silence_threshold:.1f}dB")
    else:
        if verbose:
            print(f"  Analyzing noise floor from first 500ms...")
        silence_threshold = auto_detect_threshold(audio, verbose=verbose)
        if not quiet and not verbose:
            print(f"  Auto-detected silence threshold: {silence_threshold:.1f}dB")

    # Detect non-silent segments
    if verbose:
        print(
            f"  Detecting speech segments (min_silence={int(min_silence * 1000)}ms, threshold={silence_threshold:.1f}dB)..."
        )

    min_silence_ms = int(min_silence * 1000)

    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_ms,
        silence_thresh=silence_threshold,
        seek_step=10,  # 10ms precision
    )

    if verbose:
        print(f"  Found {len(nonsilent_ranges)} non-silent segments")

    # Filter out very short segments (likely mouth clicks, breaths, etc.)
    if verbose:
        print(f"  Filtering segments < {int(min_segment * 1000)}ms...")

    min_segment_ms = int(min_segment * 1000)
    filtered_count = 0
    valid_ranges = []

    for start, end in nonsilent_ranges:
        duration = end - start
        if duration >= min_segment_ms:
            valid_ranges.append((start, end))
        else:
            filtered_count += 1
            if verbose:
                print(
                    f"    Segment at {start / 1000:.2f}s: {duration}ms (filtered - too short)"
                )

    if verbose:
        print(f"  Kept {len(valid_ranges)} valid speech segments")
    elif not quiet:
        print(
            f"  Found {len(valid_ranges)} speech segments, filtered {filtered_count} short segments"
        )

    if len(valid_ranges) == 0:
        raise RuntimeError(
            "No valid speech segments found. Audio may be too quiet or completely silent."
        )

    # Rebuild audio with consistent gaps
    if verbose:
        print(f"  Rebuilding audio with {int(gap * 1000)}ms gaps...")

    output = AudioSegment.empty()
    gap_segment = AudioSegment.silent(duration=int(gap * 1000))

    for i, (start, end) in enumerate(valid_ranges):
        # Add speech segment
        output += audio[start:end]

        # Add gap between segments (but not after the last one)
        if i < len(valid_ranges) - 1:
            output += gap_segment

    trimmed_duration = len(output) / 1000.0
    time_saved = original_duration - trimmed_duration
    percent_saved = (
        (time_saved / original_duration * 100) if original_duration > 0 else 0
    )

    if not quiet:
        print(
            f"  Duration: {format_duration(original_duration)} → {format_duration(trimmed_duration)} (saved {format_duration(time_saved)}, {percent_saved:.1f}%)"
        )

    # Export with original quality
    output_path = generate_output_path(input_path, output_suffix)

    if verbose:
        print(f"  Exporting with original quality ({original_bitrate})...")

    try:
        if audio_format == "mp3":
            output.export(output_path, format="mp3", bitrate=original_bitrate)
        elif audio_format == "wav":
            output.export(output_path, format="wav")
        else:
            output.export(output_path, format=audio_format, bitrate=original_bitrate)
    except Exception as e:
        raise RuntimeError(f"Failed to export audio: {e}")

    if not quiet:
        print(f"  ✓ Saved: {Path(output_path).name}")

    return {
        "success": True,
        "input_path": input_path,
        "output_path": output_path,
        "original_duration": original_duration,
        "trimmed_duration": trimmed_duration,
        "time_saved": time_saved,
        "percent_saved": percent_saved,
        "segments_kept": len(valid_ranges),
        "segments_filtered": filtered_count,
        "threshold_used": silence_threshold,
    }


def process_batch(
    input_dir: str, recursive: bool = False, output_suffix: str = "_trimmed", **kwargs
) -> Dict:
    """
    Process all audio files in a directory.

    Args:
        input_dir: Directory containing audio files
        recursive: Process subdirectories recursively
        output_suffix: Suffix for output files
        **kwargs: Additional arguments passed to process_single_file

    Returns:
        Dictionary with batch processing results
    """
    verbose = kwargs.get("verbose", False)
    quiet = kwargs.get("quiet", False)

    # Find all audio files
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")

    if not input_path.is_dir():
        raise ValueError(f"Path is not a directory: {input_dir}")

    # Supported audio extensions
    audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}

    # Find audio files
    if recursive:
        audio_files = [
            f
            for f in input_path.rglob("*")
            if f.is_file()
            and f.suffix.lower() in audio_extensions
            and not f.stem.endswith(output_suffix)  # Skip already processed files
        ]
    else:
        audio_files = [
            f
            for f in input_path.glob("*")
            if f.is_file()
            and f.suffix.lower() in audio_extensions
            and not f.stem.endswith(output_suffix)
        ]

    if not audio_files:
        print(f"No audio files found in {input_dir}", file=sys.stderr)
        return {
            "success": True,
            "total_files": 0,
            "processed": 0,
            "errors": 0,
            "total_time_saved": 0,
        }

    if not quiet:
        print(f"\nProcessing directory: {input_dir}")
        print(f"Found {len(audio_files)} audio files")

    # Process each file
    results = []
    errors = []
    total_time_saved = 0

    for i, audio_file in enumerate(audio_files, 1):
        try:
            if not quiet and not verbose:
                print(f"\n[{i}/{len(audio_files)}] ", end="")

            result = process_single_file(
                str(audio_file), output_suffix=output_suffix, **kwargs
            )

            results.append(result)
            total_time_saved += result["time_saved"]

            if not quiet and not verbose:
                print(f"  ✓")

        except Exception as e:
            error_msg = f"Error processing {audio_file.name}: {e}"
            errors.append(error_msg)

            if not quiet:
                print(f"  ✗ {error_msg}", file=sys.stderr)

    # Print summary
    if not quiet:
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"  Processed: {len(results)}/{len(audio_files)} files")
        print(f"  Total time saved: {format_duration(total_time_saved)}")
        if errors:
            print(f"  Errors: {len(errors)}")
            for error in errors:
                print(f"    - {error}")

    return {
        "success": True,
        "total_files": len(audio_files),
        "processed": len(results),
        "errors": len(errors),
        "total_time_saved": total_time_saved,
        "results": results,
        "error_messages": errors,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Adaptive Audio Trimmer for Social Media - Remove long silences while preserving speech rhythm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (auto-detect threshold)
  %(prog)s "voiceover.mp3"
  
  # Manual threshold for noisy outdoor recording
  %(prog)s "outdoor.mp3" --threshold -35
  
  # Custom gap duration
  %(prog)s "speech.mp3" --gap 0.15
  
  # Batch process directory
  %(prog)s "/path/to/audio_files/" --recursive
  
  # Verbose mode
  %(prog)s "file.mp3" -v
""",
    )

    # Positional arguments
    parser.add_argument("input_path", help="Path to audio file or directory")

    # Silence detection
    parser.add_argument(
        "--threshold",
        type=float,
        metavar="DB",
        help="Manual silence threshold in dB, e.g., -40 (default: auto-detect)",
    )

    parser.add_argument(
        "--min-silence",
        type=float,
        default=0.33,
        metavar="SEC",
        help="Minimum silence duration to remove in seconds (default: 0.33)",
    )

    # Output control
    parser.add_argument(
        "--gap",
        type=float,
        default=0.1,
        metavar="SEC",
        help="Replacement gap duration in seconds (default: 0.1)",
    )

    parser.add_argument(
        "--min-segment",
        type=float,
        default=0.2,
        metavar="SEC",
        help="Minimum speech segment to keep in seconds (default: 0.2)",
    )

    parser.add_argument(
        "--output-suffix",
        default="_trimmed",
        help="Output filename suffix (default: _trimmed)",
    )

    # Batch processing
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively (batch mode only)",
    )

    # Output modes
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output (show all segments)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode (errors only)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.threshold is not None and (args.threshold > 0 or args.threshold < -60):
        parser.error("Threshold must be between -60 and 0 dB")

    if args.gap <= 0:
        parser.error("Gap duration must be positive")

    if args.min_silence <= 0:
        parser.error("Minimum silence duration must be positive")

    if args.min_segment < 0:
        parser.error("Minimum segment duration cannot be negative")

    if args.verbose and args.quiet:
        parser.error("Cannot use --verbose and --quiet together")

    # Check dependencies
    if not args.quiet:
        print("Checking dependencies...")
        ffmpeg_path = check_dependencies()
        print(f"  ✓ ffmpeg found at {ffmpeg_path}")
        print(f"  ✓ pydub installed")
    else:
        check_dependencies()

    # Determine if input is file or directory
    input_path = Path(args.input_path)

    try:
        if input_path.is_file():
            # Process single file
            result = process_single_file(
                str(input_path),
                threshold=args.threshold,
                min_silence=args.min_silence,
                gap=args.gap,
                min_segment=args.min_segment,
                output_suffix=args.output_suffix,
                verbose=args.verbose,
                quiet=args.quiet,
            )

            if not args.quiet:
                print("\n✓ Processing complete!")

            sys.exit(0)

        elif input_path.is_dir():
            # Process batch
            result = process_batch(
                str(input_path),
                recursive=args.recursive,
                threshold=args.threshold,
                min_silence=args.min_silence,
                gap=args.gap,
                min_segment=args.min_segment,
                output_suffix=args.output_suffix,
                verbose=args.verbose,
                quiet=args.quiet,
            )

            if not args.quiet:
                print("\n✓ Batch processing complete!")

            # Exit with error code if there were errors
            if result["errors"] > 0:
                sys.exit(1)
            else:
                sys.exit(0)
        else:
            print(f"Error: Path does not exist: {args.input_path}", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
