#!/usr/bin/env python3
"""
Generate product_images/image_analysis.md using gemini-cli.

Supports both legacy layout:
  product_list/<product_id>/product_images
and dated batch layout:
  product_list/YYYYMMDD/<product_id>/product_images

This script captures stdout only (stderr often contains Gemini CLI meta logs).
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

    # Drop obvious meta/tool chatter lines anywhere.
    cleaned = []
    for line in lines:
        if any(line.startswith(p) for p in META_LINE_PREFIXES):
            continue
        cleaned.append(line)

    # Trim leading blank / meta-ish lines until first markdown header.
    # Prefer the required header if present.
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

    # Ensure required first line is present.
    while cleaned and cleaned[0].strip() == "":
        cleaned = cleaned[1:]

    if not cleaned or cleaned[0].strip() != required_first_line:
        cleaned = [required_first_line, ""] + cleaned

    return "\n".join(cleaned).rstrip() + "\n"


PROMPT_TEMPLATE = """You are analyzing TikTok Shop product images for a Germany audience campaign.

STRICT OUTPUT CONTRACT (MANDATORY):
- Output MUST be pure Markdown only. No preamble, no tool chatter, no "I will...", no "Loaded cached credentials".
- First line MUST be: "# Image Analysis | 图片分析"
- Use bilingual section headers: English | 中文
- Be extremely detailed and concrete. Use bullet points and tables.
- Minimum length: at least {min_lines} lines (not words). If you are short, expand with deeper observations, more examples, and more actionable filming ideas.

INLINE TRANSLATION RULE (MANDATORY):
- For every non-table bullet/paragraph you write, provide German first, then Chinese translation on the next line.
- Use this exact pattern:
  - DE: ...
    ZH: ...
- If something is not visible, write "DE: Unklar." then "ZH: 不清楚。"

LINE COUNT COMPLIANCE (MANDATORY):
- Include a section "## On-Screen Text Suggestions (DE) (80+ lines) | 屏幕文字建议（德语 80+行）" with at least 80 single-line German overlay texts (one per line).
- Include a section "## Shot List (25+) | 分镜清单（至少25条）" with at least 25 rows.

ANTI-GENERIC RULE (MANDATORY):
- Do NOT write generic templates.
- Every section must include concrete, image-grounded details.
- If a detail is not visible, write "Unclear" (do not invent).
- In sections 1–4, include at least 30 bullet points, and each bullet MUST cite evidence by mentioning the specific image filename(s) (e.g., `product_image_1.webp`).

CONTEXT:
- Target market: Germany (TikTok Shop DE)
- Goal: Market intelligence + creative direction for short-form ads

SOURCE OF TRUTH (MANDATORY):
- If `tabcut_data.md` or `tabcut_data.json` or `fastmoss_data.json` is attached, you MUST extract the product name from it and keep product identification consistent with it.
- Do NOT switch to a different product category.
- If an image seems inconsistent, mark that detail as "Unklar/不清楚" instead of changing the product.

TASK:
Analyze ALL provided images as a set. Focus on:
1) What exactly is the product (type, variant, bundle, materials)
2) Visible claims/labels/packaging text (quote German text exactly if present)
3) Trust signals (certifications, seals, ingredients, usage steps, before/after style claims)
4) Visual angles that will sell on TikTok (macro shots, textures, UI screens, accessories)
5) Competitive positioning (who would buy it, what pain it solves, why now)
6) Compliance (avoid medical/legal guarantees; flag risky claims if seen)
7) Filming plan ideas: at least 12 shot ideas with seconds + purpose
8) Editing overlays: suggested German on-screen text lines (short, punchy)
9) Objections + rebuttals (German audience)
10) Recommended 3 script angles derived from visuals

DELIVERABLE STRUCTURE (use this order):
1. Product Identification | 产品识别
2. What Each Image Shows (catalog) | 单张图片内容目录
3. Claims & Text (verbatim quotes) | 文案与标签（逐字引用）
4. Visual Selling Points | 视觉卖点
5. Variants, Bundle, Accessories | 规格/套装/配件
6. Usage & Demo Opportunities | 使用与演示机会
7. Trust & Proof Elements | 信任与证据元素
8. Risks / Compliance Notes | 风险与合规提醒
9. Target Audience Hypothesis (DE) | 受众推断（德国）
10. Creative Hooks From Visuals | 视觉钩子
11. Shot List (12+) | 分镜清单（至少12条）
12. On-Screen Text Suggestions (DE) | 屏幕文字建议（德语）
13. Angle Recommendations (3) | 三个脚本角度建议
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
    parser = argparse.ArgumentParser(description="Generate image_analysis.md for a product.")
    parser.add_argument("product_id", type=str, help="TikTok product ID")
    parser.add_argument("--base", type=str, default=None, help="Base folder containing product_id subfolders")
    parser.add_argument("--date", type=str, default=None, help="YYYYMMDD under product_list/ (sets base)")
    parser.add_argument("--min-lines", type=int, default=200, help="Minimum line count for output")
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
    images_dir = product_dir / "product_images"
    out_path = images_dir / "image_analysis.md"

    if not images_dir.exists():
        raise SystemExit(f"Missing images folder: {images_dir}")

    image_files = sorted(
        [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    )
    if not image_files:
        raise SystemExit(f"No images found in: {images_dir}")

    prompt = PROMPT_TEMPLATE.format(min_lines=args.min_lines)

    # Add product metadata as optional grounding context.
    context_files = []
    for name in ("tabcut_data.md", "tabcut_data.json", "fastmoss_data.json"):
        p = product_dir / name
        if p.exists():
            context_files.append(p)

    files_for_gemini = image_files + context_files

    available_images = "\n".join(f"- {p.name}" for p in image_files)
    prompt = (
        prompt
        + "\n\nAVAILABLE IMAGE FILES (MUST ONLY REFER TO THESE FILENAMES):\n"
        + available_images
        + "\n"
    )

    text = ""
    for attempt in range(1, args.attempts + 1):
        if attempt == 1:
            attempt_prompt = prompt
        else:
            attempt_prompt = (
                prompt
                + f"\n\nATTEMPT {attempt}: Your previous output was too short. Expand substantially until you reach at least {args.min_lines} lines. "
                  "Add more concrete observations, more DE overlay examples, and a bigger shot list if needed."
            )
        raw = run_gemini(
            files_for_gemini,
            attempt_prompt,
            timeout_s=args.timeout,
            models=[args.model_primary, args.model_fallback],
        )
        text = sanitize_markdown(raw, "# Image Analysis | 图片分析")
        if count_lines(text) >= args.min_lines:
            break

    if not text.strip():
        raise SystemExit("Gemini returned empty output.")

    lines = count_lines(text)
    if lines < args.min_lines:
        raise SystemExit(f"Output too short: {lines} lines (need >= {args.min_lines}).")

    images_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"✅ Wrote: {out_path} ({lines} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
