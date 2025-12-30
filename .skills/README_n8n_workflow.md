# TikTok Content Creation Workflow (n8n)

Complete 3-step workflow for TikTok product video script generation, designed for n8n orchestration.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TikTok Content Workflow                       │
└─────────────────────────────────────────────────────────────────┘

Step 1: Product Scraping
├── Input: Product ID(s)
├── Tool: Python scraper (n8n Execute Command)
├── Options: Download videos YES/NO
└── Output: tabcut_data.json + tabcut_data.md [+ ref_video/*.mp4]
         ↓
Step 2: Ad Analysis
├── Input: tabcut_data.json + ref_video/*.mp4
├── Tool: gemini-cli (User runs manually)
├── Action: Analyze reference videos + product images
└── Output: video_analysis.md + image_analysis.md
         ↓
Step 3: Script Generation
├── Input: All analysis files
├── Tool: Claude Code (n8n API call)
├── Action: Generate 3 production-ready scripts
└── Output: 3 script .md files + Campaign_Summary.md
```

---

## Skills Files

| Step | Skill File | Who Runs It | Purpose |
|:-----|:-----------|:------------|:--------|
| **1** | `.skills/tiktok_product_scraper.md` | n8n workflow | Scrape product data from tabcut.com |
| **2** | `.skills/tiktok_ad_analysis.md` | User (gemini-cli) | Analyze videos and create intelligence reports |
| **3** | `.skills/tiktok_script_generator.md` | Claude Code | Generate 3 TikTok ad scripts |

---

## Step 1: Product Scraping

**Skill:** `.skills/tiktok_product_scraper.md`

### n8n Node Configuration

**Node Type:** Execute Command

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts && \
source venv/bin/activate && \
python run_scraper.py --product-id {{$json.product_id}} {{$json.download_videos ? '--download-videos' : ''}} && \
python convert_json_to_md.py {{$json.product_id}}
```

**Input Parameters:**
```json
{
  "product_id": "1729630936525936882",
  "download_videos": true
}
```

**Output:**
```
product_list/{product_id}/
├── tabcut_data.json
├── tabcut_data.md          ← Review this file
└── ref_video/              ← If download_videos=true
    ├── video_1_{creator}.mp4
    ├── video_2_{creator}.mp4
    ├── video_3_{creator}.mp4
    ├── video_4_{creator}.mp4
    └── video_5_{creator}.mp4
```

**Success Criteria:**
- `tabcut_data.json` created
- `tabcut_data.md` created for human review
- Videos downloaded (if requested)

---

## Step 2: Ad Analysis

**Skill:** `.skills/tiktok_ad_analysis.md`

### Manual Execution (User)

**This step runs OUTSIDE n8n - user executes in terminal**

```bash
# Navigate to product directory
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/1729630936525936882/ref_video/

# Run video analysis with gemini-cli
gemini "$(cat ../tabcut_data.json)" "Analyze all MP4 videos in current directory. [See full prompt in skill file]" > ../video_analysis.md

# Run image analysis (if product_images/ exists)
cd ../product_images/
gemini "Analyze all images for product intelligence. [See full prompt in skill file]" > image_analysis.md
```

**Output:**
```
product_list/{product_id}/
├── video_analysis.md       ← Created by user
└── product_images/
    └── image_analysis.md   ← Created by user
```

**Success Criteria:**
- `video_analysis.md` contains market insights for all reference videos
- `image_analysis.md` contains product packaging analysis (if images available)

### n8n Integration Option

If you want to automate this in n8n:

**Node Type:** Execute Command

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/{{$json.product_id}}/ref_video && \
gemini "$(cat ../tabcut_data.json)" "[Full prompt from tiktok_ad_analysis.md]" > ../video_analysis.md
```

**Note:** Requires gemini-cli accessible from n8n environment

---

## Step 3: Script Generation

**Skill:** `.skills/tiktok_script_generator.md`

### n8n Node Configuration

**Option A: Execute via Claude Code CLI**

**Node Type:** Execute Command

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688 && \
claude "Generate 3 TikTok scripts for product {{$json.product_id}} using the tiktok-script-generator skill. Category: {{$json.category}}"
```

**Option B: HTTP Request to Claude API**

**Node Type:** HTTP Request

**Method:** POST
**URL:** `https://api.anthropic.com/v1/messages`
**Headers:**
```json
{
  "x-api-key": "{{$env.ANTHROPIC_API_KEY}}",
  "anthropic-version": "2023-06-01",
  "content-type": "application/json"
}
```

**Body:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 16000,
  "messages": [
    {
      "role": "user",
      "content": "Use the tiktok-script-generator skill to create 3 TikTok ad scripts for product ID: {{$json.product_id}}, Category: {{$json.category}}"
    }
  ]
}
```

**Input Parameters:**
```json
{
  "product_id": "1729630936525936882",
  "category": "Electronics"
}
```

**Output:**
```
shorts_scripts/{product_id}/
├── {Product}_{Angle1}.md
├── {Product}_{Angle2}.md
├── {Product}_{Angle3}.md
└── Campaign_Summary.md
```

**Success Criteria:**
- 3 unique script files created
- Campaign_Summary.md created
- All scripts have YAML frontmatter
- Scripts are 30-40 seconds duration
- Bilingual (DE + ZH)
- Compliance verified

---

## Complete n8n Workflow Template

```json
{
  "name": "TikTok Content Generation",
  "nodes": [
    {
      "name": "Start",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [100, 200]
    },
    {
      "name": "Step 1: Scrape Product",
      "type": "n8n-nodes-base.executeCommand",
      "position": [300, 200],
      "parameters": {
        "command": "cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts && source venv/bin/activate && python run_scraper.py --product-id {{$json.product_id}} {{$json.download_videos ? '--download-videos' : ''}} && python convert_json_to_md.py {{$json.product_id}}"
      }
    },
    {
      "name": "Human Review: tabcut_data.md",
      "type": "n8n-nodes-base.wait",
      "position": [500, 200],
      "parameters": {
        "resume": "webhook",
        "responseMessage": "Please review tabcut_data.md and click Continue"
      }
    },
    {
      "name": "Step 2: Manual Gemini Analysis",
      "type": "n8n-nodes-base.wait",
      "position": [700, 200],
      "parameters": {
        "resume": "webhook",
        "responseMessage": "Run gemini-cli analysis, then click Continue"
      }
    },
    {
      "name": "Step 3: Generate Scripts",
      "type": "n8n-nodes-base.executeCommand",
      "position": [900, 200],
      "parameters": {
        "command": "cd /Users/lxt/Movies/TikTok/WZ/lukas_9688 && claude 'Generate scripts for {{$json.product_id}} category {{$json.category}}'"
      }
    },
    {
      "name": "Done",
      "type": "n8n-nodes-base.noOp",
      "position": [1100, 200]
    }
  ],
  "connections": {
    "Start": { "main": [[{ "node": "Step 1: Scrape Product" }]] },
    "Step 1: Scrape Product": { "main": [[{ "node": "Human Review: tabcut_data.md" }]] },
    "Human Review: tabcut_data.md": { "main": [[{ "node": "Step 2: Manual Gemini Analysis" }]] },
    "Step 2: Manual Gemini Analysis": { "main": [[{ "node": "Step 3: Generate Scripts" }]] },
    "Step 3: Generate Scripts": { "main": [[{ "node": "Done" }]] }
  }
}
```

**Workflow Input:**
```json
{
  "product_id": "1729630936525936882",
  "download_videos": true,
  "category": "Electronics"
}
```

---

## Batch Processing (Multiple Products)

### n8n Workflow for Batch

```json
{
  "name": "TikTok Batch Content Generation",
  "nodes": [
    {
      "name": "Read CSV",
      "type": "n8n-nodes-base.spreadsheetFile",
      "position": [100, 200],
      "parameters": {
        "operation": "read",
        "filePath": "/path/to/products.csv"
      }
    },
    {
      "name": "Split Into Batches",
      "type": "n8n-nodes-base.splitInBatches",
      "position": [300, 200],
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "name": "Step 1: Scrape Product",
      "type": "n8n-nodes-base.executeCommand",
      "position": [500, 200]
    },
    {
      "name": "Wait: Manual Review",
      "type": "n8n-nodes-base.wait",
      "position": [700, 200]
    },
    {
      "name": "Step 3: Generate Scripts",
      "type": "n8n-nodes-base.executeCommand",
      "position": [900, 200]
    }
  ]
}
```

---

## File Structure (After Complete Workflow)

```
product_list/{product_id}/
├── tabcut_data.json              # Step 1 output
├── tabcut_data.md                # Step 1 output (for review)
├── video_analysis.md             # Step 2 output (manual)
├── product_images/
│   ├── product_image_1.webp
│   ├── ...
│   └── image_analysis.md         # Step 2 output (manual)
└── ref_video/
    ├── video_1_{creator}.mp4     # Step 1 output (optional)
    ├── video_2_{creator}.mp4
    ├── ...
    └── video_5_{creator}.mp4

shorts_scripts/{product_id}/
├── {Product}_{Angle1}.md         # Step 3 output
├── {Product}_{Angle2}.md         # Step 3 output
├── {Product}_{Angle3}.md         # Step 3 output
└── Campaign_Summary.md           # Step 3 output
```

---

## Key Decision Points

### 1. Download Videos?

**YES** - Download videos in Step 1:
- ✅ Enables detailed video analysis in Step 2
- ✅ Can extract exact hooks, VO transcripts, shot breakdowns
- ✅ Higher quality script generation in Step 3
- ❌ Larger storage (50-200 MB per product)
- ❌ Slower scraping (~2-5 minutes per product)

**NO** - Skip video downloads:
- ✅ Faster scraping (~30 seconds per product)
- ✅ Minimal storage (~10 KB per product)
- ✅ Good for quick metadata gathering
- ❌ Step 2 analysis will be metadata-based inference only
- ❌ Scripts will miss specific creative insights

**Recommendation:** Download videos for your top-priority products

### 2. Manual vs Automated Step 2?

**Manual (Recommended):**
- User runs gemini-cli in terminal
- Full control over analysis quality
- Can verify gemini is actually watching videos
- Best for high-value products

**Automated (n8n):**
- Runs gemini-cli via Execute Command node
- Faster for batch processing
- Requires gemini accessible from n8n environment
- Less quality control

---

## Error Handling & Auto-Recovery

### Step 1 Failures (Product Scraping)

#### Tabcut.com Failures → Auto-Fallback to FastMoss

**NEW FEATURE:** The scraper now automatically falls back to FastMoss when Tabcut fails.

**Automatic Fallback Triggers:**
- ❌ Product name is "Unknown Product" or "undefined"
- ❌ Total sales is `null` or `-`
- ❌ Zero product images downloaded
- ❌ Zero videos available

**When fallback occurs:**
```bash
⚠️ Tabcut returned insufficient data for product 1729724699406473785
   → Automatically retrying with FastMoss as data source...
✅ FastMoss scraping successful! (2 images, 5 videos)
```

**Manual Fallback (if needed):**
```bash
cd scripts && source venv/bin/activate
python run_scraper.py --product-id {PRODUCT_ID} --source fastmoss --download-videos
```

#### Other Step 1 Failures

**Scraper authentication fails:**
- Check credentials in `scripts/config/.env`
- Verify `TABCUT_USERNAME` and `TABCUT_PASSWORD` are set
- For FastMoss: verify `FASTMOSS_USERNAME` and `FASTMOSS_PASSWORD`

**MD conversion fails:**
- Check if `tabcut_data.json` or `fastmoss_data.json` exists
- For FastMoss data, copy to `tabcut_data.json`:
  ```bash
  cp product_list/{ID}/fastmoss_data.json product_list/{ID}/tabcut_data.json
  python convert_json_to_md.py {ID}
  ```

**Product permanently unavailable:**
- Skip product if both Tabcut AND FastMoss return no data
- Log as "SKIPPED - No data on any source"

### Step 2 Failures (Video/Image Analysis)

**Gemini can't access videos:**
- Verify MP4 files exist in `ref_video/`
- Use absolute paths when calling Gemini MCP
- Check gemini-cli is installed: `which gemini` or `gemini --version`

**Analysis seems hallucinated:**
- Ask gemini to describe specific timestamps
- Request frame-by-frame breakdown for suspicious sections
- Cross-check video duration with ffmpeg

**Whisper transcription too slow:**
- Expected behavior for longer videos (>1 min)
- Use faster-whisper model: already configured
- Consider using TikTok captions as primary (hybrid workflow)

**Video analysis errors (FFmpeg):**
- Error 234: Corrupted video file → Skip video, continue with others
- "No such file": Check video download completed successfully
- Audio extraction fails: Continue with visual-only analysis

### Step 3 Failures (Script Generation)

**Claude can't find analysis files:**
- Verify `video_synthesis.md` exists (required)
- Verify `image_analysis.md` exists (if product has images)
- Check file paths use correct product ID directory

**Scripts don't meet quality standards:**
- Review input analysis files for completeness
- Ensure category compliance rules followed
- Verify 3 distinct hook angles were used
- Check bilingual voiceovers (DE + ZH) are present

**Low-quality scripts (generic/templated feel):**
- Input analysis may be insufficient → Re-run Step 2 with more detail
- Ensure video_synthesis has specific market insights, not generic observations
- Request Claude to add 2+ "human beats" (reactions, asides, self-corrections)

---

## Quality Gates

### After Step 1
- [ ] `tabcut_data.json` created
- [ ] `tabcut_data.md` created and reviewed
- [ ] Product data looks accurate
- [ ] Videos downloaded (if requested)
- [ ] Ready to proceed to Step 2

### After Step 2
- [ ] `video_analysis.md` created
- [ ] All reference videos analyzed
- [ ] Market insights section included
- [ ] `image_analysis.md` created (if images available)
- [ ] Ready to proceed to Step 3

### After Step 3
- [ ] 3 unique scripts created
- [ ] Campaign_Summary.md created
- [ ] All scripts have frontmatter
- [ ] Duration targets met (30-40s)
- [ ] Bilingual (DE + ZH)
- [ ] Compliance verified
- [ ] Ready for production

---

## Tips for n8n Setup

### Environment Variables

Set in n8n environment:
```bash
ANTHROPIC_API_KEY=sk-ant-...
TABCUT_USERNAME=your_username
TABCUT_PASSWORD=your_password
```

### Webhook Triggers

For manual review steps, use webhooks:
```
http://localhost:5678/webhook/tiktok-review-step1
http://localhost:5678/webhook/tiktok-review-step2
```

### Error Notifications

Add notification nodes after each step:
- Email on failure
- Slack notification on completion
- Log to database for tracking

---

## Session Learnings & Best Practices

### From Production Run (2025-12-30)

**Products Processed:** 7 total (5 successful, 2 skipped)
**Scripts Generated:** 15 production-ready scripts
**Total Coverage:** 6,787 units sold | €221K+ revenue

#### Key Successes ✅

1. **Hybrid Transcription Works Perfectly**
   - TikTok captions (yt-dlp) → Whisper fallback
   - Detected languages: DE, RU, AR, EN
   - Zero hallucinations observed

2. **Gemini MCP Image Analysis = Game Changer**
   - Extracted packaging details, trust signals, unique features
   - Enabled compliance checks (SUS 304, certifications)
   - Provided visual hooks for script writing

3. **Video Synthesis Creates Market Intelligence**
   - Identified winning patterns (e.g., "Old vs New" upgrade narrative)
   - Spotted conversion drivers (46.67% CVR for Pirate Ship!)
   - Recommended specific visual shots and duration ranges

4. **Script Diversity Works**
   - 3 distinct hook angles per product avoided repetition
   - Counter-Intuitive, Pain Point, Documentary = highest conversions
   - ElevenLabs v3 grammar kept voiceovers natural

#### Failure Patterns & Fixes ❌→✅

1. **Problem:** Tabcut returned "Unknown Product" for 2 products
   - **Fix:** Implemented FastMoss fallback (recovered Product 3)
   - **Learning:** Always try 2+ data sources before skipping

2. **Problem:** Video 3 corrupted (FFmpeg error 234)
   - **Fix:** Continued with 2/5 videos successfully analyzed
   - **Learning:** Partial data > no data; don't block on single failures

3. **Problem:** Low sales products (11 units) = weak insights
   - **Fix:** Flag products <50 sales as "low confidence"
   - **Learning:** Prioritize products with >200 sales for best ROI

#### Performance Benchmarks

| Metric | Target | Actual | Status |
|:-------|:-------|:-------|:-------|
| Scraping speed | 2-5 min | 2-4 min | ✅ Met |
| Video analysis | 2-4 min | 3-6 min | ⚠️ Slow (expected for Whisper) |
| Script generation | 2-3 min | 2-3 min | ✅ Met |
| **Total per product** | **6-12 min** | **7-13 min** | ✅ Met |
| Overall success rate | >70% | 71% (5/7) | ✅ Met |

#### Top Performing Products (for future targeting)

1. **Steam Cleaner:** 4,151 sales | 60% CVR | €135K revenue
   - **Why:** Pain point (grease removal) + chemiefrei messaging
2. **Pirate Ship Bottle:** 391 sales | **46.67% CVR** | €2.8K revenue
   - **Why:** ASMR/satisfying content + single creator dominance
3. **Rose Bear:** 1,449 sales | €18.2K revenue
   - **Why:** Seasonal (Valentine's) + "eternal" vs real flowers angle

#### Script Quality Indicators

**High-Quality Scripts Include:**
- ✅ Specific numbers (60s vs 20s, €7 vs €30, 46.67% conversion)
- ✅ 2+ human beats (reactions, asides, questions)
- ✅ Irregular pacing (short hits + medium sentences)
- ✅ ElevenLabs v3 cues: 3-4 per script (not overdirected)
- ✅ Visual cue descriptions (vortex, foam, LED display)

**Low-Quality Scripts Avoid:**
- ❌ Generic praise ("amazing", "incredible", "game-changer")
- ❌ Repeated cadence (every sentence same length)
- ❌ Over-explaining (let visuals speak)
- ❌ Medical/legal guarantees without proof

---

## Version History

**v2.0.0** (2025-12-30)
- **NEW:** Automatic Tabcut→FastMoss fallback on failures
- **NEW:** Session learnings and benchmarks section
- **NEW:** Enhanced error handling documentation
- **IMPROVED:** Video analysis error recovery (partial data strategy)
- **IMPROVED:** Low-volume product handling guidance

**v1.0.0** (2025-12-29)
- Initial n8n workflow documentation
- 3-step orchestration guide
- Batch processing support
- Quality gates and error handling
