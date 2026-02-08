# Core Scripts Contract

This file locks the TikTok product workflow to the current maintained scripts.

## Mandatory Core Scripts

Use only these scripts for product workflow execution:

- `scripts/run_scraper.py` (Phase 1: scraping)
- `scripts/convert_json_to_md.py` (Phase 1 post-process)
- `scripts/analyze_video_batch.py` (Phase 2A: per-video analysis)
- `scripts/analyze_product_images.py` (Phase 2B: image analysis)
- `scripts/create_video_synthesis.py` (Phase 2C: synthesis)
- `scripts/verify_gate.sh` (quality gates)
- `scripts/generate_product_indices.py` (Phase 4 index generation)
- `scripts/validate_bilingual_coverage.py` (quality validator)
- `scripts/validate_compliance_flags.py` (quality validator)
- `scripts/validate_elevenlabs_cues.py` (quality validator)

## Execution Baseline

- Use system `python3` for all `scripts/*.py` commands.
- Do not rely on `venv` activation snippets in legacy examples.

## Deprecated / Removed Wrappers

Do not use these wrappers; they are removed or obsolete:

- `scripts/auto_complete_workflow.py`
- `scripts/complete_workflow_autonomous.sh`
- `scripts/e2e_workflow_samples.sh`
- `scripts/parallel_analysis.sh`
- `scripts/parallel_analysis_simple.sh`
- `scripts/test_optimization.sh`
- `scripts/test_scraper.py`
- `scripts/test_video_download.py`
- `scripts/test_no_auth.py`

## Data Availability Guardrail

If a product has no usable `top_videos[*].video_url` in `tabcut_data.json` and `fastmoss_data.json`:

- Mark video-dependent phases as blocked for that product.
- Skip `analyze_video_batch.py` and `create_video_synthesis.py` for that product.
- Continue with available phases (`convert_json_to_md.py`, image analysis if images exist).
