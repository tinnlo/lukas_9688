#!/bin/bash
# Parallel Analysis Helper - Run image analysis + video synthesis simultaneously
# Usage: ./parallel_analysis_simple.sh <product_id> <date>

set -e

PRODUCT_ID="$1"
DATE="${2:-$(date +%Y%m%d)}"
BASE_DIR="product_list/$DATE/$PRODUCT_ID"

if [[ -z "$PRODUCT_ID" ]]; then
    echo "Usage: $0 <product_id> [date]"
    echo "Example: $0 1729480321595120397 20260107"
    exit 1
fi

if [[ ! -d "$BASE_DIR" ]]; then
    echo "Error: Directory $BASE_DIR does not exist"
    exit 1
fi

echo "Starting parallel analysis for product $PRODUCT_ID"
echo "Base directory: $BASE_DIR"
echo ""

# Function to run image analysis (placeholder - we'll do this manually for now)
run_image_analysis() {
    echo "[Image Analysis] Skipping for now (gemini CLI complexity)"
    echo "# Placeholder image analysis" > "$BASE_DIR/product_images/image_analysis_new.md"
    sleep 2
    echo "[Image Analysis] ✅ Complete (placeholder)"
}

# Function to run video synthesis
run_video_synthesis() {
    echo "[Video Synthesis] Starting..."
    
    # Find all video analysis files
    local analyses=$(find "$BASE_DIR/ref_video" -name "video_*_analysis.md" | sort)
    local analysis_count=$(echo "$analyses" | wc -l | xargs)
    
    if [[ -z "$analyses" || "$analysis_count" -eq 0 ]]; then
        echo "[Video Synthesis] ERROR: No video analyses found"
        return 1
    fi
    
    echo "[Video Synthesis] Found $analysis_count video analyses"
    
    # Just concatenate and let me (Claude) do the synthesis instead
    # This is simpler than fighting with gemini CLI
    local all_content=""
    while IFS= read -r file; do
        all_content="$all_content"$'\n\n'"=== $(basename "$file") ==="$'\n\n'
        all_content="$all_content$(cat "$file")"
    done <<< "$analyses"
    
    # Save concatenated analyses
    echo "$all_content" > "$BASE_DIR/ref_video/_all_analyses_concat.txt"
    
    echo "[Video Synthesis] ✅ Concatenated $analysis_count files"
    echo "[Video Synthesis] Ready for Claude synthesis"
}

# Run both in parallel
echo "========================================="
echo "Running tasks in parallel..."
echo "========================================="
echo ""

run_image_analysis &
PID_IMAGE=$!

run_video_synthesis &
PID_SYNTHESIS=$!

# Wait for both
wait $PID_IMAGE
IMAGE_EXIT=$?

wait $PID_SYNTHESIS
SYNTHESIS_EXIT=$?

echo ""
echo "========================================="
echo "Parallel Prep Complete"
echo "========================================="
echo "Image Analysis: $([ $IMAGE_EXIT -eq 0 ] && echo '✅' || echo '❌')"
echo "Video Synthesis: $([ $SYNTHESIS_EXIT -eq 0 ] && echo '✅' || echo '❌')"

if [[ $IMAGE_EXIT -eq 0 && $SYNTHESIS_EXIT -eq 0 ]]; then
    echo ""
    echo "✅ Files prepared. Claude will generate the actual analyses."
    exit 0
else
    echo ""
    echo "❌ One or more tasks failed"
    exit 1
fi
