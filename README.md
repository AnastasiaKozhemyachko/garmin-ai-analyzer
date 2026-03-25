# Garmin AI Analyzer

Automated Garmin health data collection with AI-powered analysis for morning and evening reports.

## Features

- Morning report: Sleep quality, recovery, and readiness assessment
- Evening report: Daily activity, stress, and sleep recommendations
- Activity analysis: Detailed workout breakdown with splits, HR zones, pace
- Weekly report: 7-day trends for sleep, HRV, stress, training load
- Health check: Early illness and overtraining detection
- Training plan: Load analysis with 3–5 day training schedule
- Sleep analysis: 14-day deep dive into sleep patterns and circadian rhythm
- Automatic ChatGPT upload with custom prompts
- Secure session management

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install garth
```

## Usage

### Morning Report
```bash
python3 run_morning.py
```
Collects recovery metrics and uploads to ChatGPT for morning readiness assessment.

### Evening Report
```bash
python3 run_evening.py
```
Collects daily activity data and uploads to ChatGPT for evening analysis.

### Activity Analysis
```bash
python3 run_activity.py
```
Collects latest activity with detailed metrics and uploads to ChatGPT for comprehensive analysis.

### Weekly Report
```bash
python3 run_weekly.py
```
Collects 7–14 days of data and generates a weekly trend report (sleep, HRV, stress, training load, VO2max).

### Health Check
```bash
python3 run_health.py
```
Analyzes 7–21 days of data for early signs of illness, overtraining, or chronic fatigue. Outputs 🟢🟡🔴 status.

### Training Plan
```bash
python3 run_training.py
```
Analyzes training load balance (acute vs chronic) and generates a specific 3–5 day training plan.

### Sleep Analysis
```bash
python3 run_sleep.py
```
Deep 14-day sleep analysis: circadian rhythm, stage trends, efficiency patterns, and recovery quality.

### Run Collection Only

To collect data without uploading to ChatGPT:

```bash
# Morning data collection only
python3 scripts/collect_morning.py

# Evening data collection only
python3 scripts/collect_evening.py

# Latest activity with detailed metrics
python3 scripts/collect_latest_activity.py

# Weekly trend data
python3 scripts/collect_weekly.py

# Health check data
python3 scripts/collect_health.py

# Training load data
python3 scripts/collect_training.py

# Sleep pattern data
python3 scripts/collect_sleep.py
```

## Configuration

Edit `utils/config.py` to customize:

- `PROMPT_MORNING` / `PROMPT_EVENING` / `PROMPT_ACTIVITY` - Analysis prompts
- `DATA_TYPES_MORNING` / `DATA_TYPES_EVENING` - Metrics to collect
- `CHATGPT_URL` - ChatGPT URL
- `DELAY_MS`, `FINDER_WAIT_MS`, `UPLOAD_WAIT_MS` - Timing settings

## Data Types Collected

### Morning Report
| Data | Source | Days | Key Metrics |
|------|--------|------|-------------|
| Sleep | DailySleepData | 3 | sleep_efficiency_pct, stage_pct, sleep_score |
| HRV | DailyHRV | 14 | trend, deviation_from_weekly_pct, baseline |
| Heart Rate | DailyHeartRate | 7 | resting_hr_delta, zone_pct, time_below_resting_pct |
| Training Readiness | TrainingReadinessData | 3 | score, factors (sleep, recovery, HRV, stress) |
| Activity | Activity | 3 | distance, pace, cadence, calories |
| Body Battery | BodyBatteryData | 3 | charge_rate_per_hour, drain_rate_per_hour |
| Stress | DailyStress | 3 | distribution_pct, overall_stress_level |
| Steps | DailySteps | 3 | total_steps, goal_pct |
| Daily Summary | DailySummary | 2 | calories, floors, SpO2, respiration, intensity |
| Training Status | DailyTrainingStatus | 7 | acute/chronic load, load_ratio, acwr_status |

### Evening Report
| Data | Source | Days | Key Metrics |
|------|--------|------|-------------|
| Stress | DailyStress | 2 | distribution_pct, overall_stress_level |
| Body Battery | BodyBatteryData | 2 | charge/drain rates, timeline |
| Activity | Activity | 2 | distance, pace, cadence, calories |
| Sleep | DailySleepData | 2 | efficiency, stage percentages |
| Heart Rate | DailyHeartRate | 3 | resting_hr_delta, zone distribution |
| HRV | DailyHRV | 3 | trend, deviation from weekly |
| Steps | DailySteps | 2 | total_steps, goal_pct |
| Daily Summary | DailySummary | 2 | full day metrics |
| Training Status | DailyTrainingStatus | 3 | load_ratio, acwr_status |
| Training Readiness | TrainingReadinessData | 2 | score for tomorrow planning |

### Activity Analysis
Fetches detailed data via Garmin Connect API:
- Pace (avg_pace_min_per_km), stride length, cadence
- HR zones (time in each zone)
- Splits/laps with per-lap metrics
- Respiration, temperature, water loss
- Training effect (aerobic/anaerobic), load, VO2max
- Body battery impact, coaching data

## Project Structure

```
├── run_morning.py          # Morning workflow
├── run_evening.py          # Evening workflow
├── run_activity.py         # Activity analysis workflow
├── run_weekly.py           # Weekly trend report workflow
├── run_health.py           # Health check workflow
├── run_training.py         # Training plan workflow
├── run_sleep.py            # Sleep deep-dive workflow
├── scripts/
│   ├── collect_morning.py  # Morning data collection
│   ├── collect_evening.py  # Evening data collection
│   ├── collect_latest_activity.py  # Latest activity collection
│   ├── collect_weekly.py   # Weekly data collection
│   ├── collect_health.py   # Health check data collection
│   ├── collect_training.py # Training data collection
│   ├── collect_sleep.py    # Sleep data collection
│   ├── upload_morning.py   # Morning upload
│   ├── upload_evening.py   # Evening upload
│   ├── upload_activity.py  # Activity upload
│   ├── upload_weekly.py    # Weekly upload
│   ├── upload_health.py    # Health check upload
│   ├── upload_training.py  # Training plan upload
│   └── upload_sleep.py     # Sleep analysis upload
└── utils/
    ├── config.py           # Configuration & prompts
    ├── collection_utils.py # Shared collection functions (slimmer registry)
    ├── upload_utils.py     # Shared upload functions
    ├── sleep_data_slimmer.py        # Sleep: efficiency, stages, movement
    ├── hrv_slimmer.py               # HRV: trend, baseline comparison
    ├── heart_rate_slimmer.py        # HR: zones, resting trend
    ├── training_readiness_slimmer.py # Readiness: score, factors
    ├── activity_slimmer.py          # Activity: pace, training effect
    ├── body_battery_slimmer.py      # BB: charge/drain rates
    ├── daily_stress_slimmer.py      # Stress: distribution, qualifier
    ├── detailed_activity_slimmer.py # Detailed: splits, HR zones, respiration
    ├── daily_steps_slimmer.py       # Steps: goal achievement
    ├── daily_summary_slimmer.py     # Summary: full day metrics
    ├── training_status_slimmer.py   # VO2max, training load balance
    └── garmin_scores_slimmer.py     # Garmin scores
```

## Requirements

- Python 3.7+
- macOS (for AppleScript automation)
- Google Chrome
- Garmin Connect account

## Deactivate Virtual Environment

```bash
deactivate
```
