#!/usr/bin/env python3
"""
Main orchestration script.
Runs all pipeline steps in sequence (Layer 2).
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

TELEGRAM_STEP = "Send Telegram Message"


def run_step(step_name: str, script_path: str) -> bool:
    """Run an individual pipeline script as a subprocess."""
    print(f"\n{'='*60}")
    print(f"Step: {step_name}")
    print(f"{'='*60}")

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ {step_name} completed successfully")
            return True
        else:
            print(f"❌ {step_name} failed with exit code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ {step_name} failed with error: {e}")
        return False


def main():
    """Main workflow."""
    print("🚀 Starting IdeaHunter Daily Workflow")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Pipeline steps — add or remove sources here as needed
    steps = [
        ("Fetch AI News (RSS)",     os.path.join(script_dir, "fetch_news_rss.py")),
        ("Fetch AI Trends",         os.path.join(script_dir, "fetch_trends.py")),
        ("Analyze Ideas (LLM)",     os.path.join(script_dir, "analyze_ideas.py")),
        (TELEGRAM_STEP,             os.path.join(script_dir, "send_telegram_message.py")),
    ]

    results = []
    for step_name, script_path in steps:
        success = run_step(step_name, script_path)
        results.append((step_name, success))

        if not success and step_name != TELEGRAM_STEP:
            print(f"\n⚠️  Critical step '{step_name}' failed. Continuing anyway...")

    # Summary
    print(f"\n{'='*60}")
    print("📊 Workflow Summary")
    print(f"{'='*60}")

    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step_name}")

    all_success = all(success for _, success in results)

    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if all_success:
        print("🎉 All steps completed successfully!")
        return 0
    else:
        print("⚠️  Some steps failed. Check logs above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
