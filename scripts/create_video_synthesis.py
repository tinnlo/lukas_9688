#!/usr/bin/env python3
"""
Generate ref_video/video_synthesis.md from per-video analyses using gemini-cli.

Supports both legacy layout:
  product_list/<product_id>/ref_video/video_*_analysis.md
and dated batch layout:
  product_list/YYYYMMDD/<product_id>/ref_video/video_*_analysis.md
"""

import argparse
import subprocess
from pathlib import Path


META_LINE_PREFIXES = (
    "Loaded cached credentials.",
    "Server ",
)

DEFAULT_MODEL_PRIMARY = "gemini-3-pro-preview"
DEFAULT_MODEL_FALLBACK = "gemini-3-flash-preview"


def sanitize_markdown(text: str, required_first_line: str) -> str:
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        if any(line.startswith(p) for p in META_LINE_PREFIXES):
            continue
        cleaned.append(line)

    required_idx = None
    for i, line in enumerate(cleaned):
        if line.strip() == required_first_line:
            required_idx = i
            break

    if required_idx is not None:
        cleaned = cleaned[required_idx:]
    else:
        first_header_idx = None
        for i, line in enumerate(cleaned):
            if line.lstrip().startswith("#"):
                first_header_idx = i
                break
        if first_header_idx is not None:
            cleaned = cleaned[first_header_idx:]

    while cleaned and cleaned[0].strip() == "":
        cleaned = cleaned[1:]

    if not cleaned or cleaned[0].strip() != required_first_line:
        cleaned = [required_first_line, ""] + cleaned

    return "\n".join(cleaned).rstrip() + "\n"


PROMPT_TEMPLATE = """You are a TikTok performance strategist. Synthesize multiple TikTok ad analyses into a single actionable playbook.

STRICT OUTPUT CONTRACT (MANDATORY):
- Output MUST be pure Markdown only. No preamble, no tool chatter, no "I will...", no "Loaded cached credentials".
- First line MUST be: "# Video Synthesis | 视频综合"
- Use bilingual section headers: English | 中文
- Minimum length: at least {min_lines} lines. If short, expand with more examples, a fuller playbook, and clearer action steps.
- Do NOT invent product claims that are not supported by the provided analyses.

LINE COUNT COMPLIANCE (MANDATORY):
- Include a section "## German Copy Bank (80+ lines) | 德语文案库（80+行）" with at least 80 single-line German hooks/claims/CTAs (one per line).
- Include a hook library table with at least 25 rows.
- Include a replication checklist with at least 20 bullet items.

TARGET MARKET:
- Germany (TikTok Shop DE)

TASK:
Read all provided `video_*_analysis.md` files (and product JSON if provided) and produce a synthesis that covers:

1. Winning Hook Patterns | 爆款开场模式
2. Creative Formats & Structures | 创意结构与模板
3. Proof & Trust Mechanics | 证据与信任机制
4. Objection Handling | 异议处理
5. German Copy Bank (short lines) | 德语文案库（短句）
6. Visual Editing Playbook | 视觉剪辑打法
7. CTA Patterns & Timing | CTA 节奏与时机
8. Audience Segments | 受众细分
9. Replication Checklist (shooting + edit) | 复刻清单（拍摄+剪辑）
10. 3 Script Angles Recommended | 三个脚本角度
11. Risk / Compliance Notes | 风险与合规提醒

Include tables where useful:
- Hook library table (Pattern / Example DE line / When to use / Risk)
- 3 recommended scripts table (Angle / Hook / Proof / CTA / Visual signature)
"""


def _should_fallback(stderr: str) -> bool:
    s = (stderr or "").lower()
    return (
        "exhausted your capacity" in s
        or "quota will reset" in s
        or "resource_exhausted" in s
        or "rate limit" in s
        or "429" in s
    )


def run_gemini(files: list[Path], prompt: str, timeout_s: int, models: list[str]) -> str:
    for i, model in enumerate(models):
        cmd = ["gemini", "-o", "text", "-m", model]
        cmd.extend([str(p) for p in files])
        cmd.append(prompt)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0 and (result.stdout or "").strip():
            return result.stdout
        if i < len(models) - 1 and _should_fallback(result.stderr):
            continue
    return result.stdout or ""


def count_lines(text: str) -> int:
    return len(text.splitlines())


def main() -> int:
    parser = argparse.ArgumentParser(description="Create video_synthesis.md from video analyses.")
    parser.add_argument("product_id", type=str, help="TikTok product ID")
    parser.add_argument("--base", type=str, default=None, help="Base folder containing product_id subfolders")
    parser.add_argument("--date", type=str, default=None, help="YYYYMMDD under product_list/ (sets base)")
    parser.add_argument("--min-lines", type=int, default=150, help="Minimum line count for synthesis")
    parser.add_argument("--timeout", type=int, default=900, help="Gemini timeout seconds per attempt")
    parser.add_argument("--attempts", type=int, default=3, help="Max attempts to reach minimum lines")
    parser.add_argument("--model-primary", type=str, default=DEFAULT_MODEL_PRIMARY, help="Primary Gemini model id")
    parser.add_argument("--model-fallback", type=str, default=DEFAULT_MODEL_FALLBACK, help="Fallback Gemini model id (used if quota/capacity hit)")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    if args.base:
        base = Path(args.base)
    elif args.date:
        base = project_root / "product_list" / args.date
    else:
        base = project_root / "product_list"

    product_dir = base / args.product_id
    video_dir = product_dir / "ref_video"
    out_path = video_dir / "video_synthesis.md"

    if not video_dir.exists():
        raise SystemExit(f"Missing ref_video folder: {video_dir}")

    analysis_files = sorted(video_dir.glob("video_*_analysis.md"))
    if not analysis_files:
        raise SystemExit(f"No video_*_analysis.md files found in: {video_dir}")

    json_files = []
    for name in ("tabcut_data.json", "fastmoss_data.json"):
        p = product_dir / name
        if p.exists():
            json_files.append(p)

    files = analysis_files + json_files
    prompt = PROMPT_TEMPLATE.format(min_lines=args.min_lines)

    text = ""
    for attempt in range(1, args.attempts + 1):
        if attempt == 1:
            attempt_prompt = prompt
        else:
            attempt_prompt = (
                prompt
                + f"\n\nATTEMPT {attempt}: Your previous output was too short. Expand substantially until you reach at least {args.min_lines} lines. "
                  "Add more concrete DE copy lines, a fuller hook library table, and an expanded replication checklist."
            )
        raw = run_gemini(
            files,
            attempt_prompt,
            timeout_s=args.timeout,
            models=[args.model_primary, args.model_fallback],
        )
        text = sanitize_markdown(raw, "# Video Synthesis | 视频综合")
        if count_lines(text) >= args.min_lines:
            break

    if not text.strip():
        raise SystemExit("Gemini returned empty output.")

    lines = count_lines(text)
    if lines < args.min_lines:
        raise SystemExit(f"Output too short: {lines} lines (need >= {args.min_lines}).")

    out_path.write_text(text, encoding="utf-8")
    print(f"✅ Wrote: {out_path} ({lines} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
