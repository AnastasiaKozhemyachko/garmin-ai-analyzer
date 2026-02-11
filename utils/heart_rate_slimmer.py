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


def slim_daily_heart_rate(item):
    """Convert DailyHeartRate to compact analysis-ready dict with series aggregation."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    # Extract heart rate series
    heart_rate_values = data.get('heart_rate_values', [])
    
    # Aggregate series
    samples_count = len(heart_rate_values)
    valid_hrs = [(ts, hr) for ts, hr in heart_rate_values if hr is not None]
    missing_count = samples_count - len(valid_hrs)
    
    if valid_hrs:
        hrs_only = [hr for _, hr in valid_hrs]
        avg_hr = round(sum(hrs_only) / len(hrs_only), 2)
        p95_hr = round(percentile(hrs_only, 0.95), 2) if percentile(hrs_only, 0.95) is not None else None
        min_hr = min(hrs_only)
        max_hr = max(hrs_only)
        
        # Find peak (first occurrence of max)
        peak_ts, peak_hr = next((ts, hr) for ts, hr in valid_hrs if hr == max_hr)
    else:
        avg_hr = p95_hr = min_hr = max_hr = None
        peak_ts = peak_hr = None
    
    # Format timestamps
    def format_timestamp(ts):
        if ts is None:
            return None
        if hasattr(ts, 'replace'):
            return ts.replace(microsecond=0).isoformat()
        return str(ts)
    
    return {
        'calendar_date': str(data.get('calendar_date')) if data.get('calendar_date') else None,
        'start_timestamp_gmt': format_timestamp(data.get('start_timestamp_gmt')),
        'end_timestamp_gmt': format_timestamp(data.get('end_timestamp_gmt')),
        'resting_heart_rate': data.get('resting_heart_rate'),
        'last_seven_days_avg_resting_heart_rate': data.get('last_seven_days_avg_resting_heart_rate'),
        'min_heart_rate': data.get('min_heart_rate'),
        'max_heart_rate': data.get('max_heart_rate'),
        'series_summary': {
            'samples_count': samples_count,
            'missing_count': missing_count,
            'avg_hr': avg_hr,
            'p95_hr': p95_hr,
            'min_hr': min_hr,
            'max_hr': max_hr,
            'peak': {
                'ts': peak_ts,
                'hr': peak_hr
            }
        }
    }


def slim_daily_heart_rate_list(items):
    """Convert list of DailyHeartRate to compact analysis-ready dicts."""
    return [slim_daily_heart_rate(item) for item in items]
