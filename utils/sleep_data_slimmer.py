import statistics
from typing import Any, Dict, List, Optional


def percentile(data: List[float], p: float) -> float:
    """Calculate percentile without numpy."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def aggregate_sleep_movement(movements: List[Dict], sleep_start_gmt_ms: Optional[int]) -> Optional[Dict]:
    """Aggregate sleep_movement array into compact summary."""
    if not movements:
        return None
    
    levels = [m['activity_level'] for m in movements]
    p90 = percentile(levels, 0.90)
    p95 = percentile(levels, 0.95)
    
    # Find longest consecutive high block
    high_blocks = []
    current_block = 0
    for level in levels:
        if level >= p90:
            current_block += 1
        else:
            if current_block > 0:
                high_blocks.append(current_block)
            current_block = 0
    if current_block > 0:
        high_blocks.append(current_block)
    
    # Find peak and calculate offset from sleep start
    max_level = max(levels)
    max_idx = levels.index(max_level)
    peak_start_gmt = movements[max_idx].get('start_gmt')
    
    # Calculate offset in minutes from sleep start
    peak_start_offset_min = None
    peak_offset_clamped = False
    if peak_start_gmt and sleep_start_gmt_ms is not None:
        try:
            from datetime import datetime, timezone
            # Parse ISO string to datetime
            dt = datetime.fromisoformat(peak_start_gmt.replace('Z', '+00:00'))
            # Ensure UTC timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            # Convert to milliseconds
            peak_ms = int(dt.timestamp() * 1000)
            # Calculate raw offset
            raw_offset_min = (peak_ms - sleep_start_gmt_ms) // 60000
            # Handle negative offsets
            if raw_offset_min < 0:
                peak_start_offset_min = None
                peak_offset_clamped = True
            else:
                peak_start_offset_min = int(raw_offset_min)
                peak_offset_clamped = False
        except:
            pass
    
    return {
        'avg': round(statistics.mean(levels), 2),
        'p95': round(p95, 2),
        'max': round(max_level, 2),
        'high_minutes': sum(1 for l in levels if l >= p90),
        'longest_high_block_minutes': max(high_blocks) if high_blocks else 0,
        'peak_start_gmt': peak_start_gmt,
        **({'peak_start_offset_min': peak_start_offset_min} if peak_start_offset_min is not None else {}),
        'peak_offset_clamped': peak_offset_clamped
    }


def aggregate_sleep_levels(levels: List[Dict], sleep_start_gmt: Optional[int]) -> Optional[Dict]:
    """Aggregate sleep_levels into compressed timeline with 10-minute resolution."""
    if not levels or not sleep_start_gmt:
        return None
    
    level_map = {0: 'deep', 1: 'light', 2: 'rem', 3: 'awake'}
    timeline = []
    
    for entry in levels:
        start_gmt = entry.get('start_gmt', '')
        activity_level = entry.get('activity_level')
        level_name = level_map.get(activity_level, 'unknown')
        
        if start_gmt:
            try:
                from datetime import datetime
                entry_ts_gmt = int(datetime.fromisoformat(start_gmt.replace('Z', '+00:00')).timestamp() * 1000)
                offset_minutes = (entry_ts_gmt - sleep_start_gmt) // 60000
                # Skip negative offsets
                if offset_minutes < 0:
                    continue
                # Round down to nearest 10 minutes
                rounded_offset = (offset_minutes // 10) * 10
                timeline.append([rounded_offset, level_name])
            except:
                pass
    
    if not timeline:
        return None
    
    # Sort by offset
    timeline.sort(key=lambda x: x[0])
    
    # Compress timeline: keep only transitions (run-length encoding)
    compressed = []
    for offset, level in timeline:
        # If same offset as last entry, replace it (keep final state)
        if compressed and compressed[-1][0] == offset:
            compressed[-1] = [offset, level]
        # If different level than last entry, add transition
        elif not compressed or compressed[-1][1] != level:
            compressed.append([offset, level])
    
    return {'timeline_10m': compressed}


def slim_daily_sleep_data(item: Any) -> Dict:
    """
    Convert DailySleepData to compact dict with aggregated summaries.
    
    Args:
        item: DailySleepData instance or dict with same structure
        
    Returns:
        Compact dict with core fields and aggregated summaries
    """
    # Handle Pydantic model or dict
    if hasattr(item, 'model_dump'):
        data = item.model_dump()
    elif hasattr(item, 'dict'):
        data = item.dict()
    elif hasattr(item, '__dict__'):
        data = vars(item)
    else:
        data = item if isinstance(item, dict) else {}
    
    # Access attributes directly if not a dict
    if not isinstance(data, dict):
        dto = getattr(item, 'daily_sleep_dto', None)
        movements = getattr(item, 'sleep_movement', [])
        levels = getattr(item, 'sleep_levels', [])
    else:
        dto = data.get('daily_sleep_dto', {})
        movements = data.get('sleep_movement', [])
        levels = data.get('sleep_levels', [])
    
    result = {}
    
    # Core fields - access from dto object or dict
    fields = [
        'calendar_date', 'sleep_start_timestamp_gmt', 'sleep_end_timestamp_gmt',
        'sleep_start_timestamp_local', 'sleep_end_timestamp_local',
        'sleep_time_seconds', 'nap_time_seconds', 'deep_sleep_seconds',
        'light_sleep_seconds', 'rem_sleep_seconds', 'awake_sleep_seconds',
        'awake_count', 'resting_heart_rate', 'body_battery_change',
        'avg_sleep_stress', 'average_respiration_value', 'lowest_respiration_value',
        'highest_respiration_value', 'sleep_score_feedback',
        'sleep_score_insight', 'sleep_score_personalized_insight'
    ]
    
    for field in fields:
        if isinstance(dto, dict):
            if field in dto:
                result[field] = dto[field]
        elif hasattr(dto, field):
            result[field] = getattr(dto, field)
    
    # Sleep score
    if isinstance(dto, dict):
        sleep_scores = dto.get('sleep_scores', {})
        overall = sleep_scores.get('overall', {})
    else:
        sleep_scores = getattr(dto, 'sleep_scores', None)
        overall = getattr(sleep_scores, 'overall', None) if sleep_scores else None
    
    if overall:
        if isinstance(overall, dict):
            result['sleep_score'] = {
                'value': overall.get('value'),
                'qualifier': overall.get('qualifier_key')
            }
        else:
            result['sleep_score'] = {
                'value': getattr(overall, 'value', None),
                'qualifier': getattr(overall, 'qualifier_key', None)
            }
    
    # Sleep need
    if isinstance(dto, dict):
        sleep_need = dto.get('sleep_need', {})
    else:
        sleep_need = getattr(dto, 'sleep_need', None)
    
    if sleep_need:
        need_fields = ['baseline', 'actual', 'feedback', 'hrv_adjustment',
                      'nap_adjustment', 'sleep_history_adjustment']
        if isinstance(sleep_need, dict):
            result['sleep_need'] = {k: sleep_need.get(k) for k in need_fields if k in sleep_need}
        else:
            result['sleep_need'] = {k: getattr(sleep_need, k, None) for k in need_fields if hasattr(sleep_need, k)}
    
    # Get sleep_start_timestamp_gmt for time calculations
    if isinstance(dto, dict):
        sleep_start_gmt = dto.get('sleep_start_timestamp_gmt')
    else:
        sleep_start_gmt = getattr(dto, 'sleep_start_timestamp_gmt', None)
    
    # Movement summary - use GMT timestamp from result
    if movements:
        sleep_start_gmt_ms = result.get('sleep_start_timestamp_gmt')
        result['movement_summary'] = aggregate_sleep_movement(movements, sleep_start_gmt_ms)
    
    # Levels timeline
    if levels:
        levels_data = aggregate_sleep_levels(levels, sleep_start_gmt)
        if levels_data:
            result['levels_timeline'] = levels_data
    
    return result


def slim_daily_sleep_data_list(items: List[Any]) -> List[Dict]:
    """
    Convert list of DailySleepData to compact dicts with aggregated summaries.
    
    Args:
        items: List of DailySleepData instances or dicts
        
    Returns:
        List of compact dicts with core fields and aggregated summaries
    """
    return [slim_daily_sleep_data(item) for item in items]


# Example usage
if __name__ == '__main__':
    import json
    
    # Example: Process list of DailySleepData items
    # from garth import DailySleepData
    # from datetime import date
    # 
    # today = date.today().isoformat()
    # daily_sleep_data_list = DailySleepData.list(today, 7)
    # slimmed = slim_daily_sleep_data_list(daily_sleep_data_list)
    # 
    # with open('slimmed_sleep_data.json', 'w') as f:
    #     json.dump(slimmed, f, indent=2, default=str)
    
    print("Sleep data slimmer ready. Use slim_daily_sleep_data(item) or slim_daily_sleep_data_list(items).")
