"""Shared formatting utilities for all slimmers."""
from datetime import datetime, timezone, timedelta


def to_dict(item):
    """Convert any garth model/object to a plain dict."""
    if hasattr(item, 'model_dump'):
        return item.model_dump()
    elif hasattr(item, 'dict'):
        return item.dict()
    elif isinstance(item, dict):
        return item
    elif hasattr(item, '__dict__'):
        return vars(item)
    return {}


def ms_to_local_iso(ms, tz_offset_ms=None):
    """Convert millisecond epoch to local ISO string (YYYY-MM-DDTHH:MM:SS).

    If tz_offset_ms is provided, uses it. Otherwise assumes UTC.
    """
    if ms is None:
        return None
    try:
        ts_sec = ms / 1000
        dt_utc = datetime.fromtimestamp(ts_sec, tz=timezone.utc)
        if tz_offset_ms is not None:
            offset = timedelta(milliseconds=tz_offset_ms)
            dt_local = dt_utc + offset
        else:
            dt_local = dt_utc
        return dt_local.strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return str(ms)


def format_timestamp(ts):
    """Format a datetime or string timestamp to clean ISO string."""
    if ts is None:
        return None
    if hasattr(ts, 'strftime'):
        return ts.strftime('%Y-%m-%dT%H:%M:%S')
    s = str(ts)
    # Clean up common artifacts
    return s.replace('.0', '').replace('+00:00', '')


def gmt_iso_to_local_iso(gmt_iso_str, tz_offset_min):
    """Convert GMT ISO string + tz offset (minutes) to local ISO string."""
    if not gmt_iso_str or tz_offset_min is None:
        return gmt_iso_str
    try:
        # Parse the GMT ISO string
        dt = datetime.fromisoformat(gmt_iso_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_local = dt + timedelta(minutes=tz_offset_min)
        return dt_local.strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return gmt_iso_str


def percentile(data, p):
    """Calculate percentile without numpy using linear interpolation."""
    if not data:
        return None
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

