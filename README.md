# Flipper SubGHz API

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Lightweight FastAPI backend for controlling Flipper Zero SubGHz transmissions over USB. List and execute `.sub` files on a connected Flipper device via HTTP API.

## Features

- **List Scripts** -- discover all `.sub` files in `/ext/subghz` on Flipper device
- **Run Transmissions** -- execute SubGHz scripts with configurable repeat count and RF device index
- **Automatic Retry** -- falls back to non-recursive listing if initial scan fails
- **Interactive Docs** -- auto-generated Swagger UI at `/docs`
- **Local Script Runner** -- execute `.py`/`.sh`/`.sub` scripts from local directory
- **Path Traversal Protection** -- safe file path resolution prevents directory escape
- **Structured Logging** -- loguru integration with configurable log levels

## Architecture

```
Flipper/
├── app/
│   ├── main.py                 # FastAPI app, root redirect, logging setup
│   ├── core/
│   │   └── config.py           # pydantic-settings configuration
│   ├── api/routes/
│   │   ├── subghz.py           # SubGHz device endpoints
│   │   └── health.py           # Health check endpoint
│   ├── services/
│   │   ├── flipper_service.py  # Flipper device interaction (USB serial)
│   │   └── subghz_service.py   # Local script listing and execution
│   └── schemas/
│       └── subghz.py           # Pydantic request/response models
├── flipper_cli.py              # Low-level Flipper serial protocol (pyserial)
├── Makefile                    # Dev/prod server management
└── requirements.txt            # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.10+
- Flipper Zero connected via USB
- Linux (serial port detection via `/dev/serial/by-id/`)

### Installation

```bash
git clone https://github.com/mazamaka/Flipper.git
cd Flipper
make install
```

### Run Server

```bash
# Development (with auto-reload)
make up

# Production
make up-prod
```

Server starts at `http://127.0.0.1:8000`. Open `/docs` for interactive API explorer.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/subghz/scripts` | List all `.sub` files on Flipper device |
| `POST` | `/subghz/scripts/{name}/run` | Execute a script by name |
| `GET` | `/health` | Health check |

### List Scripts

```bash
curl http://localhost:8000/subghz/scripts
```

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

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `repeat` | int | 1-100 | 1 | Number of transmission repeats |
| `device` | int | 0-3 | 0 | RF device index |

## Configuration

Create `.env` file in project root:

```env
LOG_LEVEL=INFO
SUBGHZ_RECURSIVE=False
SUBGHZ_ALLOWED_EXTS=.py,.sh,.sub
SCRIPT_TIMEOUT_SEC=60
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | str | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SUBGHZ_RECURSIVE` | bool | `False` | Recursive directory search for scripts |
| `SUBGHZ_ALLOWED_EXTS` | str | `.py,.sh` | Comma-separated allowed script extensions |
| `SCRIPT_TIMEOUT_SEC` | int | `60` | Script execution timeout in seconds |

## Makefile Targets

```bash
make help      # Show available targets
make install   # Create venv and install dependencies
make up        # Start dev server with auto-reload
make up-prod   # Start production server (0.0.0.0:8000)
make down      # Stop server
make clean     # Remove __pycache__ directories
```

## Notes

- Script names in API responses omit the `.sub` extension
- File matching is case-insensitive
- Device paths are absolute (e.g., `/ext/subghz/Win_stop.sub`)
- Requires `flipper_cli.py` module for USB serial communication
- Serial connection uses 230400 baud with exclusive port access
- Automatically frees port if occupied by qFlipper or other processes

## Author

**Maksym Babenko**
- GitHub: [@mazamaka](https://github.com/mazamaka)
- Telegram: [@Mazamaka](https://t.me/Mazamaka)

## License

MIT
