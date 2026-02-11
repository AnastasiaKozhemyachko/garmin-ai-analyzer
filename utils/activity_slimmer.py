def slim_activity(item):
    """
    Convert Activity to compact analysis-ready dict.
    
    For morning reports, we keep only fields that help understand:
    - What activity was done (type, name, location)
    - When it happened (start_time_local)
    - Physical load metrics (distance, duration, steps, calories, HR, elevation)
    
    This provides context for recovery/readiness without overwhelming detail.
    """
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    # Format timestamp
    def format_timestamp(ts):
        if ts is None:
            return None
        if hasattr(ts, 'replace'):
            return ts.replace(microsecond=0).isoformat()
        return str(ts)
    
    # Extract activity type
    activity_type = data.get('activity_type')
    if activity_type:
        if isinstance(activity_type, dict):
            type_key = activity_type.get('type_key')
        else:
            type_key = getattr(activity_type, 'type_key', None)
    else:
        type_key = None
    
    return {
        'activity_id': data.get('activity_id'),
        'type': type_key,
        'start_time_local': format_timestamp(data.get('start_time_local')),
        'location_name': data.get('location_name'),
        'metrics': {
            'distance_m': data.get('distance'),
            'duration_s': data.get('duration'),
            'moving_s': data.get('moving_duration'),
            'steps': data.get('steps'),
            'calories_kcal': data.get('calories'),
            'avg_hr': data.get('average_hr'),
            'max_hr': data.get('max_hr'),
            'elevation_gain_m': data.get('elevation_gain')
        }
    }


def slim_activity_list(items):
    """Convert list of Activity to compact analysis-ready dicts."""
    return [slim_activity(item) for item in items]
