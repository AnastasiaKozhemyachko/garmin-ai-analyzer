#!/usr/bin/env python3
"""Activity Analysis Workflow: Collect latest activity and upload to ChatGPT."""
import sys
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "scripts"


def main():
    print("🏃 Activity Analysis Workflow")
    print("=" * 50)
    
    # Step 1: Collect latest activity
    print("\n📊 Step 1: Collecting latest activity data...")
    result = subprocess.run([sys.executable, str(SCRIPTS_DIR / "collect_latest_activity.py")])
    if result.returncode != 0:
        print("\n❌ Failed to collect activity data")
        sys.exit(1)
    
    # Step 2: Upload to ChatGPT
    print("\n📤 Step 2: Uploading to ChatGPT...")
    result = subprocess.run([sys.executable, str(SCRIPTS_DIR / "upload_activity.py")])
    if result.returncode != 0:
        print("\n❌ Failed to upload to ChatGPT")
        sys.exit(1)
    
    print("\n✅ Activity analysis complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
