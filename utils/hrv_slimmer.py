def slim_daily_hrv(item):
    """Convert DailyHRV to compact analysis-ready dict."""
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
    
    baseline_dict = {}
    if baseline.get('low_upper') is not None:
        baseline_dict['low_upper'] = baseline.get('low_upper')
    if baseline.get('balanced_low') is not None:
        baseline_dict['balanced_low'] = baseline.get('balanced_low')
    if baseline.get('balanced_upper') is not None:
        baseline_dict['balanced_upper'] = baseline.get('balanced_upper')
    if baseline_dict:
        result['baseline'] = baseline_dict
    
    return result


def slim_daily_hrv_list(items):
    """Convert list of DailyHRV to compact analysis-ready dicts."""
    return [slim_daily_hrv(item) for item in items]
