#!/usr/bin/env python3
import garth
import json
from datetime import date
from getpass import getpass
from garth.exc import GarthException
from sleep_data_slimmer import slim_daily_sleep_data_list
from hrv_slimmer import slim_daily_hrv_list
from heart_rate_slimmer import slim_daily_heart_rate_list
from training_readiness_slimmer import slim_training_readiness_list
from activity_slimmer import slim_activity_list
from body_battery_slimmer import slim_body_battery_list


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
            
            # Slim down data BEFORE converting to dict
            if name == "daily_sleep_data":
                data = slim_daily_sleep_data_list(data)
            elif name == "daily_hrv":
                data = slim_daily_hrv_list(data)
            elif name == "daily_heart_rate":
                data = slim_daily_heart_rate_list(data)
            elif name == "training_readiness_data":
                data = slim_training_readiness_list(data)
            elif name == "activity":
                data = slim_activity_list(data)
            elif name == "body_battery_data":
                data = slim_body_battery_list(data)
            else:
                # Convert to dict for proper JSON serialization
                if hasattr(data, '__iter__') and not isinstance(data, (str, dict)):
                    data = [item.dict() if hasattr(item, 'dict') else item for item in data]
                elif hasattr(data, 'dict'):
                    data = data.dict()
            
            all_data[name] = data
            print(f"✅ {name} ({days}d)")
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\n✅ Data saved to {output_file}")
