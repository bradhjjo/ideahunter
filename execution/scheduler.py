#!/usr/bin/env python3
"""
Scheduler script.
Runs the main workflow every day at a configured time.
"""

import schedule
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# Load env vars from .env if present (not required in CI environments)
try:
    load_dotenv()
except:
    pass


def run_daily_workflow():
    """Execute the daily pipeline."""
    print(f"\n{'='*60}")
    print(f"💡 Running IdeaHunter Daily Workflow")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")

    try:
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print("\n✅ Daily workflow completed successfully")
        else:
            print(f"\n❌ Daily workflow failed with exit code {result.returncode}")

    except Exception as e:
        print(f"\n❌ Error running daily workflow: {e}")


def main():
    """Start the scheduler loop."""
    # Set SCHEDULE_TIME in .env to override, e.g. SCHEDULE_TIME=08:30
    schedule_time = os.getenv('SCHEDULE_TIME', '07:00')

    print("🤖 IdeaHunter Scheduler Started")
    print(f"📅 Scheduled to run daily at {schedule_time}")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPress Ctrl+C to stop the scheduler\n")

    schedule.every().day.at(schedule_time).do(run_daily_workflow)

    # Optional: pass --test to run immediately once on startup
    if '--test' in sys.argv:
        print("🧪 Test mode: running workflow immediately...\n")
        run_daily_workflow()

    # Scheduler loop — checks every 60 seconds
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
