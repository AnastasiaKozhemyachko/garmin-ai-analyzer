def slim_training_readiness(item):
    """Convert TrainingReadinessData to compact analysis-ready dict."""
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif isinstance(item, dict):
        data = item
    else:
        data = vars(item)
    
    # Format timestamps
    def format_timestamp(ts):
        if ts is None:
            return None
        if hasattr(ts, 'replace'):
            return ts.replace(microsecond=0).isoformat()
        return str(ts)
    
    return {
        'calendar_date': str(data.get('calendar_date')) if data.get('calendar_date') else None,
        'timestamp_local': format_timestamp(data.get('timestamp_local')),
        'level': data.get('level'),
        'score': data.get('score'),
        'feedback_short': data.get('feedback_short'),
        'feedback_long': data.get('feedback_long'),
        'factors': {
            'sleep_score': data.get('sleep_score'),
            'sleep_score_percent': data.get('sleep_score_factor_percent'),
            'recovery_time_hours': data.get('recovery_time'),
            'recovery_percent': data.get('recovery_time_factor_percent'),
            'acute_load': data.get('acute_load'),
            'hrv_percent': data.get('hrv_factor_percent'),
            'hrv_weekly_average': data.get('hrv_weekly_average'),
            'stress_history_percent': data.get('stress_history_factor_percent'),
            'sleep_history_percent': data.get('sleep_history_factor_percent')
        }
    }


def slim_training_readiness_list(items, pick="latest"):
    """
    Convert list of TrainingReadinessData to compact analysis-ready dicts.
    Deduplicates by calendar_date, keeping one record per day.
    
    For morning reports, Garmin may return multiple readiness snapshots per day.
    We keep either the latest (default) or earliest reading per calendar_date.
    
    Args:
        items: list of TrainingReadinessData models or dicts
        pick: "latest" (default) or "earliest" - which record to keep per day
    
    Returns:
        list of slim dicts, one per calendar_date, sorted by date ascending
    """
    from datetime import datetime
    
    # Slim all items first
    slimmed = [slim_training_readiness(item) for item in items]
    
    # Group by calendar_date and pick best per day
    by_date = {}
    for slim in slimmed:
        cal_date = slim.get('calendar_date')
        if not cal_date:
            continue
        
        # Parse timestamp for comparison
        ts_str = slim.get('timestamp_local')
        try:
            ts = datetime.fromisoformat(ts_str) if ts_str else None
        except:
            ts = None
        
        # Keep best record per date based on pick strategy
        if cal_date not in by_date:
            by_date[cal_date] = (slim, ts)
        else:
            existing_slim, existing_ts = by_date[cal_date]
            
            # Compare timestamps if both exist
            if ts and existing_ts:
                if (pick == "latest" and ts > existing_ts) or (pick == "earliest" and ts < existing_ts):
                    by_date[cal_date] = (slim, ts)
            elif ts and not existing_ts:
                by_date[cal_date] = (slim, ts)
    
    # Extract slimmed dicts and sort by calendar_date
    result = [slim for slim, _ in by_date.values()]
    result.sort(key=lambda x: x.get('calendar_date') or '')
    
    return result
