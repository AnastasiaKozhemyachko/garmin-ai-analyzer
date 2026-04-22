from format_utils import to_dict


def slim_daily_stress(item):
    """Convert DailyStress to compact analysis-ready dict with distribution analysis."""
    data = to_dict(item)

    result = {}
    if data.get('calendar_date') is not None:
        result['calendar_date'] = str(data.get('calendar_date'))
    if data.get('overall_stress_level') is not None:
        result['overall_stress_level'] = data.get('overall_stress_level')
    if data.get('max_stress_level') is not None:
        result['max_stress_level'] = data.get('max_stress_level')
    if data.get('stress_qualifier') is not None:
        result['stress_qualifier'] = data.get('stress_qualifier')

    # Duration fields
    rest_s = data.get('rest_stress_duration')
    low_s = data.get('low_stress_duration')
    med_s = data.get('medium_stress_duration')
    high_s = data.get('high_stress_duration')

    if rest_s is not None:
        result['rest_duration_s'] = rest_s
    if low_s is not None:
        result['low_duration_s'] = low_s
    if med_s is not None:
        result['medium_duration_s'] = med_s
    if high_s is not None:
        result['high_duration_s'] = high_s

    # Activity and uncategorized stress
    if data.get('activity_stress_duration') is not None:
        result['activity_duration_s'] = data.get('activity_stress_duration')
    if data.get('uncategorized_stress_duration') is not None:
        result['uncategorized_duration_s'] = data.get('uncategorized_stress_duration')

    # Compute percentage distribution
    durations = {
        'rest': rest_s or 0,
        'low': low_s or 0,
        'medium': med_s or 0,
        'high': high_s or 0,
    }
    total = sum(durations.values())
    if total > 0:
        result['distribution_pct'] = {
            k: round(v / total * 100, 1) for k, v in durations.items()
        }

    return result


def slim_daily_stress_list(items):
    """Convert list of DailyStress to compact analysis-ready dicts."""
    result = [slim_daily_stress(item) for item in items]
    # Filter out empty records
    return [r for r in result if r.get('overall_stress_level') is not None]
