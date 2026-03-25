"""Slimmer for GarminScoresData — overall daily scores from Garmin."""


def slim_garmin_scores(item):
    """Convert GarminScoresData to compact analysis-ready dict."""
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
    for date_key in ['calendar_date', 'date']:
        val = data.get(date_key)
        if val is not None:
            result['calendar_date'] = str(val)
            break

    # Overall score
    overall = data.get('overall')
    if overall is not None:
        if isinstance(overall, dict):
            for key in ['value', 'qualifier', 'optimal_start', 'optimal_end']:
                val = overall.get(key)
                if val is not None:
                    result.setdefault('overall', {})[key] = val
        elif hasattr(overall, 'value'):
            result['overall'] = {
                'value': getattr(overall, 'value', None),
                'qualifier': getattr(overall, 'qualifier', None),
            }
        else:
            result['overall_score'] = overall

    # Sub-scores
    for score_name in ['sleep', 'activity', 'stress', 'heart_rate',
                        'hrv', 'body_battery', 'training_readiness',
                        'training_status', 'recovery']:
        val = data.get(score_name)
        if val is None:
            # Try _score suffix
            val = data.get(f'{score_name}_score')
        if val is None:
            continue

        if isinstance(val, dict):
            score_dict = {}
            for key in ['value', 'qualifier', 'optimal_start', 'optimal_end']:
                v = val.get(key)
                if v is not None:
                    score_dict[key] = v
            if score_dict:
                result[score_name] = score_dict
        elif hasattr(val, 'value'):
            result[score_name] = {
                'value': getattr(val, 'value', None),
                'qualifier': getattr(val, 'qualifier', None),
            }
        elif isinstance(val, (int, float)):
            result[score_name] = val

    return result


def slim_garmin_scores_list(items):
    """Convert list of GarminScoresData to compact analysis-ready dicts."""
    results = []
    for item in items:
        slimmed = slim_garmin_scores(item)
        if slimmed.get('calendar_date') is not None:
            results.append(slimmed)
    return results

