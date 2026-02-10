#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "utils"))
from config import RESULTS_DIR

DATA_FILE = RESULTS_DIR / "morning_data.json"
VENV_PYTHON = Path(__file__).parent / "venv" / "bin" / "python3"


def main():
    python_cmd = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    
    print("🌅 Starting morning workflow...\n")
    
    print("📊 Step 1: Collecting morning data...")
    try:
        subprocess.run([python_cmd, "scripts/collect_morning.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to collect data: {e}")
        sys.exit(1)
    
    if not DATA_FILE.exists():
        print(f"\n❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    print("\n📤 Step 2: Uploading to ChatGPT...")
    try:
        subprocess.run([python_cmd, "scripts/upload_morning.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to upload: {e}")
        sys.exit(1)
    
    print("\n✅ Morning workflow complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
