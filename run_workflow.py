#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from config import DATA_FILE


def run_script(script_name, *args):
    """Run a Python script with arguments."""
    cmd = [sys.executable, script_name, *args]
    subprocess.run(cmd, check=True, cwd=Path(__file__).parent)


def main():
    print("🏃 Starting Garmin workflow...\n")
    
    print("📊 Step 1: Collecting Garmin data...")
    try:
        run_script("collect_garmin_data.py")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to collect data: {e}")
        sys.exit(1)
    
    if not DATA_FILE.exists():
        print(f"\n❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    print(f"\n✅ Data collection complete!")
    
    print("\n📤 Step 2: Uploading to ChatGPT...")
    try:
        run_script("upload_to_chatgpt.py", str(DATA_FILE))
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to upload: {e}")
        sys.exit(1)
    
    print("\n✅ Workflow complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
