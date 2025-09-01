# Flipper SubGHz API (FastAPI)

FastAPI backend to list and run SubGHz `.sub` files directly on a connected Flipper device.

The API queries the device storage under `/ext/subghz` and can start transmissions from a selected `.sub` file.

## Structure

- `app/main.py` — FastAPI app and router wiring
- `app/api/routes/subghz.py` — SubGHz routes (device listing and run-by-name)
- `app/services/flipper_service.py` — Interaction with the Flipper via `flipper_cli`
- `app/schemas/subghz.py` — Pydantic models for device scripts
- `app/core/config.py` — App settings (logging, etc.)

Removed: local script execution, health routes, and local `subghz/` folder.

## Requirements

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ensure your Flipper is connected and accessible by `flipper_cli` (provided in this repo as a Python module wrapper).

## Run

```bash
uvicorn app.main:app --reload
```

Open docs at http://127.0.0.1:8000/docs

## API

- GET `/subghz/scripts`
  - Lists all `.sub` files found on the device under `/ext/subghz` (recursively)
  - Response item shape:
    ```json
    { "name": "Win_stop", "path": "/ext/subghz/Win_stop.sub" }
    ```
    Where `name` has no `.sub` suffix, and `path` is the full device path.

- POST `/subghz/scripts/{name}/run?repeat=1&device=0`
  - Starts the selected SubGHz file by name (`Win_stop` or `Win_stop.sub`)
  - Query params:
    - `repeat` — number of repeats (default 1)
    - `device` — RF device index (default 0)

## Notes

- Listing uses `storage list -r /ext/subghz` with a fallback to non-recursive and parses `.sub` files case-insensitively.
- Names in the list are returned without the `.sub` extension for convenience.
