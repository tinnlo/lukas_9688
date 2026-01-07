# Quick Reference: Optimized Video Analysis

## Commands

### Run Batch Analysis (Optimized)
```bash
cd scripts
source venv/bin/activate
python analyze_video_batch.py <product_id> --date YYYYMMDD
```

### Run Performance Test
```bash
cd scripts
./test_optimization.sh
```

### Check Single Video
```bash
python analyze_single_video.py <product_id> <video_number> --date YYYYMMDD
```

---

## Expected Performance

| Videos | Old Time | New Time | Speedup |
|:-------|:---------|:---------|:--------|
| 1 | ~60s | ~25s | 2.4x |
| 3 | ~3min | ~60s | 3x |
| 5 | ~5min | ~90s | 3.3x |

---

## What Changed?

✅ **Whisper caching** - loads once, not per video  
✅ **Parallel extraction** - 5 FFmpeg at once  
✅ **Async Gemini** - 5 API calls at once  
✅ **640px frames** - smaller, faster  
✅ **Tiny Whisper** - 4x faster transcription  

---

## Files Modified

- `scripts/analyze_video_batch.py` - Main optimizations
- `scripts/analyze_single_video.py` - Consistency update
- `.skills/tiktok_ad_analysis.md` - Updated docs

---

## Troubleshooting

### "Rate limit exceeded"
→ Reduce concurrency in code (Semaphore(5) → Semaphore(3))

### "Frame quality too low"
→ Increase quality (q:v 8 → q:v 5) and resolution (640 → 800)

### "Transcription inaccurate"
→ Switch Whisper model (tiny → small)

---

## Validation

```bash
cd scripts
source venv/bin/activate
python3 -c "import analyze_video_batch; print('✅ OK')"
```

---

**Version:** 4.3.0 | **Date:** 2026-01-07 | **Status:** Production Ready
