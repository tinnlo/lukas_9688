# Audio Trimmer - Social Media Edition

Automatically removes long pauses in voiceover recordings while preserving natural speech rhythm. Perfect for creating punchy TikTok/Instagram/YouTube Shorts content.

## Features

✅ **Adaptive Silence Detection** - Auto-detects silence threshold based on recording environment (indoor/outdoor)  
✅ **Configurable Gap Removal** - Removes silences > 0.33s, replaces with tight 0.1s gaps  
✅ **Smart Filtering** - Removes mouth clicks and breaths (< 200ms segments)  
✅ **Quality Preservation** - Maintains original audio bitrate and quality  
✅ **Batch Processing** - Process entire directories at once  
✅ **Multiple Formats** - Supports MP3, WAV, M4A, AAC, OGG, FLAC  

## Quick Start

### Installation

```bash
# Install required Python library
pip3 install pydub

# Or install all project requirements
pip3 install -r scripts/requirements.txt
```

**System Requirement**: ffmpeg must be installed
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### Basic Usage

```bash
# Process single file (auto-detect silence threshold)
python3 scripts/audio_trimmer.py "path/to/voiceover.mp3"

# Process with verbose output to see details
python3 scripts/audio_trimmer.py "path/to/voiceover.mp3" -v
```

## Usage Examples

### Single File Processing

```bash
# Basic - auto-detect everything
python3 scripts/audio_trimmer.py "voiceover.mp3"

# Manual threshold for noisy outdoor recording
python3 scripts/audio_trimmer.py "outdoor.mp3" --threshold -35

# Custom gap duration (150ms instead of default 100ms)
python3 scripts/audio_trimmer.py "speech.mp3" --gap 0.15

# Keep longer pauses (only remove silences > 0.5s)
python3 scripts/audio_trimmer.py "interview.mp3" --min-silence 0.5

# Verbose mode - see all detected segments
python3 scripts/audio_trimmer.py "file.mp3" -v
```

### Batch Processing

```bash
# Process all audio files in a directory
python3 scripts/audio_trimmer.py "/path/to/audio_folder/"

# Process directory and all subdirectories
python3 scripts/audio_trimmer.py "/path/to/audio_folder/" --recursive

# Batch with custom settings
python3 scripts/audio_trimmer.py "/path/to/folder/" --threshold -40 --gap 0.12
```

### Custom Output

```bash
# Custom output suffix
python3 scripts/audio_trimmer.py "voice.mp3" --output-suffix "_fast"
# Creates: voice_fast.mp3

# Quiet mode (only show errors)
python3 scripts/audio_trimmer.py "voice.mp3" -q
```

## How It Works

### Adaptive Threshold Detection

The script analyzes the first 500ms of your audio to detect the ambient noise floor:

1. Calculates RMS (Root Mean Square) amplitude
2. Converts to dBFS (decibels relative to full scale)
3. Sets threshold 12dB above noise floor (conservative for natural pacing)
4. Clamps between -50dB (quiet studio) and -40dB (moderate outdoor) for adaptive natural speech
5. For very noisy environments (cafe/street), use manual `--threshold -35` or `-30`

### Processing Pipeline

```
Input Audio
    ↓
Auto-detect silence threshold (or use manual)
    ↓
Detect all speech segments (non-silent regions)
    ↓
Filter out very short segments (< 200ms - likely mouth clicks/breaths)
    ↓
Rebuild audio: [Speech 1] + [0.1s gap] + [Speech 2] + [0.1s gap] + ...
    ↓
Export with original quality
```

## Command-Line Options

### Required
- `input_path` - Path to audio file or directory

### Silence Detection
- `--threshold DB` - Manual silence threshold in dB, e.g., -40 (default: auto-detect)
- `--min-silence SEC` - Minimum silence duration to remove (default: 0.33s)

### Output Control
- `--gap SEC` - Replacement gap duration (default: 0.1s)
- `--min-segment SEC` - Minimum speech segment to keep (default: 0.2s)
- `--output-suffix SUFFIX` - Output filename suffix (default: _trimmed)

### Batch Processing
- `--recursive` - Process subdirectories recursively

### Output Modes
- `-v, --verbose` - Show all segments and detailed progress
- `-q, --quiet` - Only show errors

## Output Examples

### Normal Mode (Default)

```
Checking dependencies...
  ✓ ffmpeg found at /usr/local/bin/ffmpeg
  ✓ pydub installed

Processing: voiceover.mp3
  Auto-detected silence threshold: -42.3dB
  Found 20 speech segments, filtered 1 short segments
  Duration: 45.6s → 34.2s (saved 11.4s, 24.9%)
  ✓ Saved: voiceover_trimmed.mp3

✓ Processing complete!
```

### Verbose Mode

```
Processing: voiceover.mp3
  Loading MP3 file...
  Analyzing noise floor from first 500ms...
  Noise floor: -48.7dB → Threshold: -42.7dB
  Detecting speech segments (min_silence=330ms, threshold=-42.7dB)...
  Found 21 non-silent segments
  Filtering segments < 200ms...
    Segment at 21.96s: 120ms (filtered - too short)
  Kept 20 valid speech segments
  Rebuilding audio with 100ms gaps...
  Duration: 45.6s → 34.2s (saved 11.4s, 24.9%)
  Exporting with original quality (130k)...
  ✓ Saved: voiceover_trimmed.mp3
```

### Batch Mode

```
Processing directory: /Users/me/audio_files/
Found 15 MP3 files

[1/15] file1.mp3
  Found 18 speech segments, filtered 2 short segments
  Duration: 42.3s → 36.1s (saved 6.2s, 14.7%)
  ✓ Saved: file1_trimmed.mp3
  ✓

[2/15] file2.mp3
  Found 23 speech segments, filtered 1 short segments
  Duration: 51.2s → 41.8s (saved 9.4s, 18.4%)
  ✓ Saved: file2_trimmed.mp3
  ✓

...

======================================================================
SUMMARY
======================================================================
  Processed: 14/15 files
  Total time saved: 127.3s
  Errors: 1
    - Error processing corrupted.mp3: Failed to load audio file
```

## Tips & Best Practices

### When to Use Auto-Detect vs Manual Threshold

**Use Auto-Detect (default)** when:
- Recording in consistent environments
- Normal voice recordings with clear speech
- You're not sure what threshold to use

**Use Manual Threshold** when:
- Auto-detect is too aggressive/conservative
- Recording in very noisy environments (use -35 to -30)
- Very quiet studio recordings (use -50 to -45)
- You want consistent behavior across multiple files

### Recommended Settings by Use Case

**TikTok/Instagram Reels** (tight, punchy):
```bash
python3 scripts/audio_trimmer.py "voice.mp3" --gap 0.1 --min-silence 0.33
```

**YouTube Shorts** (slightly more natural):
```bash
python3 scripts/audio_trimmer.py "voice.mp3" --gap 0.15 --min-silence 0.4
```

**Interview/Podcast** (preserve natural rhythm):
```bash
python3 scripts/audio_trimmer.py "interview.mp3" --gap 0.2 --min-silence 0.5
```

**Outdoor/Noisy Recording**:
```bash
python3 scripts/audio_trimmer.py "outdoor.mp3" --threshold -35 --min-segment 0.3
```

### Threshold Guidelines

| Environment | Suggested Threshold |
|-------------|---------------------|
| Professional studio | -50 to -48 dB |
| Quiet home office | -48 to -45 dB (auto-detect default) |
| Normal room | -45 to -40 dB |
| Noisy cafe/outdoor | -40 to -35 dB |

## Troubleshooting

### "ffmpeg NOT FOUND" Error

**Problem**: ffmpeg is not installed or not in PATH

**Solution**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# After installation, verify
ffmpeg -version
```

### "pydub NOT INSTALLED" Error

**Problem**: pydub Python library is missing

**Solution**:
```bash
pip3 install pydub
```

### "No valid speech segments found" Error

**Problem**: Audio is too quiet or silence threshold is too strict

**Solutions**:
1. Try lowering the threshold manually: `--threshold -50`
2. Decrease min-silence duration: `--min-silence 0.2`
3. Check audio isn't corrupted: play it in a media player
4. Use verbose mode to see detection details: `-v`

### Output sounds choppy or cuts off words

**Problem**: Threshold is too high (not sensitive enough)

**Solutions**:
1. Lower the threshold: `--threshold -45` (more negative = more sensitive)
2. Increase gap duration: `--gap 0.15`
3. Use verbose mode to see where cuts are happening

### Too much silence remains

**Problem**: Threshold is too low (too sensitive)

**Solutions**:
1. Raise the threshold: `--threshold -35` (less negative = less sensitive)
2. Decrease min-silence: `--min-silence 0.25`

## Technical Details

### Dependencies
- **pydub** (>=0.25.1) - Audio processing library
- **ffmpeg** - Audio codec backend (system dependency)
- **Python 3.8+** - Runtime environment

### Supported Audio Formats
- MP3 (MPEG Audio Layer III)
- WAV (Waveform Audio File Format)
- M4A (MPEG-4 Audio)
- AAC (Advanced Audio Coding)
- OGG (Ogg Vorbis)
- FLAC (Free Lossless Audio Codec)

### Audio Quality Preservation
- Bitrate: Automatically detected and preserved from input
- Sample Rate: Preserved from input (typically 44.1kHz or 48kHz)
- Channels: Preserved (mono/stereo)
- Format: Same as input

### Performance
- Processing speed: ~10-20x real-time (depends on CPU)
- Memory usage: ~2-3x file size (loads entire file into RAM)
- Disk space: Requires space for both original and trimmed files

## Integration with TikTok Workflow

This script is designed to work seamlessly with the TikTok content workflow:

```bash
# 1. Generate voiceover with ElevenLabs or other TTS
# 2. Trim the audio for social media
python3 scripts/audio_trimmer.py "product_list/20260211/123456/voiceover.mp3" -v

# 3. Use trimmed audio in video editing
# Output: product_list/20260211/123456/voiceover_trimmed.mp3
```

### Batch Processing After Script Generation

```bash
# Process all voiceovers in a product batch
python3 scripts/audio_trimmer.py "product_list/20260211/" --recursive
```

## File Naming

Input: `my_voiceover.mp3`  
Output: `my_voiceover_trimmed.mp3` (default)

Custom suffix:
```bash
python3 scripts/audio_trimmer.py "voice.mp3" --output-suffix "_social"
# Output: voice_social.mp3
```

## Safety

✅ **Original files are NEVER modified**  
✅ Creates new files with `_trimmed` suffix (configurable)  
✅ In batch mode, skips files already ending with `_trimmed.mp3`  
✅ Graceful error handling - one bad file won't stop batch processing  

## License

MIT License - Free to use and modify

## Author

Created for TikTok short-form video content workflow

---

**Version**: 1.0.0  
**Last Updated**: February 2026
