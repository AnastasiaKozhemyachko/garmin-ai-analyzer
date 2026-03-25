"""Slimmer for DailySummary data — comprehensive daily health metrics."""


def slim_daily_summary(item):
    """Convert DailySummary to compact analysis-ready dict."""
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
    for date_key in ['calendar_date', 'summary_date']:
        val = data.get(date_key)
        if val is not None:
            result['calendar_date'] = str(val)
            break

    # Steps and distance
    for key in ['total_steps', 'daily_step_goal', 'total_distance_meters']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Floors
    for key in ['floors_ascended', 'floors_ascended_in_meters',
                 'floors_descended', 'floors_descended_in_meters']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Calories
    for key in ['total_kilocalories', 'active_kilocalories',
                 'bmr_kilocalories', 'consumed_kilocalories',
                 'net_calorie_goal', 'remaining_kilocalories']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Intensity minutes
    for key in ['moderate_intensity_minutes', 'vigorous_intensity_minutes',
                 'intensity_minutes_goal']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Compute intensity total
    mod = data.get('moderate_intensity_minutes', 0) or 0
    vig = data.get('vigorous_intensity_minutes', 0) or 0
    if mod or vig:
        result['total_intensity_minutes'] = mod + vig * 2  # vigorous counts double

    # Stress
    for key in ['average_stress_level', 'max_stress_level',
                 'stress_duration', 'rest_stress_duration',
                 'low_stress_duration', 'medium_stress_duration',
                 'high_stress_duration']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Heart rate
    for key in ['resting_heart_rate', 'min_heart_rate', 'max_heart_rate',
                 'min_avg_heart_rate', 'max_avg_heart_rate']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Respiration
    for key in ['avg_waking_respiration_value', 'highest_respiration_value',
                 'lowest_respiration_value']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # SpO2
    for key in ['average_spo2', 'lowest_spo2']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Body battery
    for key in ['body_battery_charged_value', 'body_battery_drained_value',
                 'body_battery_highest_value', 'body_battery_lowest_value',
                 'body_battery_most_recent_value']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Active time
    for key in ['active_seconds', 'sedentary_seconds',
                 'highly_active_seconds', 'sleeping_seconds']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Activities count
    for key in ['total_activities', 'activities_distance']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    return result


def slim_daily_summary_list(items):
    """Convert list of DailySummary to compact analysis-ready dicts."""
    results = []
    for item in items:
        slimmed = slim_daily_summary(item)
        if slimmed.get('calendar_date') is not None:
            results.append(slimmed)
    return results

