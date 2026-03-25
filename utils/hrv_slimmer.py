def slim_daily_hrv(item):
    """Convert DailyHRV to compact analysis-ready dict with trend analysis."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    baseline = data.get('baseline', {})
    if not isinstance(baseline, dict):
        baseline = baseline.dict() if hasattr(baseline, 'dict') else vars(baseline) if hasattr(baseline, '__dict__') else {}
    
    result = {}
    if data.get('calendar_date') is not None:
        result['calendar_date'] = str(data.get('calendar_date'))
    if data.get('weekly_avg') is not None:
        result['weekly_avg'] = data.get('weekly_avg')
    if data.get('last_night_avg') is not None:
        result['last_night_avg'] = data.get('last_night_avg')
    if data.get('last_night_5_min_high') is not None:
        result['last_night_5_min_high'] = data.get('last_night_5_min_high')
    if data.get('status') is not None:
        result['status'] = data.get('status')
    if data.get('feedback_phrase') is not None:
        result['feedback_phrase'] = data.get('feedback_phrase')
    if data.get('start_timestamp_gmt') is not None:
        result['start_timestamp_gmt'] = str(data.get('start_timestamp_gmt'))
    if data.get('end_timestamp_gmt') is not None:
        result['end_timestamp_gmt'] = str(data.get('end_timestamp_gmt'))
    if data.get('start_timestamp_local') is not None:
        result['start_timestamp_local'] = str(data.get('start_timestamp_local'))
    
    baseline_dict = {}
    if baseline.get('low_upper') is not None:
        baseline_dict['low_upper'] = baseline.get('low_upper')
    if baseline.get('balanced_low') is not None:
        baseline_dict['balanced_low'] = baseline.get('balanced_low')
    if baseline.get('balanced_upper') is not None:
        baseline_dict['balanced_upper'] = baseline.get('balanced_upper')
    if baseline.get('marker_value') is not None:
        baseline_dict['marker_value'] = baseline.get('marker_value')
    if baseline_dict:
        result['baseline'] = baseline_dict
    
    # Compute trend: compare last_night_avg to baseline range
    last_night = data.get('last_night_avg')
    balanced_low = baseline.get('balanced_low')
    balanced_upper = baseline.get('balanced_upper')
    low_upper = baseline.get('low_upper')
    
    if last_night is not None and balanced_low is not None and balanced_upper is not None:
        if last_night > balanced_upper:
            result['trend'] = 'above_baseline'
        elif last_night >= balanced_low:
            result['trend'] = 'balanced'
        elif low_upper is not None and last_night >= low_upper:
            result['trend'] = 'below_balanced'
        else:
            result['trend'] = 'low'
    
    # Deviation from weekly average
    weekly_avg = data.get('weekly_avg')
    if last_night is not None and weekly_avg is not None and weekly_avg > 0:
        deviation = round((last_night - weekly_avg) / weekly_avg * 100, 1)
        result['deviation_from_weekly_pct'] = deviation
    
    return result


def slim_daily_hrv_list(items):
    """Convert list of DailyHRV to compact analysis-ready dicts."""
    return [slim_daily_hrv(item) for item in items]
