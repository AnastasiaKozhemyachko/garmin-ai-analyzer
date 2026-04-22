def slim_activity(item):
    """
    Convert Activity to compact analysis-ready dict.
    """
    from format_utils import to_dict, format_timestamp

    data = to_dict(item)

    # Extract activity type
    activity_type = data.get('activity_type')
    if activity_type:
        if isinstance(activity_type, dict):
            type_key = activity_type.get('type_key')
        else:
            type_key = getattr(activity_type, 'type_key', None)
    else:
        type_key = None
    
    result = {
        'activity_id': data.get('activity_id'),
        'type': type_key,
        'name': data.get('activity_name'),
        'start_time_local': format_timestamp(data.get('start_time_local'))
    }
    
    if data.get('location_name') is not None:
        result['location_name'] = data.get('location_name')
    
    metrics = {}
    for key, value in [
        ('distance_m', round(data.get('distance'), 1) if data.get('distance') is not None else None),
        ('duration_s', round(data.get('duration')) if data.get('duration') is not None else None),
        ('moving_s', round(data.get('moving_duration')) if data.get('moving_duration') is not None else None),
        ('steps', data.get('steps')),
        ('calories_kcal', data.get('calories')),
        ('avg_hr', data.get('average_hr')),
        ('max_hr', data.get('max_hr')),
        ('elevation_gain_m', data.get('elevation_gain')),
        ('elevation_loss_m', data.get('elevation_loss')),
    ]:
        if value is not None:
            metrics[key] = value

    # Compute avg pace (min/km) if distance and duration available
    distance = data.get('distance')
    duration = data.get('moving_duration') or data.get('duration')
    if distance and duration and distance > 0:
        pace_min_per_km = (duration / 60) / (distance / 1000)
        metrics['avg_pace_min_per_km'] = round(pace_min_per_km, 2)

    # Stride length
    avg_stride = data.get('avg_stride_length') or data.get('average_stride_length')
    if avg_stride is not None:
        metrics['avg_stride_length_m'] = round(avg_stride, 2)

    result['metrics'] = metrics

    # Cadence (real garth field names)
    cadence = data.get('average_running_cadence_in_steps_per_minute')
    max_cadence = data.get('max_running_cadence_in_steps_per_minute')
    if cadence is not None:
        result['cadence_avg'] = round(cadence, 1)
    if max_cadence is not None:
        result['cadence_max'] = round(max_cadence, 1)

    return result


def slim_activity_list(items):
    """Convert list of Activity to compact analysis-ready dicts."""
    return [slim_activity(item) for item in items]
