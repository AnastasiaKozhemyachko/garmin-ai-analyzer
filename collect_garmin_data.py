#!/usr/bin/env python3
import garth
import json
import sys
from datetime import date
from getpass import getpass
from garth.exc import GarthException
from config import GARTH_DIR, RESULTS_DIR, DATA_FILE, DAYS_TO_COLLECT, DATA_TYPES


def authenticate():
    """Authenticate with Garmin or resume existing session."""
    if GARTH_DIR.exists():
        try:
            garth.resume(str(GARTH_DIR))
            garth.client.username  # Test if session is valid
            print(f"✅ Resumed session as: {garth.client.username}")
            return
        except GarthException:
            print("⚠️  Session expired, logging in again...")
    
    email = input("Enter your Garmin email: ")
    password = getpass("Enter your Garmin password: ")
    garth.login(email, password)
    garth.save(str(GARTH_DIR))
    print(f"✅ Login successful as: {garth.client.username}")


def collect_data():
    """Collect Garmin data for the specified number of days."""
    RESULTS_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    all_data = {}
    
    for name, class_name in DATA_TYPES:
        try:
            data_class = getattr(garth, class_name)
            
            # Activity uses different parameters (limit/start instead of date/days)
            if class_name == "Activity":
                data = data_class.list(limit=100)
            else:
                data = data_class.list(today, DAYS_TO_COLLECT)
            
            all_data[name] = data
            print(f"✅ {name}")
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\n✅ Data saved to {DATA_FILE}")


def main():
    try:
        authenticate()
        collect_data()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
