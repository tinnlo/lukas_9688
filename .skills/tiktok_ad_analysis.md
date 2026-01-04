---
name: tiktok-ad-analysis
description: AUTOMATIC video market analysis with hybrid transcription (TikTok captions → Whisper fallback). Auto-triggers when videos exist in ref_video/. Analyzes TikTok reference videos to extract hooks, strategies, and insights for script generation.
version: 4.2.0
author: Automated script (Python-based)
execution: Python script with FFmpeg + yt-dlp + Whisper + Gemini (AUTO-RUNS conditionally)
orchestration: tiktok_product_analysis.md (for batch parallelism)
---

# TikTok Ad Analysis Skill (AUTOMATIC)

**WHAT THIS DOES:** Automatically analyzes TikTok reference videos with bilingual output (English + Chinese)
**WHEN IT RUNS:** AUTO-TRIGGERS after Step 1 (scraping) if `ref_video/` folder contains .mp4 files
**HOW IT WORKS:** Python script extracts frames + transcribes audio → Gemini generates analysis
**OUTPUT:** `video_N_analysis.md` for each video + `video_synthesis.md` summary (MANDATORY)

---

## Integration with Skill Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  SKILL PIPELINE                                             │
│                                                             │
│  1. tiktok_product_scraper.md → Downloads products + videos │
│                     │                                       │
│                     ▼                                       │
│  2. THIS SKILL (tiktok_ad_analysis.md)                      │
│     - Python scripts for frame extraction + transcription   │
│     - Gemini for per-video analysis                         │
│     - Output: video_N_analysis.md files                     │
│                     │                                       │
│                     ▼                                       │
│  3. tiktok_product_analysis.md (ORCHESTRATION)              │
│     - Parallel batch processing across products             │
│     - Image analysis (Gemini async MCP)                     │
│     - Video synthesis generation (Gemini async MCP)         │
│     - Output: video_synthesis.md, image_analysis.md         │
│                     │                                       │
│                     ▼                                       │
│  4. tiktok_script_generator.md                              │
│     - Script writing (Claude Code)                          │
│     - Campaign Summary (references analysis files)          │
│     - Output: Script_1/2/3.md, Campaign_Summary.md          │
└─────────────────────────────────────────────────────────────┘
```

**Agent Assignment:**
| Task | Agent | Tool |
|:-----|:------|:-----|
| Video frame extraction | Python (FFmpeg) | Local script |
| Audio transcription | Python (Whisper) | Local script |
| Per-video analysis | Gemini | gemini_cli_execute |
| Batch orchestration | Gemini | gemini_cli_execute_async |
| Video synthesis | Gemini | gemini_cli_execute_async |
| Script writing | Claude Code | Direct writing |

---

## Auto-Trigger Logic

**⚠️ CRITICAL:** This skill AUTO-RUNS conditionally. No manual invocation needed in normal workflow.

**Trigger Conditions:**
```bash
# After Step 1 (product scraping) completes:
if [ -d "product_list/{product_id}/ref_video" ]; then
  video_count=$(find "product_list/{product_id}/ref_video" -type f -name "*.mp4" 2>/dev/null | wc -l)
  if [ $video_count -gt 0 ]; then
    echo "✅ AUTO-TRIGGER: Found $video_count videos"
    # Automatically run video analysis
    python analyze_video_batch.py {product_id}
  else
    echo "⏭️ SKIP: No videos found"
  fi
else
  echo "⏭️ SKIP: No ref_video folder"
fi
```

**Manual Execution (if needed):**

```bash
# Navigate to scripts directory
cd scripts

# Activate virtual environment
source venv/bin/activate

# Analyze all videos for a product
python analyze_video_batch.py 1729479916562717270

# Or analyze a single video
python analyze_single_video.py 1729479916562717270 2
```

**Output:**
- `product_list/{product_id}/ref_video/video_N_analysis.md` (bilingual, per video)
- `product_list/{product_id}/ref_video/video_synthesis.md` (MANDATORY market summary)

---

## Prerequisites

✅ **Python 3.8+** with virtual environment
✅ **ffmpeg** installed (for keyframe/audio extraction)
✅ **faster-whisper** installed (`pip install faster-whisper`)
✅ **yt-dlp** installed (`pip install yt-dlp`)
✅ **gemini-cli** installed and configured
✅ **Local video files** in `product_list/{product_id}/ref_video/`
✅ **tabcut_data.json** available (contains performance metadata)

---

## Transcription Workflow (Hybrid Approach)

```
┌─────────────────────────────┐
│  1. TikTok Captions         │ ← Fastest (yt-dlp)
│     (direct download)        │
└──────────┬──────────────────┘
           │ Not available?
           ▼
┌─────────────────────────────┐
│  2. Whisper AI              │ ← Fallback (reliable)
│     (faster-whisper)         │
└──────────┬──────────────────┘
           │ Failed?
           ▼
┌─────────────────────────────┐
│  3. No transcript           │ ← Music/silent
│     (mark as unavailable)    │
└─────────────────────────────┘
```

**Benefits:**
- **Speed:** TikTok captions are instant when available
- **Accuracy:** Whisper handles videos without captions
- **Coverage:** Graceful fallback for music-only content

---

## Script Files

### `analyze_video_batch.py` - Batch Processing

**Usage:**
```bash
python analyze_video_batch.py <product_id>
```

**What it does:**
1. For each video in `ref_video/`:
   - FFmpeg extracts keyframes (every 3 seconds) + audio
   - Tries TikTok captions via yt-dlp (fast)
   - Falls back to Whisper transcription if needed
   - Passes frames + transcript to Gemini
   - Writes `video_N_analysis.md`

2. After all videos: Creates `video_synthesis.md` (market-level insights)

**Output files:**
```
product_list/{product_id}/ref_video/
├── video_1_analysis.md    # Individual analysis (bilingual)
├── video_2_analysis.md
├── video_3_analysis.md
├── video_4_analysis.md
├── video_5_analysis.md
└── video_synthesis.md     # Market summary (all videos)
```

### `analyze_single_video.py` - Single Video

**Usage:**
```bash
python analyze_single_video.py <product_id> <video_number>
```

**Example:**
```bash
python analyze_single_video.py 1729479916562717270 2
```

**What it does:** Same workflow as batch, but for a single video

---

## Analysis Output Format

Each `video_N_analysis.md` contains:

### 1. Video Metadata | 视频元数据
- Creator, followers, rank, sales, views, duration

### 2. Voiceover/Dialogue Transcript | 旁白/对话文本
- **Language Detected:** German/English/Russian/etc.
- **Original Transcript:** With timestamps [MM:SS]
- **中文翻译:** Chinese translation line by line

### 3. Hook/Opening Strategy | 开场策略
- Hook Type (Problem-Solution, Pricing-FOMO, etc.)
- Hook Description
- Visual + Audio Combination
- Effectiveness Rating

### 4. Shot-by-Shot Storyboard | 分镜脚本
- Frame-by-frame analysis
- Visual action descriptions
- Voiceover alignment
- Shot purpose (Hook, Product Reveal, CTA, etc.)

### 5. Visual Elements Catalog | 视觉元素目录
- Graphics/Text Overlays
- Product Showcase
- Transitions
- Color Grading
- Lighting

### 6. Music/Audio Analysis | 音乐/音频分析
- Genre, Mood, Audio Quality
- Voice type (Human/TTS)
- Sync analysis

### 7. Key Selling Points | 核心卖点
- Feature emphasis with time allocation

### 8. Creative Strategy & Execution | 创意策略与执行
- Production Style (UGC/Professional)
- Germany Market Fit
- Authenticity Level
- Viral Elements

### 9. Call-to-Action Analysis | 行动号召分析
- CTA Type, Timing, Strength Rating

### 10. Target Audience Inference | 目标受众推断
- Demographics, Psychographics, Language Signals

### 11. Effectiveness Rating (7-Dimension) | 有效性评分
- Hook Strength, Pacing, Visual Quality, Trust Signals
- Value Clarity, CTA Effectiveness, Overall Score

### 12. Replication Insights | 复制要点
- Production Budget
- Equipment Needed
- Key Success Factor
- Reproduducible Elements

### 13. Recommendations (DO/DON'T/OPPORTUNITY) | 建议
- Specific actionable recommendations
- Mistakes to avoid
- Untapped opportunities

---

## Language Support

**Transcription supports:**
- German (de) - Primary market
- English (en)
- Russian (ru) - Diaspora targeting
- Spanish (es), French (fr), Japanese (ja), Korean (ko), Portuguese (pt)
- Chinese Simplified (zh-Hans), Chinese Traditional (zh-Hant)

**Auto-detection:** Both yt-dlp captions and Whisper auto-detect language

---

## Performance Notes

| Method | Speed | Accuracy | When Used |
|:-------|:------|:---------|:----------|
| TikTok captions (yt-dlp) | ~2-5s | High (creator's own) | When creator adds captions |
| Whisper transcription | ~30-60s | Very High | When no captions available |
| No transcript | Instant | N/A | Music-only or unintelligible |

**Typical batch time (5 videos):**
- All have TikTok captions: ~30 seconds
- All need Whisper: ~4-5 minutes
- Mixed: ~1-2 minutes

---

## Error Handling

### No TikTok captions available
```
  ├─ Fetching captions from TikTok (yt-dlp)...
  ├─ No captions found on TikTok
  ├─ Falling back to Whisper transcription...
```

### Whisper transcription succeeds
```
  ├─ Transcribing audio with faster-whisper...
  ├─ Detected language: de (confidence: 1.00)
  ├─ Transcript length: 9 segments
  └─ Transcript: whisper_transcription - de with 9 segments
```

### Both methods fail
```
  ├─ No transcript available - marking as music/silent
  └─ Transcript: none - unknown with 0 segments
```

---

## Installation

```bash
# Create virtual environment
cd scripts
python3 -m venv venv

# Activate
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install faster-whisper yt-dlp

# Verify ffmpeg is installed
ffmpeg -version

# Verify yt-dlp works
yt-dlp --version

# Test Whisper
python -c "from faster_whisper import WhisperModel; print('OK')"
```

---

## Configuration

### Whisper Model Options

Edit `analyze_single_video.py` or `analyze_video_batch.py`:

```python
# Current (fast, good accuracy)
model = WhisperModel("base", device="cpu", compute_type="int8")

# For better accuracy (slower)
model = WhisperModel("small", device="cpu", compute_type="int8")

# For best accuracy (slowest)
model = WhisperModel("medium", device="cpu", compute_type="int8")
```

### yt-dlp Language Priority

Current priority order:
```python
"--sub-lang", "en,de,ru,es,fr,ja,ko,pt,zh-Hans,zh-Hant"
```

Add/remove languages as needed for your market.

---

## Troubleshooting

### Issue: yt-dlp can't access TikTok

**Error:** `HTTP Error 429: Too Many Requests`

**Solution:** TikTok rate limiting - wait a few minutes and retry, or rely on Whisper fallback

### Issue: Whisper slow transcription

**Solution:** Use smaller model (`base` instead of `small`/`medium`)

### Issue: Gemini quota exhausted

**Error:** `API Error: You have exhausted your capacity`

**Solution:** Wait for quota reset (~4-6 hours) or switch Google account

### Issue: No audio in transcript

**Check:**
```bash
# Verify audio file was extracted
ls -lh product_list/{product_id}/ref_video/video_N_analysis_temp/audio.mp3

# Play audio to verify
ffplay product_list/{product_id}/ref_video/video_N_analysis_temp/audio.mp3
```

---

## File Structure After Analysis

```
product_list/{product_id}/
├── tabcut_data.json           # Source metadata
├── ref_video/
│   ├── video_1_{creator}.mp4
│   ├── video_1_analysis_temp/  # Temp (can be deleted)
│   │   ├── frames/            # Extracted keyframes
│   │   │   ├── frame_001.jpg
│   │   │   ├── frame_002.jpg
│   │   │   └── ...
│   │   └── audio.mp3          # Extracted audio
│   ├── video_1_analysis.md    # ← Generated analysis
│   ├── video_2_{creator}.mp4
│   ├── video_2_analysis_temp/
│   ├── video_2_analysis.md
│   └── ...
└── script/                    # Scripts use analysis (new workflow)
    ├── Product_Model_Angle1.md
    ├── Product_Model_Angle2.md
    └── Product_Model_Angle3.md
```

**Cleanup:** `*_analysis_temp/` directories can be deleted after successful analysis

---

## Next Step: Script Generation

After video analysis is complete:

1. **Check the analyses:**
   ```bash
   ls -lh product_list/{product_id}/ref_video/video_*_analysis.md
   ```

2. **Verify bilingual format:**
   - Check section headers have `English | 中文`
   - Check transcripts have Chinese translations

3. **Run script generation:**
   - Use `tiktok_script_generator.md` skill
   - Claude will read `video_*_analysis.md` files
   - Generate 3 production-ready scripts

**Workflow:**
```
[Hybrid Analysis] → video_N_analysis.md (bilingual)
                        ↓
            [Script Generator Skill] → 3 Scripts (German + Chinese)
```

---

## Version History

**v4.1.0** (2026-01-01) - **AUTOMATIC EXECUTION**
- **MAJOR CHANGE:** Skill now AUTO-RUNS conditionally (no longer manual/optional)
- **Auto-trigger logic:** Checks if `ref_video/` has .mp4 files after Step 1 → runs automatically
- **Updated description:** Changed from "Automated" to "AUTOMATIC" (clarifies it's conditional, not manual)
- **Added trigger conditions:** Documented when skill runs vs when it skips
- **Output requirement:** `video_synthesis.md` is now MANDATORY (not optional)
- **Why this matters:** Ensures video analysis never gets skipped when videos exist
- **Integration:** Part of automated workflow, not a standalone manual tool

**v4.0.0** (2025-12-29)
- **NEW:** Hybrid transcription workflow (TikTok captions → Whisper fallback)
- **NEW:** Bilingual output format (English + Chinese)
- **NEW:** Language detection and confidence scores
- **NEW:** Graceful handling of music-only content
- **Improved:** Python-based automated processing
- **Removed:** Manual gemini-cli prompts (now automated)

**v3.0.0** (Previous)
- Manual gemini-cli usage by user

**v2.0.0** (Previous)
- Four-tier system (failed due to MCP limitations)
