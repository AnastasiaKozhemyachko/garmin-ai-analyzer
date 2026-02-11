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
    
    return {
        'calendar_date': str(data.get('calendar_date')) if data.get('calendar_date') else None,
        'weekly_avg': data.get('weekly_avg'),
        'last_night_avg': data.get('last_night_avg'),
        'last_night_5_min_high': data.get('last_night_5_min_high'),
        'status': data.get('status'),
        'feedback_phrase': data.get('feedback_phrase'),
        'baseline': {
            'low_upper': baseline.get('low_upper'),
            'balanced_low': baseline.get('balanced_low'),
            'balanced_upper': baseline.get('balanced_upper')
        }
    }


def slim_daily_hrv_list(items):
    """Convert list of DailyHRV to compact analysis-ready dicts."""
    return [slim_daily_hrv(item) for item in items]
