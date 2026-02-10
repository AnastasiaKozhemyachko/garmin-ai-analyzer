# Garmin AI Analyzer

Automated Garmin health data collection with AI-powered analysis for morning and evening reports.

## Features

- Morning report: Sleep quality, recovery, and readiness assessment
- Evening report: Daily activity, stress, and sleep recommendations
- Automatic ChatGPT upload with custom prompts
- Secure session management

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install garth
```

## Usage

### Evening Report
```bash
python3 run_evening.py
```
Collects daily activity data and uploads to ChatGPT for evening analysis.

### Morning Report
```bash
python3 run_morning.py
```
Collects recovery metrics and uploads to ChatGPT for morning readiness assessment.

## Configuration

Edit `utils/config.py` to customize:

- `PROMPT_MORNING` / `PROMPT_EVENING` - Analysis prompts
- `DATA_TYPES_MORNING` / `DATA_TYPES_EVENING` - Metrics to collect
- `CHATGPT_URL` - ChatGPT URL
- `DELAY_MS`, `FINDER_WAIT_MS`, `UPLOAD_WAIT_MS` - Timing settings

## Project Structure

```
├── run_evening.py          # Evening workflow
├── run_morning.py          # Morning workflow
├── scripts/
│   ├── collect_evening.py  # Evening data collection
│   ├── collect_morning.py  # Morning data collection
│   ├── upload_evening.py   # Evening upload
│   └── upload_morning.py   # Morning upload
└── utils/
    ├── config.py           # Configuration
    ├── collection_utils.py # Shared collection functions
    └── upload_utils.py     # Shared upload functions
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
