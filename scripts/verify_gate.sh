#!/usr/bin/env bash
set -euo pipefail

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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
  --phase analysis|scripts|index|all What to verify (default: all)
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
  BASE="$REPO_ROOT/product_list/$DATE"
fi

# Resolve BASE to absolute path if it's relative
if [[ ! "$BASE" = /* ]]; then
  BASE="$REPO_ROOT/$BASE"
fi

if [[ "$PHASE" != "analysis" && "$PHASE" != "scripts" && "$PHASE" != "index" && "$PHASE" != "all" ]]; then
  echo "Invalid --phase: $PHASE" >&2
  usage
  exit 2
fi

if [[ -z "$PRODUCT_IDS" ]]; then
  # Resolve CSV path relative to repo root if it's relative
  if [[ ! "$CSV" = /* ]]; then
    CSV="$REPO_ROOT/$CSV"
  fi
  
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

  tabcut_md="$product_dir/tabcut_data.md"
  fastmoss_md="$product_dir/fastmoss_data.md"

  if [[ ! -f "$tabcut_md" && ! -f "$fastmoss_md" ]]; then
    echo "❌ FAIL: missing tabcut_data.md and fastmoss_data.md"
    fail=1
  else
    [[ -f "$tabcut_md" ]] && echo "✅ tabcut_data.md"
    [[ -f "$fastmoss_md" ]] && echo "✅ fastmoss_data.md"
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

    # Phase 2: Quality Standards (bilingual coverage, compliance)
    echo ""
    echo "--- Quality Standards ---"

    # Bilingual coverage validation
    if [[ -f "$img_dir/image_analysis.md" ]]; then
      if python3 "$SCRIPT_DIR/validate_bilingual_coverage.py" "$img_dir/image_analysis.md" >/dev/null 2>&1; then
        echo "✅ image_analysis.md bilingual coverage"
      else
        echo "⚠️ WARN: image_analysis.md bilingual coverage below standards"
      fi
    fi

    if [[ -f "$video_dir/video_synthesis.md" ]]; then
      if python3 "$SCRIPT_DIR/validate_bilingual_coverage.py" "$video_dir/video_synthesis.md" >/dev/null 2>&1; then
        echo "✅ video_synthesis.md bilingual coverage"
      else
        echo "❌ FAIL: video_synthesis.md bilingual coverage below standards"
        fail=1
      fi
    fi

    # Compliance flags validation
    if [[ -f "$video_dir/video_synthesis.md" ]]; then
      if python3 "$SCRIPT_DIR/validate_compliance_flags.py" "$video_dir/video_synthesis.md" >/dev/null 2>&1; then
        echo "✅ video_synthesis.md compliance flags"
      else
        echo "❌ FAIL: video_synthesis.md has compliance violations"
        fail=1
      fi
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

      # Phase 2: Quality Standards for scripts
      echo ""
      echo "--- Script Quality Standards ---"

      # Compliance check for scripts (no risky claims)
      script_compliance_fail=0
      for script in "$scripts_dir"/*.md; do
        [[ -e "$script" ]] || continue
        [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
        if ! python3 "$SCRIPT_DIR/validate_compliance_flags.py" "$script" >/dev/null 2>&1; then
          echo "❌ FAIL: $(basename "$script") has compliance violations"
          fail=1
          script_compliance_fail=1
          break
        fi
      done
      [[ "$script_compliance_fail" -eq 0 ]] && echo "✅ All scripts: compliance clean"

      # ElevenLabs cues validation
      script_cues_fail=0
      for script in "$scripts_dir"/*.md; do
        [[ -e "$script" ]] || continue
        [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
        if ! python3 "$SCRIPT_DIR/validate_elevenlabs_cues.py" "$script" >/dev/null 2>&1; then
          echo "❌ FAIL: $(basename "$script") ElevenLabs cues below standards"
          fail=1
          script_cues_fail=1
          break
        fi
      done
      [[ "$script_cues_fail" -eq 0 ]] && echo "✅ All scripts: ElevenLabs cues quality"

    else
      echo "❌ FAIL: scripts/ folder missing"
      fail=1
    fi
  fi

  # Phase 3: Product Index (only check if scripts passed)
  if [[ "$PHASE" == "index" || "$PHASE" == "all" ]]; then
    echo ""
    echo "--- Product Index Check ---"

    # Only require index if scripts gate passed
    scripts_passed=true
    
    # Check if scripts gate would pass
    if [[ -d "$scripts_dir" ]]; then
      md_count="$(find "$scripts_dir" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "$md_count" -lt 4 ]] || [[ ! -f "$scripts_dir/Campaign_Summary.md" ]]; then
        scripts_passed=false
      fi
    else
      scripts_passed=false
    fi

    if [[ "$scripts_passed" == "true" ]]; then
      # Scripts passed, so index is required
      index_file="$product_dir/product_index.md"
      
      if [[ ! -f "$index_file" ]]; then
        echo "❌ FAIL: product_index.md missing (scripts complete, index required)"
        fail=1
      else
        # Check basic structure (YAML frontmatter)
        if ! head -n 1 "$index_file" | grep -q '^---$'; then
          echo "❌ FAIL: product_index.md missing YAML frontmatter"
          fail=1
        else
          # Optional: check product_id matches
          yaml_pid=$(grep -m 1 '^product_id:' "$index_file" | sed 's/product_id: *"\(.*\)"/\1/')
          if [[ -n "$yaml_pid" && "$yaml_pid" != "$pid" ]]; then
            echo "❌ FAIL: product_index.md product_id mismatch (expected $pid, got $yaml_pid)"
            fail=1
          else
            echo "✅ product_index.md exists and valid"
          fi
        fi
      fi
    else
      # Scripts incomplete, index not required
      if [[ -f "$product_dir/product_index.md" ]]; then
        echo "ℹ️  product_index.md exists (scripts incomplete, not enforced)"
      else
        echo "⊘ product_index.md not required (scripts incomplete)"
      fi
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
