#!/bin/bash
set -e

echo "=== E2E Workflow: 7 Products to product_list/samples/ ==="
echo ""

PRODUCT_IDS=(
  "1729582760298126134"
  "1729578893675305782"
  "1729656437150292790"
  "1729581033272679222"
  "1729752455966792502"
  "1729695453196425349"
  "1729759408296335493"
)

REPO_ROOT="/Users/lxt/Movies/TikTok/WZ/lukas_9688"
SCRIPTS_DIR="$REPO_ROOT/scripts"
OUT_DIR="$REPO_ROOT/product_list/samples"
DATE="samples"

cd "$SCRIPTS_DIR"
source venv/bin/activate

# ========================================
# PHASE 1: SCRAPING
# ========================================
echo "=== PHASE 1: SCRAPING ==="
echo "Scraping 7 products with videos..."
echo ""

python run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "$OUT_DIR"

echo ""
echo "✅ Phase 1 complete"
echo ""

# ========================================
# PHASE 2A: VIDEO ANALYSIS (PARALLEL)
# ========================================
echo "=== PHASE 2A: VIDEO ANALYSIS (PARALLEL) ==="
echo ""

# Batch 1: 5 products
echo "Batch 1: Launching 5 products in parallel..."
for pid in "${PRODUCT_IDS[@]:0:5}"; do
  echo "  Starting $pid..."
  python analyze_video_batch.py "$pid" --date "$DATE" &
done
wait
echo "✅ Batch 1 complete (5 products)"
echo ""

# Batch 2: 2 products
echo "Batch 2: Launching 2 products in parallel..."
for pid in "${PRODUCT_IDS[@]:5:2}"; do
  echo "  Starting $pid..."
  python analyze_video_batch.py "$pid" --date "$DATE" &
done
wait
echo "✅ Batch 2 complete (2 products)"
echo ""
echo "✅ Phase 2A complete (all videos analyzed)"
echo ""

# ========================================
# PHASE 2B+2C: IMAGE + SYNTHESIS (PARALLEL WITHIN PRODUCT)
# ========================================
echo "=== PHASE 2B+2C: IMAGE ANALYSIS + VIDEO SYNTHESIS ==="
echo ""

for i in "${!PRODUCT_IDS[@]}"; do
  pid="${PRODUCT_IDS[$i]}"
  echo "[$((i+1))/7] Processing product $pid..."

  # Launch image + synthesis in parallel
  python analyze_product_images.py "$pid" --date "$DATE" &
  python create_video_synthesis.py "$pid" --date "$DATE" &
  wait

  echo "✅ Product $pid complete"
done

echo ""
echo "✅ Phase 2B+2C complete (all analysis done)"
echo ""

# ========================================
# QUALITY GATE
# ========================================
echo "=== QUALITY GATE: ANALYSIS VERIFICATION ==="
echo ""

bash verify_gate.sh \
  --base "$OUT_DIR" \
  --product-ids "${PRODUCT_IDS[*]}" \
  --phase analysis

if [ $? -ne 0 ]; then
  echo "❌ Quality gate failed. Check analysis files."
  exit 1
fi

echo ""
echo "✅ Quality gate passed"
echo ""

# ========================================
# PHASE 3: SCRIPT GENERATION
# ========================================
echo "=== PHASE 3: SCRIPT GENERATION (Claude Code) ==="
echo ""
echo "⚠️  This phase requires Claude Code interaction"
echo ""
echo "For each product, Claude will:"
echo "  1. Read analysis files in parallel"
echo "  2. Generate 3 scripts + Campaign Summary"
echo "  3. Write all 4 files in parallel"
echo ""
echo "Products ready for script generation:"
for i in "${!PRODUCT_IDS[@]}"; do
  echo "  [$((i+1))] ${PRODUCT_IDS[$i]}"
done
echo ""
echo "Run Claude Code with:"
echo "  cd $REPO_ROOT"
echo "  # Use tiktok_script_generator.md skill for each product"
echo ""
read -p "Press Enter after scripts are generated..."
echo ""

# ========================================
# PHASE 4: PRODUCT INDEX GENERATION
# ========================================
echo "=== PHASE 4: PRODUCT INDEX GENERATION ==="
echo ""
echo "Generating product_index.md for successful products..."
echo ""

python3 generate_product_indices.py \
  --base "$OUT_DIR" \
  --product-ids "${PRODUCT_IDS[*]}" \
  --require-scripts \
  --incremental

echo ""
echo "✅ Phase 4 complete"
echo ""

# ========================================
# FINAL VERIFICATION
# ========================================
echo "=== FINAL VERIFICATION ==="
echo ""

bash verify_gate.sh \
  --base "$OUT_DIR" \
  --product-ids "${PRODUCT_IDS[*]}" \
  --phase all

if [ $? -ne 0 ]; then
  echo "⚠️  Some products incomplete. Check output above."
fi

echo ""
echo "=== E2E WORKFLOW COMPLETE ==="
echo "Total products processed: 7"
echo "Output directory: $OUT_DIR"
echo ""
echo "Next steps:"
echo "  - Review product_index.md files in Obsidian"
echo "  - Check scripts/ folders for quality"
echo "  - Run compliance validators if needed"
echo ""
