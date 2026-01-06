#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
verify_gate.sh — Vault quality gate verifier for TikTok workflow

Usage:
  scripts/verify_gate.sh --date YYYYMMDD [--csv scripts/products.csv] [--phase analysis|scripts|all]
  scripts/verify_gate.sh --base product_list/YYYYMMDD --product-ids "id1 id2" [--phase analysis|scripts|all]

Options:
  --date YYYYMMDD              Date folder under product_list/ (e.g. 20260103)
  --base PATH                  Base folder that contains product_id subfolders (e.g. product_list/20260103)
  --csv PATH                   CSV with header product_id (default: scripts/products.csv)
  --product-ids "..."          Space-separated product IDs (overrides --csv)
  --phase analysis|scripts|all What to verify (default: all)
  --image-min-lines N          Min lines for product_images/image_analysis.md (default: 200)
  --synthesis-min-lines N      Min lines for ref_video/video_synthesis.md (default: 150)

Exit codes:
  0 = all products PASS
  1 = at least one product FAIL
EOF
}

DATE=""
BASE=""
CSV="scripts/products.csv"
PRODUCT_IDS=""
PHASE="all"
IMAGE_MIN_LINES=200
SYNTHESIS_MIN_LINES=150

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="${2:-}"; shift 2 ;;
    --base) BASE="${2:-}"; shift 2 ;;
    --csv) CSV="${2:-}"; shift 2 ;;
    --product-ids) PRODUCT_IDS="${2:-}"; shift 2 ;;
    --phase) PHASE="${2:-}"; shift 2 ;;
    --image-min-lines) IMAGE_MIN_LINES="${2:-}"; shift 2 ;;
    --synthesis-min-lines) SYNTHESIS_MIN_LINES="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$BASE" ]]; then
  if [[ -z "$DATE" ]]; then
    echo "Missing --date (or provide --base)" >&2
    usage
    exit 2
  fi
  BASE="product_list/$DATE"
fi

if [[ "$PHASE" != "analysis" && "$PHASE" != "scripts" && "$PHASE" != "all" ]]; then
  echo "Invalid --phase: $PHASE" >&2
  usage
  exit 2
fi

if [[ -z "$PRODUCT_IDS" ]]; then
  if [[ ! -f "$CSV" ]]; then
    echo "CSV not found: $CSV" >&2
    exit 2
  fi
  PRODUCT_IDS="$(tail -n +2 "$CSV" | tr -d '\r' | awk 'NF {print $1}' | xargs)"
fi

if [[ -z "$PRODUCT_IDS" ]]; then
  echo "No product IDs provided (empty --product-ids and empty CSV?)" >&2
  exit 2
fi

has_bad_preamble() {
  # Fails if file starts with Gemini/LLM meta chatter instead of Markdown.
  local file="$1"
  head -n 8 "$file" | grep -Eqi '^(i will|i can|i am unable|loaded cached credentials|server |```|due to technical limitations|the provided image file path|i do not have access|unable to (access|see)|as a text-based ai)'
}

line_count() {
  local file="$1"
  wc -l <"$file" | tr -d ' '
}

fail=0

for pid in $PRODUCT_IDS; do
  echo ""
  echo "=== $pid ==="

  product_dir="$BASE/$pid"
  if [[ ! -d "$product_dir" ]]; then
    echo "❌ FAIL: product folder missing: $product_dir"
    fail=1
    continue
  fi

  tabcut_json="$product_dir/tabcut_data.json"
  fastmoss_json="$product_dir/fastmoss_data.json"

  if [[ ! -f "$tabcut_json" && ! -f "$fastmoss_json" ]]; then
    echo "❌ FAIL: missing tabcut_data.json and fastmoss_data.json"
    fail=1
  else
    [[ -f "$tabcut_json" ]] && echo "✅ tabcut_data.json"
    [[ -f "$fastmoss_json" ]] && echo "✅ fastmoss_data.json"
  fi

  if [[ -f "$tabcut_json" ]]; then
    if [[ -f "$product_dir/tabcut_data.md" ]]; then
      echo "✅ tabcut_data.md"
    else
      echo "❌ FAIL: tabcut_data.md missing"
      fail=1
    fi
  fi

  if [[ "$PHASE" == "analysis" || "$PHASE" == "all" ]]; then
    img_dir="$product_dir/product_images"
    img_count=0
    if [[ -d "$img_dir" ]]; then
      img_count="$(find "$img_dir" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "$img_count" -gt 0 ]]; then
        img_analysis="$img_dir/image_analysis.md"
        if [[ -f "$img_analysis" ]]; then
          lines="$(line_count "$img_analysis")"
          if has_bad_preamble "$img_analysis"; then
            echo "❌ FAIL: image_analysis.md has meta preamble (\"I will...\")"
            fail=1
          elif [[ "$lines" -ge "$IMAGE_MIN_LINES" ]]; then
            echo "✅ image_analysis.md ($lines lines)"
          else
            echo "❌ FAIL: image_analysis.md too short ($lines lines, need >= $IMAGE_MIN_LINES)"
            fail=1
          fi
        else
          echo "❌ FAIL: image_analysis.md missing (found $img_count images)"
          fail=1
        fi
      fi
    fi

    video_dir="$product_dir/ref_video"
    video_count=0
    if [[ -d "$video_dir" ]]; then
      video_count="$(find "$video_dir" -type f -name "*.mp4" 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "$video_count" -gt 0 ]]; then
        synthesis="$video_dir/video_synthesis.md"
        if [[ -f "$synthesis" ]]; then
          lines="$(line_count "$synthesis")"
          if has_bad_preamble "$synthesis"; then
            echo "❌ FAIL: video_synthesis.md has meta preamble (\"I will...\")"
            fail=1
          elif [[ "$lines" -ge "$SYNTHESIS_MIN_LINES" ]]; then
            echo "✅ video_synthesis.md ($lines lines)"
          else
            echo "❌ FAIL: video_synthesis.md too short ($lines lines, need >= $SYNTHESIS_MIN_LINES)"
            fail=1
          fi
        else
          echo "❌ FAIL: video_synthesis.md missing (found $video_count videos)"
          fail=1
        fi

        analysis_count="$(find "$video_dir" -type f -name "video_*_analysis.md" 2>/dev/null | wc -l | tr -d ' ')"
        if [[ "$analysis_count" -lt "$video_count" ]]; then
          echo "❌ FAIL: video analyses incomplete ($analysis_count/$video_count)"
          fail=1
        else
          echo "✅ video analyses ($analysis_count/$video_count)"
        fi
      fi
    fi

    # If a product has no usable assets, the workflow is blocked.
    if [[ "$img_count" -eq 0 && "$video_count" -eq 0 ]]; then
      echo "❌ FAIL: no images and no videos found (blocked)"
      fail=1
    fi
  fi

  if [[ "$PHASE" == "scripts" || "$PHASE" == "all" ]]; then
    scripts_dir="$product_dir/scripts"
    if [[ -d "$scripts_dir" ]]; then
      md_count="$(find "$scripts_dir" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "$md_count" -lt 4 ]]; then
        echo "❌ FAIL: scripts/*.md count too low ($md_count, need >= 4 incl. Campaign_Summary.md)"
        fail=1
      else
        echo "✅ scripts md count ($md_count)"
      fi

      if [[ ! -f "$scripts_dir/Campaign_Summary.md" ]]; then
        echo "❌ FAIL: Campaign_Summary.md missing"
        fail=1
      else
        echo "✅ Campaign_Summary.md"
      fi

      for script in "$scripts_dir"/*.md; do
        [[ -e "$script" ]] || continue
        [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
        if ! head -n 1 "$script" | grep -q '^---$'; then
          echo "❌ FAIL: script missing YAML frontmatter: $(basename "$script")"
          fail=1
          break
        fi
        if ! grep -q '^## Scripts' "$script" || ! grep -q '^## Voiceover' "$script"; then
          echo "❌ FAIL: script missing required sections: $(basename "$script")"
          fail=1
          break
        fi
      done
    else
      echo "❌ FAIL: scripts/ folder missing"
      fail=1
    fi
  fi
done

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "=== GATE RESULT: PASS ==="
  exit 0
else
  echo "=== GATE RESULT: FAIL ==="
  exit 1
fi
