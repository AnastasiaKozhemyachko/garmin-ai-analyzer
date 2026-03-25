"""Slimmer for DailyTrainingStatus data — training load balance and status."""


def slim_training_status(item):
    """Convert DailyTrainingStatus to compact analysis-ready dict."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)

    result = {}

    # Date
    for date_key in ['calendar_date', 'timestamp_local']:
        val = data.get(date_key)
        if val is not None:
            result['calendar_date'] = str(val)
            break

    # Training load (real garth field names)
    acute = data.get('daily_training_load_acute') or data.get('acute_training_load')
    chronic = data.get('daily_training_load_chronic') or data.get('chronic_training_load')
    if acute is not None:
        result['acute_load'] = round(acute, 1) if isinstance(acute, float) else acute
    if chronic is not None:
        result['chronic_load'] = round(chronic, 1) if isinstance(chronic, float) else chronic

    # Load ratio (real garth field name)
    ratio = data.get('daily_acute_chronic_workload_ratio') or data.get('training_load_balance')
    if ratio is not None:
        result['load_ratio'] = round(ratio, 2) if isinstance(ratio, float) else ratio
    elif acute is not None and chronic is not None and chronic > 0:
        result['load_ratio'] = round(acute / chronic, 2)

    # ACWR status
    for key in ['acwr_status', 'acwr_percent', 'acwr_status_feedback']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Training status
    for key in ['training_status', 'training_status_feedback_phrase',
                 'training_status_phrase', 'latest_training_status_phrase']:
        val = data.get(key)
        if val is not None:
            if key == 'training_status_feedback_phrase':
                result['training_status_phrase'] = val
            elif key not in ('training_status',):
                result[key] = val
            else:
                result['training_status_code'] = val

    # Load tunnel (min/max recommended load)
    min_load = data.get('min_training_load_chronic')
    max_load = data.get('max_training_load_chronic')
    if min_load is not None and max_load is not None:
        result['load_tunnel'] = {
            'min': round(min_load, 1),
            'max': round(max_load, 1)
        }

    # Fitness trend
    for key in ['fitness_trend', 'fitness_trend_sport']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Recovery time
    for key in ['recovery_time_hours', 'recovery_time']:
        val = data.get(key)
        if val is not None:
            result['recovery_time_hours'] = val
            break

    # Training paused
    val = data.get('training_paused')
    if val is not None:
        result['training_paused'] = val

    return result


def slim_training_status_list(items):
    """Convert list of DailyTrainingStatus to compact analysis-ready dicts."""
    results = []
    for item in items:
        slimmed = slim_training_status(item)
        if slimmed and len(slimmed) > 1:  # at least date + something
            results.append(slimmed)
    return results

