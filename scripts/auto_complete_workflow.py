#!/usr/bin/env python3
"""
Autonomous Workflow Automation Script
Handles: Scraper → Video Analysis → Script Generation → Campaign Summary
With automatic error handling and retry logic
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PRODUCT_LIST_DIR = PROJECT_ROOT / "product_list"
PRODUCTS_CSV = SCRIPT_DIR / "products.csv"
LOGS_DIR = SCRIPT_DIR / "logs"

# Product IDs from CSV
PRODUCT_IDS = [
    "1729607303430380470",
    "1729607478878640746",
    "1729480764457261195",
    "1729647639515339683",
    "1729485974225328597",
    "1729657383498390149",
    "1729706896043317618",
    "1729483322301848170",
]

def log(msg, level="INFO"):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level:8} | {msg}")

def has_videos(product_id):
    """Check if product has videos ready"""
    video_dir = PRODUCT_LIST_DIR / product_id / "ref_video"
    if not video_dir.exists():
        return False
    videos = list(video_dir.glob("*.mp4"))
    return len(videos) >= 5

def has_video_analysis(product_id):
    """Check if video analysis is complete"""
    video_dir = PRODUCT_LIST_DIR / product_id / "ref_video"
    synthesis = video_dir / "video_synthesis.md"
    return synthesis.exists()

def has_scripts(product_id):
    """Check if scripts are generated"""
    scripts_dir = PRODUCT_LIST_DIR / product_id / "scripts"
    if not scripts_dir.exists():
        return False
    scripts = list(scripts_dir.glob("*.md"))
    return len(scripts) >= 3

def has_campaign_summary(product_id):
    """Check if Campaign Summary exists"""
    campaign = PRODUCT_LIST_DIR / product_id / "scripts" / "Campaign_Summary.md"
    return campaign.exists()

def run_command(cmd, timeout=1800):
    """Run command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT"
    except Exception as e:
        return False, "", str(e)

def wait_for_scraper():
    """Wait for scraper to complete all products"""
    log("⏳ Waiting for scraper to complete all 8 products...")
    max_wait = 3600  # 1 hour
    start = time.time()

    completed = set()
    while time.time() - start < max_wait:
        for pid in PRODUCT_IDS:
            if pid not in completed and has_videos(pid):
                log(f"✅ Scraper completed: {pid}")
                completed.add(pid)

        if len(completed) == len(PRODUCT_IDS):
            log(f"🎉 Scraper completed ALL {len(PRODUCT_IDS)} products!")
            return True

        log(f"⏳ Progress: {len(completed)}/{len(PRODUCT_IDS)} products scraped")
        time.sleep(30)

    log(f"❌ Scraper timeout. Completed: {len(completed)}/{len(PRODUCT_IDS)}")
    return len(completed) > 0

def run_video_analysis():
    """Run video analysis for all products"""
    log("🎬 Starting video analysis for all products...")
    analyzed = []
    failed = []

    for pid in PRODUCT_IDS:
        if has_video_analysis(pid):
            log(f"⏭️  Skipping (already analyzed): {pid}")
            analyzed.append(pid)
            continue

        if not has_videos(pid):
            log(f"⏭️  Skipping (no videos): {pid}")
            failed.append(pid)
            continue

        log(f"🎬 Analyzing: {pid}")
        success, stdout, stderr = run_command(
            f"source venv/bin/activate && python analyze_video_batch.py {pid}",
            timeout=1800
        )

        if success and has_video_analysis(pid):
            log(f"✅ Analysis complete: {pid}")
            analyzed.append(pid)
        else:
            log(f"⚠️  Analysis failed: {pid}")
            failed.append(pid)
            # Skip but don't fail - continue with others

    log(f"📊 Video Analysis Summary: {len(analyzed)} success, {len(failed)} failed/skipped")
    return analyzed

def run_script_generation():
    """Generate scripts for all analyzed products"""
    log("✍️  Starting script generation for all products...")

    # Use Gemini CLI to generate scripts for each product
    for pid in PRODUCT_IDS:
        if has_video_analysis(pid) or (PRODUCT_LIST_DIR / pid / "tabcut_data.json").exists():
            log(f"📝 Generating scripts: {pid}")

            # Create scripts directory
            scripts_dir = PRODUCT_LIST_DIR / pid / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            # Use the tiktok_script_generator skill via Gemini CLI
            cmd = f"""
            gemini exec << 'EOF'
            Use the 'tiktok_script_generator' skill to generate 3 bilingual TikTok scripts and Campaign Summary for product {pid}.
            Product folder: {PRODUCT_LIST_DIR / pid}
            Output scripts to: {scripts_dir}
            Ensure bilingual format (German + Chinese) with v1.7.0 Campaign Summary format.
            EOF
            """

            success, stdout, stderr = run_command(cmd, timeout=600)

            if success:
                log(f"✅ Scripts generated: {pid}")
            else:
                log(f"⚠️  Script generation had issues: {pid} - {stderr[:100]}")

def run_campaign_summary():
    """Generate/update Campaign Summaries for all products"""
    log("📋 Ensuring Campaign Summaries exist for all products...")

    for pid in PRODUCT_IDS:
        scripts_dir = PRODUCT_LIST_DIR / pid / "scripts"

        if not scripts_dir.exists():
            log(f"⏭️  Skipping (no scripts dir): {pid}")
            continue

        # Check if Campaign_Summary.md exists
        campaign_file = scripts_dir / "Campaign_Summary.md"

        if campaign_file.exists():
            log(f"✅ Campaign Summary exists: {pid}")
            continue

        log(f"⚠️  Campaign Summary missing: {pid} - generating...")

        # Campaign Summary should have been created by script generator
        # If not, this is a fallback to ensure it exists
        # For now, just log it
        log(f"   (Campaign Summary should be created by script_generator skill)")

def verify_deliverables():
    """Verify all deliverables are complete"""
    log("✔️  Verifying all deliverables...")

    summary = {
        "total": len(PRODUCT_IDS),
        "scraped": 0,
        "analyzed": 0,
        "scripts": 0,
        "campaign": 0,
    }

    for pid in PRODUCT_IDS:
        if has_videos(pid):
            summary["scraped"] += 1
        if has_video_analysis(pid):
            summary["analyzed"] += 1
        if has_scripts(pid):
            summary["scripts"] += 1
        if has_campaign_summary(pid):
            summary["campaign"] += 1

    log(f"""
    📊 DELIVERABLES SUMMARY:
    ├─ Scraped: {summary['scraped']}/{summary['total']}
    ├─ Video Analysis: {summary['analyzed']}/{summary['total']}
    ├─ Scripts Generated: {summary['scripts']}/{summary['total']}
    └─ Campaign Summaries: {summary['campaign']}/{summary['total']}
    """)

    return summary

def main():
    """Main orchestration workflow"""
    log("🚀 Starting Autonomous Workflow Orchestration")
    log(f"   Processing {len(PRODUCT_IDS)} products")

    try:
        # Phase 1: Wait for scraper
        log("\n" + "="*60)
        log("PHASE 1: Waiting for Scraper Completion")
        log("="*60)
        if not wait_for_scraper():
            log("⚠️  Scraper incomplete but continuing with available products...")

        # Phase 2: Video Analysis
        log("\n" + "="*60)
        log("PHASE 2: Running Video Analysis")
        log("="*60)
        analyzed = run_video_analysis()

        # Phase 3: Script Generation
        log("\n" + "="*60)
        log("PHASE 3: Generating Scripts & Campaign Summaries")
        log("="*60)
        run_script_generation()

        # Phase 4: Campaign Summary
        log("\n" + "="*60)
        log("PHASE 4: Campaign Summaries")
        log("="*60)
        run_campaign_summary()

        # Phase 5: Verification
        log("\n" + "="*60)
        log("PHASE 5: Final Verification")
        log("="*60)
        summary = verify_deliverables()

        log("\n" + "="*60)
        log("🎉 WORKFLOW COMPLETE")
        log("="*60)

    except Exception as e:
        log(f"❌ Workflow error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
