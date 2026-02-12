def percentile(data, p):
    """Calculate percentile without numpy using linear interpolation."""
    if not data:
        return None
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def slim_body_battery_item(item):
    """Convert BodyBatteryData to compact analysis-ready dict."""
    from config import HIGH_STRESS_THRESHOLD
    
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    # Extract event data
    event = data.get('event', {})
    if not isinstance(event, dict):
        event = event.dict() if hasattr(event, 'dict') else vars(event) if hasattr(event, '__dict__') else {}
    
    # Format event start time
    event_start_gmt = event.get('event_start_time_gmt')
    if event_start_gmt:
        if hasattr(event_start_gmt, 'replace'):
            event_start_str = event_start_gmt.replace(microsecond=0).isoformat()
            event_start_ms = int(event_start_gmt.timestamp() * 1000)
        else:
            event_start_str = str(event_start_gmt)
            event_start_ms = None
    else:
        event_start_str = None
        event_start_ms = None
    
    # Convert timezone offset and duration
    timezone_offset_ms = event.get('timezone_offset', 0)
    timezone_offset_min = timezone_offset_ms // 60000 if timezone_offset_ms else None
    
    duration_ms = event.get('duration_in_milliseconds', 0)
    duration_s = int(duration_ms / 1000) if duration_ms else None
    
    # Extract stress series
    stress_values = data.get('stress_values_array', [])
    stress_samples = len(stress_values)
    valid_stress = [(ts, val) for ts, val in stress_values if val is not None]
    stress_missing = stress_samples - len(valid_stress)
    
    if valid_stress:
        stress_vals = [val for _, val in valid_stress]
        stress_avg = round(sum(stress_vals) / len(stress_vals), 2)
        stress_p95 = round(percentile(stress_vals, 0.95), 2) if percentile(stress_vals, 0.95) is not None else None
        stress_min = min(stress_vals)
        stress_max = max(stress_vals)
        stress_peak_ts, stress_peak_val = next((ts, val) for ts, val in valid_stress if val == stress_max)
    else:
        stress_avg = stress_p95 = stress_min = stress_max = None
        stress_peak_ts = stress_peak_val = None
    
    # Extract body battery series
    bb_values = data.get('body_battery_values_array', [])
    bb_samples = len(bb_values)
    
    if bb_values:
        # Extract bb values (index 2 in each entry)
        bb_vals = [entry[2] for entry in bb_values if len(entry) > 2 and entry[2] is not None]
        
        if bb_vals:
            bb_min = min(bb_vals)
            bb_max = max(bb_vals)
            bb_start = bb_vals[0]
            bb_end = bb_vals[-1]
            bb_delta = bb_end - bb_start
            
            # Find peak and lowest
            bb_peak_idx = bb_vals.index(bb_max)
            bb_peak_ts = bb_values[bb_peak_idx][0]
            
            bb_lowest_idx = bb_vals.index(bb_min)
            bb_lowest_ts = bb_values[bb_lowest_idx][0]
        else:
            bb_min = bb_max = bb_start = bb_end = bb_delta = None
            bb_peak_ts = bb_lowest_ts = None
    else:
        bb_min = bb_max = bb_start = bb_end = bb_delta = None
        bb_peak_ts = bb_lowest_ts = None
    
    # Build timeline (full if stress, 30m buckets otherwise)
    timeline_stress_30m = []
    if event_start_ms:
        stress_dict = {ts: val for ts, val in stress_values}
        bb_dict = {entry[0]: entry[2] for entry in bb_values if len(entry) > 2}
        all_ts = sorted(set(stress_dict.keys()) | set(bb_dict.keys()))
        
        stress_vals_in_event = [val for val in stress_dict.values() if val is not None]
        max_stress = max(stress_vals_in_event) if stress_vals_in_event else 0
        has_high_stress = max_stress > HIGH_STRESS_THRESHOLD
        
        if has_high_stress:
            # Include all timestamps when stress exists
            for ts in all_ts:
                offset_min = (ts - event_start_ms) // 60000
                values = {}
                if ts in bb_dict:
                    values['bb'] = bb_dict[ts]
                if ts in stress_dict:
                    values['stress'] = stress_dict[ts]
                timeline_stress_30m.append([offset_min, values])
        else:
            # Use 30-minute buckets when no high stress
            buckets = {}
            for ts in all_ts:
                offset_min = (ts - event_start_ms) // 60000
                bucket = (offset_min // 30) * 30
                if bucket not in buckets:
                    buckets[bucket] = {}
                if ts in bb_dict:
                    buckets[bucket]['bb'] = bb_dict[ts]
                if ts in stress_dict and stress_dict[ts] is not None:
                    buckets[bucket]['stress'] = stress_dict[ts]
            timeline_stress_30m = [[offset, values] for offset, values in sorted(buckets.items())]
    
    # Build activity dict without nulls
    activity_dict = {}
    if data.get('activity_id') is not None:
        activity_dict['id'] = data.get('activity_id')
    if data.get('activity_type') is not None:
        activity_dict['type'] = data.get('activity_type')
    if data.get('activity_name') is not None:
        activity_dict['name'] = data.get('activity_name')
    
    # Build stress peak dict
    stress_peak = {}
    if stress_peak_ts is not None:
        stress_peak['ts'] = stress_peak_ts
    if stress_peak_val is not None:
        stress_peak['value'] = stress_peak_val
    
    # Build body battery peak/lowest dicts
    bb_peak = {}
    if bb_peak_ts is not None:
        bb_peak['ts'] = bb_peak_ts
    if bb_max is not None:
        bb_peak['value'] = bb_max
    
    bb_lowest = {}
    if bb_lowest_ts is not None:
        bb_lowest['ts'] = bb_lowest_ts
    if bb_min is not None:
        bb_lowest['value'] = bb_min
    
    # Build stress series summary without nulls
    stress_summary = {'samples_count': stress_samples, 'missing_count': stress_missing}
    if stress_avg is not None:
        stress_summary['avg'] = stress_avg
    if stress_p95 is not None:
        stress_summary['p95'] = stress_p95
    if stress_min is not None:
        stress_summary['min'] = stress_min
    if stress_max is not None:
        stress_summary['max'] = stress_max
    if stress_peak:
        stress_summary['peak'] = stress_peak
    
    # Build body battery series summary without nulls
    bb_summary = {'samples_count': bb_samples}
    if bb_min is not None:
        bb_summary['min'] = bb_min
    if bb_max is not None:
        bb_summary['max'] = bb_max
    if bb_start is not None:
        bb_summary['start_value'] = bb_start
    if bb_end is not None:
        bb_summary['end_value'] = bb_end
    if bb_delta is not None:
        bb_summary['delta'] = bb_delta
    if bb_peak:
        bb_summary['peak'] = bb_peak
    if bb_lowest:
        bb_summary['lowest'] = bb_lowest
    
    # Build event dict without nulls
    event_dict = {}
    if event.get('event_type') is not None:
        event_dict['type'] = event.get('event_type')
    if event_start_str is not None:
        event_dict['start_gmt'] = event_start_str
    if timezone_offset_min is not None:
        event_dict['timezone_offset_min'] = timezone_offset_min
    if duration_s is not None:
        event_dict['duration_s'] = duration_s
    if event.get('body_battery_impact') is not None:
        event_dict['impact'] = event.get('body_battery_impact')
    if event.get('feedback_type') is not None:
        event_dict['feedback_type'] = event.get('feedback_type')
    if event.get('short_feedback') is not None:
        event_dict['short_feedback'] = event.get('short_feedback')
    
    result = {
        'event': event_dict,
        'stress_series_summary': stress_summary,
        'body_battery_series_summary': bb_summary,
        'timeline_stress_30m': timeline_stress_30m
    }
    
    # Add optional fields
    if activity_dict:
        result['activity'] = activity_dict
    
    avg_stress_val = data.get('average_stress')
    if avg_stress_val is not None:
        result['avg_stress'] = round(avg_stress_val, 2)
    
    return result


def slim_body_battery_list(items):
    """Convert list of BodyBatteryData to compact analysis-ready dicts."""
    return [slim_body_battery_item(item) for item in items]
