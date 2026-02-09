"""Configuration for Garmin data collection and ChatGPT upload."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
GARTH_DIR = PROJECT_ROOT / ".garth"
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_FILE = RESULTS_DIR / "all_data.json"

# Data collection
DAYS_TO_COLLECT = 14

# ChatGPT upload
CHATGPT_URL = "https://chatgpt.com/"
DELAY_MS = 3000
FINDER_WAIT_MS = 2000
UPLOAD_WAIT_MS = 20000

# Analysis prompt
ANALYSIS_PROMPT = """Проанализируй данные из файла.

Сделай:
1) короткий итог (3–5 строк)
2) что настораживает (HRV/RHR/сон/стресс — если есть)
3) вероятность, что я начинаю заболевать (низкая/средняя/высокая) + почему
4) план на ближайшие 3 дня."""

# Garmin data types to collect
DATA_TYPES = [
    ("activity", "Activity"),
    ("body_battery_data", "BodyBatteryData"),
    ("daily_body_battery_stress", "DailyBodyBatteryStress"),
    ("daily_hrv", "DailyHRV"),
    ("daily_heart_rate", "DailyHeartRate"),
    ("daily_hydration", "DailyHydration"),
    ("daily_intensity_minutes", "DailyIntensityMinutes"),
    ("daily_sleep", "DailySleep"),
    ("daily_sleep_data", "DailySleepData"),
    ("daily_steps", "DailySteps"),
    ("daily_stress", "DailyStress"),
    ("daily_summary", "DailySummary"),
    ("daily_training_status", "DailyTrainingStatus"),
    ("fitness_activity", "FitnessActivity"),
    ("garmin_scores_data", "GarminScoresData"),
    ("hrv_data", "HRVData"),
    ("monthly_training_status", "MonthlyTrainingStatus"),
    ("morning_training_readiness", "MorningTrainingReadinessData"),
    ("sleep_data", "SleepData"),
    ("training_readiness_data", "TrainingReadinessData"),
    ("weekly_intensity_minutes", "WeeklyIntensityMinutes"),
    ("weekly_steps", "WeeklySteps"),
    ("weekly_stress", "WeeklyStress"),
    ("weekly_training_status", "WeeklyTrainingStatus"),
    ("weight_data", "WeightData"),
]
