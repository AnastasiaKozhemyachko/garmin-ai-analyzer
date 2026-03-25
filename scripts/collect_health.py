#!/usr/bin/env python3
"""Collect health data from Garmin."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import GARTH_DIR, RESULTS_DIR, DAYS_TO_COLLECT, DATA_TYPES_HEALTH
from collection_utils import authenticate, collect_data


def main():
    try:
        authenticate(GARTH_DIR)
        collect_data(DATA_TYPES_HEALTH, RESULTS_DIR / "health_data.json", RESULTS_DIR, DAYS_TO_COLLECT)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
