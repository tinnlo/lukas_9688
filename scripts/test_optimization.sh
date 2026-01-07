#!/bin/bash
# Test script to verify optimization improvements
# Measures time for video analysis with the new optimized code

set -e

# Configuration
PRODUCT_ID="1729600227153779322"
DATE="20251230"
TEST_DIR="product_list/${DATE}/${PRODUCT_ID}/ref_video"

echo "=================================================="
echo "TikTok Video Analysis Optimization Test"
echo "=================================================="
echo ""
echo "Product ID: ${PRODUCT_ID}"
echo "Date: ${DATE}"
echo "Test Directory: ${TEST_DIR}"
echo ""

# Check if videos exist
VIDEO_COUNT=$(find "${TEST_DIR}" -name "*.mp4" 2>/dev/null | wc -l | xargs)
echo "Videos found: ${VIDEO_COUNT}"

if [ "${VIDEO_COUNT}" -eq 0 ]; then
    echo "❌ No videos found in ${TEST_DIR}"
    exit 1
fi

echo ""
echo "=================================================="
echo "Starting optimized batch analysis..."
echo "=================================================="
echo ""

# Record start time
START_TIME=$(date +%s)

# Run the optimized batch script
cd scripts
source venv/bin/activate 2>/dev/null || true

python analyze_video_batch.py "${PRODUCT_ID}" --date "${DATE}"

# Record end time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
echo "Test Complete!"
echo "=================================================="
echo ""
echo "Total time: ${DURATION} seconds"
echo "Videos processed: ${VIDEO_COUNT}"
echo "Average time per video: $((DURATION / VIDEO_COUNT)) seconds"
echo ""

# Check if analysis files were created
ANALYSIS_COUNT=$(find "../${TEST_DIR}" -name "video_*_analysis.md" 2>/dev/null | wc -l | xargs)
echo "Analysis files created: ${ANALYSIS_COUNT}/${VIDEO_COUNT}"

if [ "${ANALYSIS_COUNT}" -eq "${VIDEO_COUNT}" ]; then
    echo "✅ All videos analyzed successfully!"
else
    echo "⚠️ Some videos failed analysis"
fi

echo ""
echo "Expected time (old): ~$((VIDEO_COUNT * 60)) seconds (~$((VIDEO_COUNT)) minutes)"
echo "Actual time (new): ${DURATION} seconds (~$((DURATION / 60)) minutes)"
echo "Speedup: ~$((VIDEO_COUNT * 60 / DURATION))x faster"
