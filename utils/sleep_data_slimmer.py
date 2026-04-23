import statistics
from typing import Any, Dict, List, Optional
from format_utils import to_dict, ms_to_local_iso, percentile



def aggregate_sleep_movement(movements: List[Dict], sleep_start_gmt_ms: Optional[int]) -> Optional[Dict]:
    """Aggregate sleep_movement array into compact summary."""
    if not movements or movements is None:
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
        **({'peak_start_offset_min': peak_start_offset_min} if peak_start_offset_min is not None else {}),
    }


def aggregate_sleep_levels(levels: List[Dict], sleep_start_gmt: Optional[int]) -> Optional[Dict]:
    """Aggregate sleep_levels into compressed timeline with 10-minute resolution."""
    if not levels or levels is None or not sleep_start_gmt:
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
    data = to_dict(item)

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
    
    # Grab GMT ms epoch for internal calculations (movement/levels offsets)
    sleep_start_gmt_ms = result.get('sleep_start_timestamp_gmt')

    # Convert local ms epochs to readable ISO strings, remove GMT timestamps
    for ts_field in ['sleep_start_timestamp_local', 'sleep_end_timestamp_local']:
        if ts_field in result and isinstance(result[ts_field], (int, float)):
            result[ts_field] = ms_to_local_iso(result[ts_field])
    # Remove raw GMT timestamps — local times are sufficient
    result.pop('sleep_start_timestamp_gmt', None)
    result.pop('sleep_end_timestamp_gmt', None)

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

    # Compute sleep efficiency (sleep time / total time in bed * 100)
    sleep_time = result.get('sleep_time_seconds', 0)
    awake_time = result.get('awake_sleep_seconds', 0)
    if sleep_time and sleep_time > 0:
        # Human-readable duration
        result['sleep_duration_hours'] = round(sleep_time / 3600, 1)
        total_in_bed = sleep_time + awake_time
        if total_in_bed > 0:
            result['sleep_efficiency_pct'] = round(sleep_time / total_in_bed * 100, 1)

    # Compute stage percentages
    deep = result.get('deep_sleep_seconds', 0) or 0
    light = result.get('light_sleep_seconds', 0) or 0
    rem = result.get('rem_sleep_seconds', 0) or 0
    awake = result.get('awake_sleep_seconds', 0) or 0
    total_stages = deep + light + rem + awake
    if total_stages > 0:
        result['stage_pct'] = {
            'deep': round(deep / total_stages * 100, 1),
            'light': round(light / total_stages * 100, 1),
            'rem': round(rem / total_stages * 100, 1),
            'awake': round(awake / total_stages * 100, 1),
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
    
    # Movement summary
    if movements:
        result['movement_summary'] = aggregate_sleep_movement(movements, sleep_start_gmt_ms)
    
    # Levels timeline
    if levels:
        levels_data = aggregate_sleep_levels(levels, sleep_start_gmt_ms)
        if levels_data:
            result['levels_timeline'] = levels_data
    
    return result


def slim_daily_sleep_data_list(items: List[Any], include_timeline: bool = True) -> List[Dict]:
    """
    Convert list of DailySleepData to compact dicts with aggregated summaries.
    
    Args:
        items: List of DailySleepData instances or dicts
        include_timeline: If False, strips levels_timeline to save tokens (for multi-day reports)

    Returns:
        List of compact dicts with core fields and aggregated summaries
    """
    results = [slim_daily_sleep_data(item) for item in items]
    if not include_timeline:
        for r in results:
            r.pop('levels_timeline', None)
    return results


