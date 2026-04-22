"""Slimmer for WeightData — extracts key weight and body composition metrics."""
from datetime import datetime


def _parse_metabolic_age(value):
    """Convert metabolic_age timestamp to years, or return None."""
    if not value:
        return None
    try:
        ts = value / 1000 if value > 1e12 else value
        birth = datetime.fromtimestamp(ts)
        now = datetime.now()
        age = now.year - birth.year - ((now.month, now.day) < (birth.month, birth.day))
        if 10 < age < 120:
            return age
    except Exception:
        pass
    return None


def slim_weight_data_list(raw_list):
    """Slim a list of WeightData entries."""
    result = []
    for entry in raw_list:
        if hasattr(entry, '__dict__'):
            d = vars(entry)
        elif hasattr(entry, 'dict'):
            d = entry.dict()
        elif isinstance(entry, dict):
            d = entry
        else:
            continue

        weight_g = d.get("weight")
        if not weight_g:
            continue

        slimmed = {
            "calendar_date": str(d.get("calendar_date", "")),
            "weight_kg": round(weight_g / 1000, 1),
        }

        if d.get("bmi"):
            slimmed["bmi"] = round(d["bmi"], 1)
        if d.get("body_fat"):
            slimmed["body_fat_pct"] = round(d["body_fat"], 1)
        if d.get("body_water"):
            slimmed["body_water_pct"] = round(d["body_water"], 1)
        if d.get("muscle_mass"):
            slimmed["muscle_mass_kg"] = round(d["muscle_mass"] / 1000, 1)
        if d.get("bone_mass"):
            slimmed["bone_mass_kg"] = round(d["bone_mass"] / 1000, 1)
        if d.get("visceral_fat") is not None:
            slimmed["visceral_fat"] = d["visceral_fat"]

        met_age = _parse_metabolic_age(d.get("metabolic_age"))
        if met_age:
            slimmed["metabolic_age"] = met_age

        result.append(slimmed)

    # Sort by date
    result.sort(key=lambda x: x.get("calendar_date", ""))

    # Add trend summary
    if len(result) >= 2:
        first = result[0]
        last = result[-1]
        delta = round(last["weight_kg"] - first["weight_kg"], 1)

        fat_first = first.get("body_fat_pct")
        fat_last = last.get("body_fat_pct")
        muscle_first = first.get("muscle_mass_kg")
        muscle_last = last.get("muscle_mass_kg")

        trend = {
            "period": f'{first["calendar_date"]} → {last["calendar_date"]}',
            "measurements": len(result),
            "weight_change_kg": delta,
            "start_kg": first["weight_kg"],
            "current_kg": last["weight_kg"],
        }
        if fat_first and fat_last:
            trend["body_fat_change_pct"] = round(fat_last - fat_first, 1)
        if muscle_first and muscle_last:
            trend["muscle_mass_change_kg"] = round(muscle_last - muscle_first, 1)

        result.append({"_trend": trend})

    return result

