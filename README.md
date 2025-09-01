# FastAPI Backend for Flipper

This adds a modular FastAPI backend with routes split by feature. A dedicated `subghz` router manages scripts located in the `subghz/` folder.

## Structure

- `app/main.py` — FastAPI app and router wiring
- `app/api/routes/health.py` — Health endpoint
- `app/api/routes/subghz.py` — SubGHz routes (list and execute scripts)
- `app/services/subghz_service.py` — Business logic for discovering and running scripts
- `app/schemas/subghz.py` — Pydantic models
- `app/core/config.py` — Settings (directory, timeouts)
- `subghz/` — Folder with scripts to list and run

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open docs at http://127.0.0.1:8000/docs

## Configuration

- `SUBGHZ_DIR` (env): path to scripts folder. Default: `./subghz`
- `SCRIPT_TIMEOUT_SEC` (env): execution timeout (default 60)

## API

- GET `/health` → `{ "status": "ok" }`
- GET `/subghz/scripts` → list available scripts (`.py`, `.sh`)
- POST `/subghz/scripts/{name}/run` with body `{ "args": ["--flag", "value"] }` → executes script and returns stdout/stderr and exit code

## Notes

- Only `.py` and `.sh` are allowed by default (adjust in `app/services/subghz_service.py`).
- Scripts run with working directory set to `SUBGHZ_DIR`.
