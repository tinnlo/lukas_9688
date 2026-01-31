# How Concurrent Gemini Calls Work

## Overview

The concurrent Gemini implementation uses **Python's asyncio** with a **Semaphore** to control concurrency. Here's how it works:

---

## The Three Key Components

### 1. Async Gemini Function

**Location:** `analyze_video_batch.py` lines 631-945

```python
async def analyze_video_with_gemini_async(
    video_path: Path,
    frames_dir: Path,
    transcript: dict,
    duration: float,
    frame_count: int,
    metadata: dict,
    product_name: str
):
    # ... (build prompt and frame list)
    
    # Key part: Run gemini-cli as async subprocess
    proc = await asyncio.create_subprocess_exec(
        *cmd,  # ['gemini', '-o', 'text', '-m', 'model', 'frame1.jpg', ..., 'prompt']
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent.parent
    )
    
    # Wait for subprocess to complete (non-blocking)
    stdout, stderr = await asyncio.wait_for(
        proc.communicate(),
        timeout=300  # 5 minutes
    )
    
    # Return markdown result
    return _sanitize_markdown(stdout.decode(), required_first_line)
```

**Why async subprocess?**
- `asyncio.create_subprocess_exec()` creates a subprocess that doesn't block
- While waiting for Gemini API response, Python can start other subprocess calls
- This is **I/O-bound parallelism** - perfect for network API calls

---

### 2. Semaphore for Concurrency Control

**Location:** `analyze_video_batch.py` lines 1158-1196

```python
async def analyze_batch():
    """Run all Gemini analyses in parallel with concurrency limit."""
    
    # Semaphore limits concurrent operations to 5
    semaphore = asyncio.Semaphore(5)  # ← KEY: Max 5 at once
    
    async def bounded_analyze(data):
        # Wait for semaphore token (blocks if 5 already running)
        async with semaphore:
            # ... analyze video ...
            analysis_md = await analyze_video_with_gemini_async(...)
            # When this exits, semaphore releases token for next video
        
        return {"index": i, "success": True}
    
    # Run all analyses in parallel (up to 5 concurrent)
    results = await asyncio.gather(*[bounded_analyze(data) for data in video_data])
    return results
```

**How Semaphore works:**
```
Semaphore(5) = 5 tokens available

Video 1: Acquires token 1 → Starts Gemini call → Token busy
Video 2: Acquires token 2 → Starts Gemini call → Token busy
Video 3: Acquires token 3 → Starts Gemini call → Token busy
Video 4: Acquires token 4 → Starts Gemini call → Token busy
Video 5: Acquires token 5 → Starts Gemini call → Token busy
Video 6: WAITS (all tokens busy)
...
Video 1: Finishes → Releases token 1
Video 6: Acquires token 1 → Starts Gemini call
```

---

### 3. asyncio.gather() for Parallel Execution

**Location:** `analyze_video_batch.py` line 1195

```python
# Create list of async tasks (one per video)
tasks = [bounded_analyze(data) for data in video_data]

# Run all tasks concurrently
results = await asyncio.gather(*tasks)
```

**What `asyncio.gather()` does:**
- Starts all tasks immediately (doesn't wait for each to finish)
- Semaphore controls how many actually run at once
- Returns results in original order (even if they finish out of order)

---

## Complete Flow

```python
# PHASE 3 in analyze_all_videos()
async def analyze_batch():
    semaphore = asyncio.Semaphore(5)
    
    async def bounded_analyze(data):
        async with semaphore:  # ← Acquire token
            # Call async Gemini function
            result = await analyze_video_with_gemini_async(...)
            # Save result
            # ← Release token automatically
        return result
    
    # Start all 5 videos concurrently
    results = await asyncio.gather(*[bounded_analyze(d) for d in video_data])
    return results

# Run the async batch from sync code
results = asyncio.run(analyze_batch())
```

---

## Visual Timeline

**Without Concurrency (Old Way):**
```
Video 1: |████████████| (2 min)
Video 2:              |████████████| (2 min)
Video 3:                           |████████████| (2 min)
Video 4:                                        |████████████| (2 min)
Video 5:                                                     |████████████| (2 min)
───────────────────────────────────────────────────────────────────────────
Total: 10 minutes
```

**With Concurrency (New Way):**
```
Video 1: |████████████| (2 min)
Video 2: |████████████| (2 min)
Video 3: |████████████| (2 min)
Video 4: |████████████| (2 min)
Video 5: |████████████| (2 min)
───────────────────────────────────────────────────────────────────────────
Total: 2 minutes (all run at same time!)
```

---

## Proof It Works

**From test output:**
```
🤖 PHASE 3: Analyzing with Gemini (parallel, max 5 concurrent)...
  ✅ [5/5] video_5_sam505606.mp4: Analysis saved       ← Finished 1st
  ✅ [3/5] video_3_shopytiktok8.mp4: Analysis saved    ← Finished 2nd
  ✅ [4/5] video_4_shopytiktok8.mp4: Analysis saved    ← Finished 3rd
  ✅ [1/5] video_1_itsme_louliii.mp4: Analysis saved   ← Finished 4th
  ✅ [2/5] video_2_jannik0686.mp4: Analysis saved      ← Finished 5th
```

**Out-of-order completion (5→3→4→1→2) proves parallelism!** ✅

If they were sequential, they would finish in order: 1→2→3→4→5

---

## Key Technical Points

### 1. Why asyncio.gather() instead of threads?

```python
# ✅ GOOD: asyncio (our choice)
results = await asyncio.gather(*tasks)

# ❌ NOT USED: Threading
with ThreadPoolExecutor(5) as executor:
    results = executor.map(sync_function, videos)
```

**Reasons:**
- Gemini API calls are **I/O-bound** (waiting for network)
- asyncio has lower overhead than threads
- Better control with Semaphore
- Can use `await` syntax for clean code

### 2. Why Semaphore instead of running all at once?

```python
# ✅ GOOD: Controlled concurrency
semaphore = asyncio.Semaphore(5)  # Max 5

# ❌ BAD: Unlimited concurrency
# results = await asyncio.gather(*tasks)  # All 100 videos at once!
```

**Reasons:**
- Gemini API has rate limits
- Too many concurrent calls → HTTP 429 errors
- Semaphore provides **backpressure**

### 3. Why 5 concurrent calls?

Based on your experience:
> "I believe I define the most of 5 concurrent gemini asynce cli mcp by my previous experience"

You can adjust:
```python
# Conservative (avoid rate limits)
semaphore = asyncio.Semaphore(3)

# Aggressive (if you have high quota)
semaphore = asyncio.Semaphore(10)
```

---

## Code Location Summary

| Component | File | Lines | Purpose |
|:----------|:-----|:------|:--------|
| Async Gemini function | `analyze_video_batch.py` | 631-945 | Run gemini-cli as async subprocess |
| Semaphore + gather | `analyze_video_batch.py` | 1158-1196 | Control concurrency, run in parallel |
| Async batch runner | `analyze_video_batch.py` | 1199 | Entry point: `asyncio.run()` |

---

## Comparison with Old Code

**Old (Sequential):**
```python
for video in videos:
    analysis = analyze_video_with_gemini(video)  # Blocking call
    save_analysis(analysis)
# Takes 5x longer
```

**New (Concurrent):**
```python
async def analyze_batch():
    semaphore = asyncio.Semaphore(5)
    async def bounded_analyze(video):
        async with semaphore:
            return await analyze_video_with_gemini_async(video)
    
    results = await asyncio.gather(*[bounded_analyze(v) for v in videos])
    
asyncio.run(analyze_batch())
# 5x faster!
```

---

## Debugging Tips

### Check if parallelism is working:

**Add timing:**
```python
import time

async def bounded_analyze(data):
    start = time.time()
    async with semaphore:
        result = await analyze_video_with_gemini_async(...)
        elapsed = time.time() - start
        print(f"Video {i} took {elapsed:.1f}s")
    return result
```

**Expected output:**
```
Video 1 took 120.5s  ← All should finish around same time
Video 2 took 121.2s
Video 3 took 119.8s
Video 4 took 122.1s
Video 5 took 120.3s
```

If they're finishing with big gaps (e.g., 120s, 240s, 360s), then concurrency isn't working!

---

## Summary

**3 ingredients for concurrent Gemini calls:**

1. **`async def` + `await`** - Make functions non-blocking
2. **`asyncio.Semaphore(5)`** - Limit to 5 concurrent calls
3. **`asyncio.gather()`** - Run all tasks in parallel

**Result:** 5 Gemini API calls run simultaneously, saving ~8 minutes per batch! 🚀

---

**Questions?** Check the actual code in `analyze_video_batch.py` lines 1158-1199!
