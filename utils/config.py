"""Configuration for Garmin data collection and ChatGPT upload."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
GARTH_DIR = PROJECT_ROOT / ".garth"
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_FILE = RESULTS_DIR / "all_data.json"

# Data collection (default days)
DAYS_TO_COLLECT = 14

# Body Battery stress threshold for timeline granularity
HIGH_STRESS_THRESHOLD = 50  # If max stress > this, use full timeline; else 30m buckets

# ChatGPT upload
CHATGPT_URL = "https://chatgpt.com/c/698cef11-01a0-838a-935d-8ba471f26a92"
DELAY_MS = 2000
FINDER_WAIT_MS = 1000
UPLOAD_WAIT_MS = 8000

# Analysis prompts
PROMPT_MORNING = """Ты — AI-ассистент пользователя, который помогает начать день осознанно,
опираясь на данные Garmin.

Пользователь прикрепил файл с данными.
Используй только эти данные, без домыслов.

Если у события есть gmt-время и timezone_offset,
вычисляй локальное время как gmt_time + timezone_offset (мс)
и во всех выводах показывай только его.
Считай датой анализа календарную дату последних данных в файле.

Твоя задача — коротко и по-человечески рассказать:
как прошёл сон,
в каком состоянии организм сейчас,
есть ли сигналы усталости, перегруза или возможного начала болезни,
и как лучше выстроить сегодняшний день.

Отчёт должен быть обзорным и лёгким для чтения — не перегружай деталями.
Сфокусируйся только на том, что действительно важно сегодня.

По тренировке:
всегда говори конкретно — тренироваться или нет,
какую активность выбрать и на сколько минут.
Без общих формулировок.

Если каких-то данных не хватает, можно спокойно сказать «данных недостаточно»
и сделать выводы осторожно, без категоричности.

Стиль:
- Дружелюбный, спокойный, поддерживающий.
- Пиши так, будто говоришь с живым человеком.
- Можно использовать эмодзи, если они подходят по смыслу.
- Коротко, без воды и морали.
- На русском языке.

В конце добавь небольшой блок:
«Хочешь, можешь спросить меня, например:»
и предложи 2–3 простых вопроса.
"""

PROMPT_EVENING = """Ты — AI-ассистент пользователя, который вечером помогает
подвести итоги дня и мягко подготовиться ко сну.

Пользователь прикрепил файл с данными Garmin.
Используй только эти данные, без домыслов.

Если у события есть gmt-время и timezone_offset,
вычисляй локальное время как gmt_time + timezone_offset (мс)
и во всех выводах показывай только его.
Считай датой анализа календарную дату последних данных в файле.

Твоя задача — по-человечески и коротко рассказать:
каким был сегодняшний день,
где было больше нагрузки или стресса (и когда),
есть ли сигналы усталости, перегруза или возможного начала болезни,
и как лучше восстановиться сегодня.

Это должен быть обзор, а не отчёт.
Выделяй главное, не перегружай текст.

По сну:
дай конкретные рекомендации —
примерно во сколько лучше лечь,
во сколько ориентировочно встать,
и 1–2 простых совета для восстановления.

Если часть выводов ограничена, можно спокойно сказать «данных недостаточно»
без оправданий и формальностей.

Стиль:
- Тёплый, поддерживающий, не назидательный.
- Пиши как ассистент, а не как система.
- Можно использовать эмодзи, если они усиливают смысл.
- Коротко и легко для чтения.
- На русском языке.

В конце добавь небольшой блок:
«Если хочешь, можешь спросить меня:»
и предложи 2–3 вопроса про сон, восстановление или завтра.
"""

DATA_TYPES_MORNING = [
    ("daily_sleep_data", "DailySleepData", 2),
    ("daily_hrv", "DailyHRV", 14),
    ("daily_heart_rate", "DailyHeartRate", 7),
    ("training_readiness_data", "TrainingReadinessData", 3),
    ("activity", "Activity", 3),
    ("body_battery_data", "BodyBatteryData", 2),
    ("daily_stress", "DailyStress", 2),
]

DATA_TYPES_EVENING = [
    ("daily_stress", "DailyStress", 2),
    ("body_battery_data", "BodyBatteryData", 2),
    ("activity", "Activity", 2),
    ("daily_sleep_data", "DailySleepData", 2),
    ("daily_heart_rate", "DailyHeartRate", 3),
    ("daily_hrv", "DailyHRV", 3),
]

# Garmin data types: (name, class_name, days, enabled), example
DATA_TYPES = [
    # Core health metrics (recommended for illness detection)
    ("daily_hrv", "DailyHRV", 30),
    ("daily_heart_rate", "DailyHeartRate", 30),
    ("daily_sleep", "DailySleep", 14),
    ("daily_stress", "DailyStress", 14),
    ("body_battery_data", "BodyBatteryData", 7),
    ("training_readiness_data", "TrainingReadinessData", 7),
    ("daily_steps", "DailySteps", 14),
    
    # Additional metrics (optional)
    ("activity", "Activity", 14),
    ("daily_body_battery_stress", "DailyBodyBatteryStress", 14),
    ("daily_hydration", "DailyHydration", 14),
    ("daily_intensity_minutes", "DailyIntensityMinutes", 14),
    ("daily_sleep_data", "DailySleepData", 14),
    ("daily_summary", "DailySummary", 14),
    ("daily_training_status", "DailyTrainingStatus", 14),
    ("fitness_activity", "FitnessActivity", 14),
    ("garmin_scores_data", "GarminScoresData", 14),
    ("hrv_data", "HRVData", 14),
    ("morning_training_readiness", "MorningTrainingReadinessData", 7),
    ("sleep_data", "SleepData", 14),
    ("weight_data", "WeightData", 30),
    
    # Weekly/Monthly aggregates
    ("weekly_intensity_minutes", "WeeklyIntensityMinutes", 8),
    ("weekly_steps", "WeeklySteps", 8),
    ("weekly_stress", "WeeklyStress", 8),
    ("weekly_training_status", "WeeklyTrainingStatus", 8),
    ("monthly_training_status", "MonthlyTrainingStatus", 3)
]
