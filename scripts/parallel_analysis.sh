#!/bin/bash
# Parallel Analysis Helper - Run image analysis + video synthesis simultaneously
# Usage: ./parallel_analysis.sh <product_id> <date>

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

# Function to run image analysis
run_image_analysis() {
    echo "[Image Analysis] Starting..."
    
    # Find all product images
    local images=$(find "$BASE_DIR/product_images" -name "*.webp" -o -name "*.jpg" -o -name "*.png" 2>/dev/null | sort)
    local image_count=$(echo "$images" | wc -l | xargs)
    
    if [[ -z "$images" || "$image_count" -eq 0 ]]; then
        echo "[Image Analysis] ERROR: No product images found in $BASE_DIR/product_images"
        return 1
    fi
    
    echo "[Image Analysis] Found $image_count images"
    
    # Read all images using filesystem tool (gemini can access them)
    local image_paths=""
    while IFS= read -r img; do
        image_paths="$image_paths$img"$'\n'
    done <<< "$images"
    
    # Run gemini CLI with prompt (using default model)
    local prompt="You are analyzing product images for a TikTok affiliate campaign.

Read and analyze the following $image_count product images located in:
$BASE_DIR/product_images/

Create a comprehensive bilingual analysis.

## Requirements:
- Create sections: Product Overview, Visual Features, Usage Scenarios, Market Positioning, etc.
- Bilingual format (English headers + Chinese notes)
- Identify key selling points visible in images
- Note any lifestyle/context shots vs pure product shots
- Suggest visual hooks for video scripts
- Output at least 80+ lines

Output the analysis directly (will be saved to file)."

    echo "$prompt" | gemini -o text > "$BASE_DIR/product_images/image_analysis.md" 2>&1
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        local lines=$(wc -l < "$BASE_DIR/product_images/image_analysis.md")
        echo "[Image Analysis] ✅ Complete ($lines lines)"
    else
        echo "[Image Analysis] ❌ Failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Function to run video synthesis
run_video_synthesis() {
    echo "[Video Synthesis] Starting..."
    
    # Find all video analysis files
    local analyses=$(find "$BASE_DIR/ref_video" -name "video_*_analysis.md" | sort)
    local analysis_count=$(echo "$analyses" | wc -l | xargs)
    
    if [[ -z "$analyses" || "$analysis_count" -eq 0 ]]; then
        echo "[Video Synthesis] ERROR: No video analyses found in $BASE_DIR/ref_video"
        return 1
    fi
    
    echo "[Video Synthesis] Found $analysis_count video analyses"
    
    # Read all analysis files into context
    local all_analyses=""
    local file_list=""
    while IFS= read -r analysis; do
        file_list="$file_list- $(basename "$analysis")"$'\n'
        all_analyses="$all_analyses"$'\n'"=== $(basename "$analysis") ==="$'\n'
        all_analyses="$all_analyses$(cat "$analysis")"$'\n\n'
    done <<< "$analyses"
    
    # Run gemini CLI with embedded file content (using default model)
    local prompt="You are synthesizing TikTok market insights from multiple video analyses.

I have analyzed $analysis_count videos and here are the complete analyses:

$all_analyses

Based on these analyses, create a comprehensive market synthesis.

## Required Sections (Bilingual: EN headers + CN notes):
1. Market Overview (total views, sales, performance summary)
2. Winning Hook Patterns (what worked best)
3. Consolidated Selling Points (key product benefits that drove sales)
4. Creative Patterns & Production Styles (visual techniques)
5. Audience Targeting Insights (demographics, psychographics)
6. CTA Strategy Analysis (what CTAs converted)
7. Germany Market Adaptation (cultural insights)
8. Performance Correlation (high vs low performers table)
9. Replication Strategy (what to copy, avoid, test)
10. Script Generation Recommendations (20-25s structure)

## Analysis Requirements:
- Identify which videos had sales vs no sales
- Correlate creative patterns with performance
- Extract winning hooks, CTAs, and visual techniques
- Provide actionable insights for script generation
- Minimum 80+ lines of comprehensive analysis

Output the synthesis directly (will be saved to file)."

    echo "$prompt" | gemini -o text > "$BASE_DIR/ref_video/video_synthesis.md" 2>&1
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        local lines=$(wc -l < "$BASE_DIR/ref_video/video_synthesis.md")
        echo "[Video Synthesis] ✅ Complete ($lines lines)"
    else
        echo "[Video Synthesis] ❌ Failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Run both tasks in parallel using background jobs
echo "========================================="
echo "Running image analysis + video synthesis in parallel..."
echo "========================================="
echo ""

run_image_analysis &
PID_IMAGE=$!

run_video_synthesis &
PID_SYNTHESIS=$!

# Wait for both to complete
wait $PID_IMAGE
IMAGE_EXIT=$?

wait $PID_SYNTHESIS
SYNTHESIS_EXIT=$?

echo ""
echo "========================================="
echo "Parallel Analysis Complete"
echo "========================================="
echo "Image Analysis: $([ $IMAGE_EXIT -eq 0 ] && echo '✅ Success' || echo '❌ Failed')"
echo "Video Synthesis: $([ $SYNTHESIS_EXIT -eq 0 ] && echo '✅ Success' || echo '❌ Failed')"

# Check if both succeeded
if [[ $IMAGE_EXIT -eq 0 && $SYNTHESIS_EXIT -eq 0 ]]; then
    echo ""
    echo "✅ All tasks completed successfully"
    
    # Show file sizes
    echo ""
    echo "Generated files:"
    ls -lh "$BASE_DIR/product_images/image_analysis.md"
    ls -lh "$BASE_DIR/ref_video/video_synthesis.md"
    
    exit 0
else
    echo ""
    echo "❌ One or more tasks failed"
    exit 1
fi
