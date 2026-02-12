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


def slim_daily_stress(item):
    """Convert DailyStress to compact analysis-ready dict."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    result = {}
    if data.get('calendar_date') is not None:
        result['calendar_date'] = str(data.get('calendar_date'))
    if data.get('overall_stress_level') is not None:
        result['overall_stress_level'] = data.get('overall_stress_level')
    if data.get('rest_stress_duration') is not None:
        result['rest_duration_s'] = data.get('rest_stress_duration')
    if data.get('low_stress_duration') is not None:
        result['low_duration_s'] = data.get('low_stress_duration')
    if data.get('medium_stress_duration') is not None:
        result['medium_duration_s'] = data.get('medium_stress_duration')
    if data.get('high_stress_duration') is not None:
        result['high_duration_s'] = data.get('high_stress_duration')
    
    return result


def slim_daily_stress_list(items):
    """Convert list of DailyStress to compact analysis-ready dicts."""
    result = [slim_daily_stress(item) for item in items]
    # Filter out empty records
    return [r for r in result if r.get('overall_stress_level') is not None]
