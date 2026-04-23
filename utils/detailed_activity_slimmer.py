import garth


def slim_detailed_activity(item):
    """
    Convert Activity to detailed dict with maximum parameters.
    Uses Garmin Connect API to fetch comprehensive activity data.
    
    Extracts:
    - Basic info (type, name, location, timestamps)
    - Duration metrics (total, moving, elapsed)
    - Distance and speed metrics
    - Heart rate data (avg, max, min)
    - Elevation data (gain, loss, min, max, avg)
    - Cadence and stride
    - Training effect and load
    - Calories and intensity minutes
    - Body battery impact
    - Coordinates
    - Water estimation
    """
    # Get activity ID
    if hasattr(item, 'activity_id'):
        activity_id = item.activity_id
    elif isinstance(item, dict):
        activity_id = item.get('activity_id')
    else:
        activity_id = getattr(item, 'activity_id', None)
    
    if not activity_id:
        return {}
    
    # Fetch detailed data from API
    try:
        detailed = garth.connectapi(f'/activity-service/activity/{activity_id}')
    except Exception as e:
        print(f"⚠️  Could not fetch detailed data: {e}")
        # Fallback to basic data
        if hasattr(item, 'model_dump'):
            return item.model_dump()
        elif hasattr(item, 'dict'):
            return item.dict()
        else:
            return vars(item)
    
    summary = detailed.get('summaryDTO', {})
    metadata = detailed.get('metadataDTO', {})
    activity_type = detailed.get('activityTypeDTO', {})
    
    # Format timestamp
    def format_timestamp(ts):
        if ts is None:
            return None
        return str(ts).replace('.0', '')
    
    result = {
        'activity_id': activity_id,
        'activity_name': detailed.get('activityName'),
        'type_key': activity_type.get('typeKey'),
        'location_name': detailed.get('locationName'),
        'start_time_local': format_timestamp(summary.get('startTimeLocal')),
    }
    
    # Duration metrics
    duration = {}
    if summary.get('duration'):
        duration['total_s'] = summary['duration']
    if summary.get('movingDuration'):
        duration['moving_s'] = summary['movingDuration']
    if summary.get('elapsedDuration'):
        duration['elapsed_s'] = summary['elapsedDuration']
    if duration:
        result['duration'] = duration
    
    # Distance and speed
    distance_speed = {}
    if summary.get('distance'):
        distance_speed['distance_m'] = summary['distance']
    if summary.get('averageSpeed'):
        distance_speed['avg_speed_m_s'] = summary['averageSpeed']
    if summary.get('averageMovingSpeed'):
        distance_speed['avg_moving_speed_m_s'] = summary['averageMovingSpeed']
    if summary.get('maxSpeed'):
        distance_speed['max_speed_m_s'] = summary['maxSpeed']
    # Compute avg pace (min/km)
    dist = summary.get('distance')
    moving_dur = summary.get('movingDuration') or summary.get('duration')
    if dist and moving_dur and dist > 0:
        pace = (moving_dur / 60) / (dist / 1000)
        distance_speed['avg_pace_min_per_km'] = round(pace, 2)
    if distance_speed:
        result['distance_speed'] = distance_speed
    
    # Heart rate
    hr = {}
    if summary.get('averageHR'):
        hr['avg'] = summary['averageHR']
    if summary.get('maxHR'):
        hr['max'] = summary['maxHR']
    if summary.get('minHR'):
        hr['min'] = summary['minHR']
    if hr:
        result['heart_rate'] = hr
    
    # Elevation
    elevation = {}
    if summary.get('elevationGain'):
        elevation['gain_m'] = summary['elevationGain']
    if summary.get('elevationLoss'):
        elevation['loss_m'] = summary['elevationLoss']
    if summary.get('minElevation'):
        elevation['min_m'] = summary['minElevation']
    if summary.get('maxElevation'):
        elevation['max_m'] = summary['maxElevation']
    if summary.get('avgElevation'):
        elevation['avg_m'] = summary['avgElevation']
    if summary.get('maxVerticalSpeed'):
        elevation['max_vertical_speed_m_s'] = summary['maxVerticalSpeed']
    if elevation:
        result['elevation'] = elevation
    
    # Cadence
    cadence = {}
    if summary.get('averageRunCadence'):
        cadence['avg_steps_per_min'] = summary['averageRunCadence']
    if summary.get('maxRunCadence'):
        cadence['max_steps_per_min'] = summary['maxRunCadence']
    if summary.get('averageStrideLength'):
        cadence['avg_stride_length_m'] = round(summary['averageStrideLength'] / 100, 2) if summary['averageStrideLength'] > 10 else summary['averageStrideLength']
    if cadence:
        result['cadence'] = cadence
    
    # Training effect and load
    training = {}
    if summary.get('trainingEffect'):
        training['aerobic_effect'] = summary['trainingEffect']
    if summary.get('aerobicTrainingEffectMessage'):
        training['aerobic_message'] = summary['aerobicTrainingEffectMessage']
    if summary.get('anaerobicTrainingEffect'):
        training['anaerobic_effect'] = summary['anaerobicTrainingEffect']
    if summary.get('anaerobicTrainingEffectMessage'):
        training['anaerobic_message'] = summary['anaerobicTrainingEffectMessage']
    if summary.get('trainingEffectLabel'):
        training['label'] = summary['trainingEffectLabel']
    if summary.get('activityTrainingLoad'):
        training['load'] = summary['activityTrainingLoad']
    if training:
        result['training'] = training
    
    # Energy and intensity
    energy = {}
    if summary.get('calories'):
        energy['total_kcal'] = summary['calories']
    if summary.get('bmrCalories'):
        energy['bmr_kcal'] = summary['bmrCalories']
    if summary.get('moderateIntensityMinutes'):
        energy['moderate_intensity_min'] = summary['moderateIntensityMinutes']
    if summary.get('vigorousIntensityMinutes'):
        energy['vigorous_intensity_min'] = summary['vigorousIntensityMinutes']
    if energy:
        result['energy'] = energy
    
    # Steps
    if summary.get('steps'):
        result['steps'] = summary['steps']
    
    # Body battery impact
    if summary.get('differenceBodyBattery'):
        result['body_battery_impact'] = summary['differenceBodyBattery']
    
    # Water estimation
    if summary.get('waterEstimated'):
        result['water_estimated_ml'] = summary['waterEstimated']
    
    # Lap info
    if summary.get('minActivityLapDuration'):
        result['min_lap_duration_s'] = summary['minActivityLapDuration']
    
    # VO2max (if available for this activity type)
    vo2_fields = {}
    for key in ['vo2Max', 'vo2MaxValue', 'vO2MaxValue']:
        if summary.get(key):
            vo2_fields['vo2_max'] = summary[key]
            break
    if vo2_fields:
        result['vo2'] = vo2_fields

    # Respiration
    respiration = {}
    if summary.get('averageRespirationRate'):
        respiration['avg'] = summary['averageRespirationRate']
    if summary.get('maxRespirationRate'):
        respiration['max'] = summary['maxRespirationRate']
    if summary.get('minRespirationRate'):
        respiration['min'] = summary['minRespirationRate']
    if respiration:
        result['respiration'] = respiration

    # Temperature
    temperature = {}
    if summary.get('minTemperature') is not None:
        temperature['min_c'] = summary['minTemperature']
    if summary.get('maxTemperature') is not None:
        temperature['max_c'] = summary['maxTemperature']
    if temperature:
        result['temperature'] = temperature

    # Heart Rate Zones (from detailed API response)
    hr_zones = detailed.get('heartRateZones')
    if hr_zones and isinstance(hr_zones, list):
        zones_summary = []
        for zone in hr_zones:
            if isinstance(zone, dict):
                zone_entry = {}
                if zone.get('zoneNumber') is not None:
                    zone_entry['zone'] = zone['zoneNumber']
                if zone.get('secsInZone') is not None:
                    zone_entry['seconds'] = zone['secsInZone']
                if zone.get('zoneLowBoundary') is not None:
                    zone_entry['low_bpm'] = zone['zoneLowBoundary']
                if zone_entry:
                    zones_summary.append(zone_entry)
        if zones_summary:
            result['hr_zones'] = zones_summary

    # Splits/Laps
    try:
        splits_data = garth.connectapi(f'/activity-service/activity/{activity_id}/splits')
        if splits_data and isinstance(splits_data, dict):
            laps = splits_data.get('lapDTOs') or splits_data.get('splitDTOs') or []
            if laps:
                laps_summary = []
                for i, lap in enumerate(laps):
                    if not isinstance(lap, dict):
                        continue
                    lap_entry = {'lap': i + 1}
                    if lap.get('distance'):
                        lap_entry['distance_m'] = round(lap['distance'], 1)
                    if lap.get('duration'):
                        lap_entry['duration_s'] = round(lap['duration'], 1)
                    if lap.get('averageHR'):
                        lap_entry['avg_hr'] = lap['averageHR']
                    if lap.get('maxHR'):
                        lap_entry['max_hr'] = lap['maxHR']
                    if lap.get('averageSpeed'):
                        lap_entry['avg_speed_m_s'] = round(lap['averageSpeed'], 3)
                    if lap.get('averageRunCadence'):
                        lap_entry['avg_cadence'] = lap['averageRunCadence']
                    if lap.get('elevationGain'):
                        lap_entry['elevation_gain_m'] = lap['elevationGain']
                    laps_summary.append(lap_entry)
                if laps_summary:
                    result['splits'] = laps_summary
    except Exception:
        pass  # Splits data not available

    return result


def slim_detailed_activity_list(items):
    """Convert list of Activity to detailed dicts."""
    return [slim_detailed_activity(item) for item in items]
