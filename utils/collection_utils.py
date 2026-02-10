#!/usr/bin/env python3
import garth
import json
from datetime import date
from getpass import getpass
from garth.exc import GarthException


def authenticate(garth_dir):
    """Authenticate with Garmin or resume existing session."""
    if garth_dir.exists():
        try:
            garth.resume(str(garth_dir))
            garth.client.username
            print(f"✅ Resumed session as: {garth.client.username}")
            return
        except GarthException:
            print("⚠️  Session expired, logging in again...")
    
    email = input("Enter your Garmin email: ")
    password = getpass("Enter your Garmin password: ")
    garth.login(email, password)
    garth.save(str(garth_dir))
    print(f"✅ Login successful as: {garth.client.username}")


def collect_data(data_types, output_file, results_dir, days_to_collect):
    """Collect Garmin data."""
    results_dir.mkdir(exist_ok=True)
    today = date.today().isoformat()
    all_data = {}
    
    for item in data_types:
        name, class_name = item[0], item[1]
        days = item[2] if len(item) > 2 else days_to_collect
        enabled = item[3] if len(item) > 3 else True
        
        if not enabled:
            continue
        
        try:
            data_class = getattr(garth, class_name)
            data = data_class.list(limit=10) if class_name == "Activity" else data_class.list(today, days)
            all_data[name] = data
            print(f"✅ {name} ({days}d)")
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\n✅ Data saved to {output_file}")
