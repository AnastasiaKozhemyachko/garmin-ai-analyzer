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
from daily_stress_slimmer import slim_daily_stress_list
from daily_steps_slimmer import slim_daily_steps_list
from daily_summary_slimmer import slim_daily_summary_list
from training_status_slimmer import slim_training_status_list
from garmin_scores_slimmer import slim_garmin_scores_list
from weight_data_slimmer import slim_weight_data_list

# Registry: data_type_name → slimmer function
SLIMMER_REGISTRY = {
    'daily_sleep_data': slim_daily_sleep_data_list,
    'daily_hrv': slim_daily_hrv_list,
    'daily_heart_rate': slim_daily_heart_rate_list,
    'training_readiness_data': slim_training_readiness_list,
    'activity': slim_activity_list,
    'body_battery_data': slim_body_battery_list,
    'daily_stress': slim_daily_stress_list,
    'daily_steps': slim_daily_steps_list,
    'daily_summary': slim_daily_summary_list,
    'daily_training_status': slim_training_status_list,
    'garmin_scores_data': slim_garmin_scores_list,
    'weight_data': slim_weight_data_list,
}


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
    """Collect Garmin data with robust error handling."""
    results_dir.mkdir(exist_ok=True)
    today = date.today().isoformat()
    all_data = {}
    
    for item in data_types:
        name, class_name = item[0], item[1]
        days = item[2] if len(item) > 2 else days_to_collect
        
        data = _fetch_and_slim(name, class_name, days, today)
        
        if data:
            all_data[name] = data
            print(f"✅ {name} ({days}d)")
        else:
            print(f"⚠️  {name}: No data available")
    
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\n✅ Data saved to {output_file}")


# Data types that return only 1 entry from .list() regardless of days parameter.
# These always need day-by-day collection to get historical data.
DAY_BY_DAY_TYPES = {'daily_training_status'}


def _fetch_and_slim(name, class_name, days, today):
    """Fetch data from Garmin and run through slimmer. Returns slimmed data or None."""
    from datetime import timedelta
    
    # Some types always need day-by-day fetching
    if name in DAY_BY_DAY_TYPES:
        collected = _fetch_day_by_day(name, class_name, days, today)
        if collected:
            return collected

    # Try primary fetch
    try:
        data_class = getattr(garth, class_name)
        if class_name == "Activity":
            raw = data_class.list(limit=days)
        else:
            raw = data_class.list(today, days)

        # If we got much fewer results than expected, try day-by-day
        if raw and isinstance(raw, list) and len(raw) < max(2, days // 3):
            day_by_day = _fetch_day_by_day(name, class_name, days, today)
            if day_by_day and isinstance(day_by_day, list) and len(day_by_day) > len(raw):
                return day_by_day

        return _slim_data(name, raw, days=days)
    except Exception as e:
        error_str = str(e)
    
    # Pydantic validation errors → try day-by-day collection
    if "validation error" in error_str.lower():
        collected = _fetch_day_by_day(name, class_name, days, today)
        if collected:
            return collected
    
    # Special fallback for garmin_scores_data via connectapi
    if name == "garmin_scores_data":
        try:
            raw_list = []
            for d_offset in range(days):
                d = (date.today() - timedelta(days=d_offset)).isoformat()
                try:
                    raw = garth.connectapi(f'/wellness-service/wellness/scores/daily/{d}/{d}')
                    if raw and isinstance(raw, list):
                        raw_list.extend(raw)
                    elif raw and isinstance(raw, dict):
                        raw_list.append(raw)
                except Exception:
                    pass
            if raw_list:
                slimmer = SLIMMER_REGISTRY.get(name)
                return slimmer(raw_list) if slimmer else raw_list
        except Exception:
            pass
    
    # Log the original error
    short_err = error_str.split('\n')[0][:100]
    print(f"⚠️  {name}: {short_err}")
    return None


def _fetch_day_by_day(name, class_name, days, today):
    """Fetch data one day at a time, skipping days with validation errors."""
    from datetime import timedelta
    
    data_class = getattr(garth, class_name, None)
    if not data_class:
        return None
    
    collected_raw = []
    for d_offset in range(days):
        d = (date.today() - timedelta(days=d_offset)).isoformat()
        try:
            day_data = data_class.list(d, 1)
            if day_data:
                collected_raw.extend(day_data)
        except Exception:
            pass  # Skip days with validation errors
    
    if collected_raw:
        return _slim_data(name, collected_raw, days=days)
    return None


def _slim_data(name, raw, days=None):
    """Run raw data through the appropriate slimmer."""
    if not raw or (isinstance(raw, list) and len(raw) == 0):
        return None
    
    slimmer = SLIMMER_REGISTRY.get(name)
    if slimmer:
        # For sleep data with many days, strip verbose timeline to save tokens
        if name == 'daily_sleep_data' and days and days > 5:
            data = slimmer(raw, include_timeline=False)
        else:
            data = slimmer(raw)
    else:
        # Generic conversion
        if hasattr(raw, '__iter__') and not isinstance(raw, (str, dict)):
            data = []
            for entry in raw:
                if hasattr(entry, 'model_dump'):
                    data.append(entry.model_dump())
                elif hasattr(entry, 'dict'):
                    data.append(entry.dict())
                elif hasattr(entry, '__dict__'):
                    data.append(vars(entry))
                else:
                    data.append(entry)
        elif hasattr(raw, 'model_dump'):
            data = raw.model_dump()
        elif hasattr(raw, 'dict'):
            data = raw.dict()
        else:
            data = raw
    
    if not data or (isinstance(data, list) and len(data) == 0):
        return None
    
    return data
