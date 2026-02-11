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
            bb_peak_ts = bb_peak_val = bb_lowest_ts = bb_lowest_val = None
    else:
        bb_min = bb_max = bb_start = bb_end = bb_delta = None
        bb_peak_ts = bb_peak_val = bb_lowest_ts = bb_lowest_val = None
    
    # Build 30-minute timeline
    timeline_30m = []
    if event_start_ms:
        # Merge stress and bb series by timestamp
        stress_dict = {ts: val for ts, val in stress_values}
        bb_dict = {entry[0]: entry[2] for entry in bb_values if len(entry) > 2}
        
        # Get all unique timestamps
        all_ts = sorted(set(stress_dict.keys()) | set(bb_dict.keys()))
        
        # Group by 30-minute buckets
        buckets = {}
        for ts in all_ts:
            offset_min = (ts - event_start_ms) // 60000
            bucket = (offset_min // 30) * 30
            
            if bucket not in buckets:
                buckets[bucket] = {}
            
            if ts in bb_dict:
                buckets[bucket]['bb'] = bb_dict[ts]
            if ts in stress_dict:
                buckets[bucket]['stress'] = stress_dict[ts]
        
        # Convert to sorted list
        timeline_30m = [[offset, values] for offset, values in sorted(buckets.items())]
    
    return {
        'event': {
            'type': event.get('event_type'),
            'start_gmt': event_start_str,
            'timezone_offset_min': timezone_offset_min,
            'duration_s': duration_s,
            'impact': event.get('body_battery_impact'),
            'feedback_type': event.get('feedback_type'),
            'short_feedback': event.get('short_feedback')
        },
        'activity': {
            'id': data.get('activity_id'),
            'type': data.get('activity_type'),
            'name': data.get('activity_name')
        },
        'avg_stress': round(data.get('average_stress'), 2) if data.get('average_stress') is not None else None,
        'stress_series_summary': {
            'samples_count': stress_samples,
            'missing_count': stress_missing,
            'avg': stress_avg,
            'p95': stress_p95,
            'min': stress_min,
            'max': stress_max,
            'peak': {
                'ts': stress_peak_ts,
                'value': stress_peak_val
            }
        },
        'body_battery_series_summary': {
            'samples_count': bb_samples,
            'min': bb_min,
            'max': bb_max,
            'start_value': bb_start,
            'end_value': bb_end,
            'delta': bb_delta,
            'peak': {
                'ts': bb_peak_ts,
                'value': bb_max
            },
            'lowest': {
                'ts': bb_lowest_ts,
                'value': bb_min
            }
        },
        'timeline_30m': timeline_30m
    }


def slim_body_battery_list(items):
    """Convert list of BodyBatteryData to compact analysis-ready dicts."""
    return [slim_body_battery_item(item) for item in items]
