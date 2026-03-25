"""Slimmer for DailySteps data — extract key step metrics for analysis."""


def slim_daily_steps(item):
    """Convert DailySteps to compact analysis-ready dict."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)

    result = {}

    # Core fields
    for key in [
        'calendar_date', 'total_steps', 'step_goal', 'total_distance',
        'total_calories', 'active_calories', 'floors_ascended',
        'floors_descended', 'average_stress_level',
        'moderate_intensity_minutes', 'vigorous_intensity_minutes',
        'steps_goal',
    ]:
        val = data.get(key)
        if val is not None:
            # Rename for clarity
            if key == 'total_distance':
                result['total_distance_m'] = round(val, 1) if isinstance(val, float) else val
            elif key == 'calendar_date':
                result['calendar_date'] = str(val)
            else:
                result[key] = val

    # Compute goal achievement percentage
    steps = data.get('total_steps')
    goal = data.get('step_goal') or data.get('steps_goal')
    if steps is not None and goal and goal > 0:
        result['goal_pct'] = round(steps / goal * 100, 1)

    return result


def slim_daily_steps_list(items):
    """Convert list of DailySteps to compact analysis-ready dicts."""
    results = []
    for item in items:
        slimmed = slim_daily_steps(item)
        if slimmed.get('total_steps') is not None or slimmed.get('calendar_date') is not None:
            results.append(slimmed)
    return results

