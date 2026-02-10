#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import CHATGPT_URL, DELAY_MS, FINDER_WAIT_MS, UPLOAD_WAIT_MS, PROMPT_MORNING
from upload_utils import upload_to_chatgpt


def main():
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "results" / "morning_data.json"
    upload_to_chatgpt(file_path, PROMPT_MORNING, CHATGPT_URL, DELAY_MS, FINDER_WAIT_MS, UPLOAD_WAIT_MS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
