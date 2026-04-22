"""Slimmer for DailySummary data — comprehensive daily health metrics."""
from format_utils import to_dict


def slim_daily_summary(item):
    """Convert DailySummary to compact analysis-ready dict."""
    data = to_dict(item)

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

    # Floors (rounded)
    for key in ['floors_ascended', 'floors_descended']:
        val = data.get(key)
        if val is not None:
            result[key] = round(val, 1) if isinstance(val, float) else val

    # Calories
    for key in ['total_kilocalories', 'active_kilocalories']:
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

    # Stress (only average and max — detail is in daily_stress)
    for key in ['average_stress_level', 'max_stress_level']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Heart rate (only resting — detail is in daily_heart_rate)
    val = data.get('resting_heart_rate')
    if val is not None:
        result['resting_heart_rate'] = val

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

    # Body battery (only high/low — detail is in body_battery_data)
    for key in ['body_battery_highest_value', 'body_battery_lowest_value']:
        val = data.get(key)
        if val is not None:
            result[key] = val

    # Active time
    for key in ['active_seconds', 'sedentary_seconds',
                 'highly_active_seconds', 'sleeping_seconds']:
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

