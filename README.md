# Garmin AI Analyzer

Automated Garmin health data collection with AI-powered analysis.

## Features

- Collects 14 days of Garmin health data
- Automatically uploads to ChatGPT for health analysis
- Supports both Python and JavaScript upload methods
- Secure session management with automatic resume

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install garth
```

## Quick Start

### Run Complete Workflow

```bash
python3 run_workflow.py
```

This will:
1. Authenticate with Garmin (or resume existing session)
2. Collect health data for the last 14 days
3. Save to `results/all_data.json`
4. Upload to ChatGPT for analysis

### Run Individual Steps

**Collect data only:**
```bash
python3 collect_garmin_data.py
```

**Upload to ChatGPT (Python):**
```bash
python3 upload_to_chatgpt.py results/all_data.json
```

**Upload to ChatGPT (JavaScript):**
```bash
npm install
node upload_to_chatgpt.js results/all_data.json
```

## Configuration

Edit `config.py` to customize:

- `DAYS_TO_COLLECT` - Number of days to collect (default: 14)
- `CHATGPT_URL` - ChatGPT URL
- `DELAY_MS`, `FINDER_WAIT_MS`, `UPLOAD_WAIT_MS` - Timing settings
- `ANALYSIS_PROMPT` - Custom analysis prompt
- `DATA_TYPES` - Garmin data types to collect

## Data Types Collected

- Activity, Body Battery, HRV, Heart Rate
- Sleep data, Stress levels, Steps
- Training status and readiness
- Weight, Hydration
- And more...

## How ChatGPT Upload Works

1. Opens file in Finder and copies it
2. Opens ChatGPT in Chrome
3. Pastes file to upload
4. Sends health analysis prompt

## Requirements

- Python 3.7+
- macOS (for AppleScript automation)
- Google Chrome
- Garmin Connect account

## Deactivate Virtual Environment

```bash
deactivate
```
