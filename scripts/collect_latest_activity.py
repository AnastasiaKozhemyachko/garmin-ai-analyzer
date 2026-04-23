#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import GARTH_DIR, RESULTS_DIR
from collection_utils import authenticate
import garth
from detailed_activity_slimmer import slim_detailed_activity


def main():
    try:
        authenticate(GARTH_DIR)
        RESULTS_DIR.mkdir(exist_ok=True)
        
        print("Collecting latest activity...")
        activities = garth.Activity.list(limit=1)
        
        if not activities or len(activities) == 0:
            print("⚠️  No activities found")
            sys.exit(0)
        
        latest_activity = slim_detailed_activity(activities[0])
        
        # Try to get fitness activity data (coaching info)
        try:
            today = date.today().isoformat()
            fitness_activities = garth.FitnessActivity.list(today, days=7)
            activity_id = latest_activity.get('activity_id')
            
            # Find matching fitness activity
            for fa in fitness_activities:
                if fa.activity_id == activity_id:
                    coaching_data = {}
                    if fa.workout_type:
                        coaching_data['workout_type'] = fa.workout_type
                    if fa.adaptive_coaching_workout_status:
                        coaching_data['coaching_status'] = fa.adaptive_coaching_workout_status
                    if fa.workout_group_enumerator:
                        coaching_data['workout_group'] = fa.workout_group_enumerator
                    if coaching_data:
                        latest_activity['coaching'] = coaching_data
                    break
        except Exception as e:
            print(f"⚠️  Could not fetch coaching data: {e}")
        
        output_file = RESULTS_DIR / "latest_activity.json"
        with open(output_file, "w") as f:
            json.dump(latest_activity, f, indent=2, default=str)
        
        print(f"✅ Latest activity saved to {output_file}")
        print(f"   Activity: {latest_activity.get('activity_name', 'N/A')}")
        print(f"   Type: {latest_activity.get('type_key', 'N/A')}")
        print(f"   Date: {latest_activity.get('start_time_local', 'N/A')}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
