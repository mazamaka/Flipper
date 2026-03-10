# Flipper SubGHz API

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A lightweight FastAPI backend for controlling Flipper Zero SubGHz transmissions. List and execute `.sub` files on a connected Flipper device via HTTP API.

## Features

- **List Scripts** — Discover all `.sub` files in `/ext/subghz` on your Flipper device
- **Run Transmissions** — Execute SubGHz scripts with configurable repeat count and RF device index
- **Automatic Retry** — Falls back to non-recursive listing if initial scan fails
- **Interactive Docs** — Auto-generated Swagger UI at `/docs`
- **Structured Logging** — Built-in loguru integration for debugging

## Quick Start

### Prerequisites

Ensure your Flipper Zero is connected and accessible via USB.

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Server

```bash
uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`. Open `/docs` for interactive API explorer.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/subghz/scripts` | List all `.sub` files on device |
| `POST` | `/subghz/scripts/{name}/run` | Execute a script by name |

### List Scripts

```bash
curl http://localhost:8000/subghz/scripts
```

Response:
```json
{
  "items": [
    {"name": "Win_stop", "path": "/ext/subghz/Win_stop.sub"},
    {"name": "test_signal", "path": "/ext/subghz/test_signal.sub"}
  ],
  "count": 2
}
```

### Run Script

```bash
curl -X POST "http://localhost:8000/subghz/scripts/Win_stop/run?repeat=2&device=0"
```

**Query Parameters:**
- `repeat` — Number of transmission repeats (1-100, default: 1)
- `device` — RF device index (0-3, default: 0)

**Response:**
```json
{"result": "OK"}
```

## Configuration

Set environment variables in `.env` file:

```env
LOG_LEVEL=INFO
SUBGHZ_RECURSIVE=False
SCRIPT_TIMEOUT_SEC=60
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | str | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SUBGHZ_RECURSIVE` | bool | False | Recursive directory search |
| `SCRIPT_TIMEOUT_SEC` | int | 60 | Script execution timeout |

## Project Structure

```
app/
├── main.py                      # FastAPI app initialization
├── core/
│   └── config.py               # Settings & configuration
├── api/
│   └── routes/
│       └── subghz.py           # SubGHz endpoints
├── services/
│   └── flipper_service.py      # Device interaction logic
└── schemas/
    └── subghz.py               # Pydantic models
```

## Requirements

- Python 3.10+
- FastAPI 0.100+
- Uvicorn
- Pydantic
- pyserial (for USB communication)
- loguru (structured logging)

See `requirements.txt` for full list.

## Notes

- Script names in responses omit the `.sub` extension for convenience
- File matching is case-insensitive
- Device paths are absolute (e.g., `/ext/subghz/Win_stop.sub`)
- Requires `flipper_cli` module in Python path for device communication

## License

MIT
