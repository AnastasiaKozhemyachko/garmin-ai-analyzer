# 🏃‍♀️ Garmin AI Analyzer

Automated Garmin health data collection + AI-powered analysis via ChatGPT.  
Pulls data from your watch, processes it, and uploads to ChatGPT with a tailored prompt.

## Which script to run?

| When / Why | Command | What you get |
|---|---|---|
| 🌅 **Morning after waking up** | `python3 run_morning.py` | Sleep quality, training readiness, daily recommendations |
| 🌙 **Evening before bed** | `python3 run_evening.py` | Day summary, stress, energy, bedtime advice |
| 🏋️ **After a workout** | `python3 run_activity.py` | Detailed workout breakdown (pace, HR zones, splits) |
| 📊 **Once a week** | `python3 run_weekly.py` | Weekly trends: sleep, HRV, stress, training load, weight |
| 🩺 **Feeling off** | `python3 run_health.py` | Illness / overtraining check (🟢🟡🔴 status) |
| 📅 **Need a training plan** | `python3 run_training.py` | Load analysis + 3–5 day plan based on recovery |
| 😴 **Sleep issues** | `python3 run_sleep.py` | Deep 14-day sleep analysis: rhythm, stages, efficiency |
| 📈 **Track progress** | `python3 run_progress.py` | Progress per activity type (walking, jump rope, cycling, pilates) |

> Each script: collects Garmin data → processes it → opens ChatGPT → pastes file + prompt.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install garth
```

First run will ask for your Garmin Connect email and password. Session is saved for future runs.

## Collect data only (no ChatGPT)

To get JSON files without uploading to ChatGPT:

```bash
python3 scripts/collect_morning.py      # → results/morning_data.json
python3 scripts/collect_evening.py      # → results/evening_data.json
python3 scripts/collect_latest_activity.py  # → results/latest_activity.json
python3 scripts/collect_weekly.py       # → results/weekly_data.json
python3 scripts/collect_health.py       # → results/health_data.json
python3 scripts/collect_training.py     # → results/training_data.json
python3 scripts/collect_sleep.py        # → results/sleep_data.json
python3 scripts/collect_progress.py     # → results/progress_data.json
```

## What each report collects

### 🌅 Morning report (`run_morning.py`)
Sleep (3d), HRV (14d), heart rate (7d), readiness (3d), activities (3d), body battery (3d), stress (3d), steps (3d), daily summary (2d), training load (7d), weight (14d).

### 🌙 Evening report (`run_evening.py`)
Stress (2d), body battery (2d), activities (2d), sleep (2d), heart rate (3d), HRV (3d), steps (2d), daily summary (2d), training load (3d), readiness (2d).

### 🏋️ Activity analysis (`run_activity.py`)
Last 1 workout with detailed data: pace, HR zones, splits/laps, respiration, temperature, water loss, training effect, VO2max.

### 📊 Weekly report (`run_weekly.py`)
Sleep (8d), HRV (14d), heart rate (8d), stress (8d), body battery (8d), steps (8d), daily summary (8d), activities (10), readiness (8d), training load (14d), weight (30d).

### 🩺 Health check (`run_health.py`)
HRV (21d), heart rate (14d), sleep (7d), stress (7d), body battery (5d), readiness (7d), daily summary (7d), training load (14d), activities (7), weight (30d).

### 📅 Training plan (`run_training.py`)
Training load (21d), readiness (7d), activities (10), HRV (14d), heart rate (7d), body battery (3d), stress (3d), steps (7d), sleep (3d), weight (30d).

### 😴 Sleep analysis (`run_sleep.py`)
Sleep (14d), HRV (14d), heart rate (14d), stress (7d), body battery (5d), daily summary (7d).

### 📈 Activity progress (`run_progress.py`)
Last 50 activities + weight (30d). Groups by type and shows progress trends.

## Configuration

Edit `utils/config.py` to customize:
- **Prompts** — ChatGPT analysis prompts (`PROMPT_MORNING`, `PROMPT_EVENING`, etc.)
- **Data types** — which metrics to collect and how many days (`DATA_TYPES_MORNING`, etc.)
- **ChatGPT URL** — target chat link (`CHATGPT_URL`)
- **Timing** — automation delays (`DELAY_MS`, `UPLOAD_WAIT_MS`)

## Project structure

```
run_*.py                  — Full workflow: collect data + upload to ChatGPT
scripts/collect_*.py      — Data collection only → results/*.json
scripts/upload_*.py       — Upload from results/ to ChatGPT only
utils/config.py           — All settings and prompts
utils/collection_utils.py — Shared data collection logic
utils/upload_utils.py     — Shared upload logic (AppleScript)
utils/format_utils.py     — Date formatting and shared utilities
utils/*_slimmer.py        — Data processors (trim, compute metrics)
results/*.json            — Collected data files
```

## Requirements

- Python 3.7+
- macOS (AppleScript automation for Chrome)
- Google Chrome
- Garmin Connect account
