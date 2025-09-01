from typing import List
import re

from fastapi import HTTPException

from app.schemas.subghz import DeviceRunRequest, DeviceScriptItem, DeviceScriptListResponse

try:
    import flipper_cli
except Exception as e:
    flipper_cli = None


SUBGHZ_DIR_ON_DEVICE = "/ext/subghz"


def _require_cli():
    if flipper_cli is None:
        raise HTTPException(status_code=500, detail="flipper_cli module is not available")


def list_device_subghz() -> DeviceScriptListResponse:
    _require_cli()
    items: List[DeviceScriptItem] = []
    seen = set()
    # Attempt to list files via device CLI. Use recursive first, then fallback.
    try:
        with flipper_cli.Flipper() as f:
            for cmd in (f"storage list -r {SUBGHZ_DIR_ON_DEVICE}", f"storage list {SUBGHZ_DIR_ON_DEVICE}"):
                lines = f.cmd_all(cmd, read_sec=2.0)
                for ln in lines:
                    s = ln.strip()
                    if not s:
                        continue
                    # Find any token that looks like a .sub file
                    matches = re.findall(r"\S+\.sub", s, flags=re.IGNORECASE)
                    for m in matches:
                        fname = m.rsplit("/", 1)[-1]
                        name_no_ext = fname[:-4] if fname.lower().endswith(".sub") else fname
                        path = m if m.startswith("/") else f"{SUBGHZ_DIR_ON_DEVICE}/{fname}"
                        if fname.lower().endswith(".sub") and name_no_ext not in seen:
                            seen.add(name_no_ext)
                            items.append(DeviceScriptItem(name=name_no_ext, path=path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing device scripts: {e}")

    return DeviceScriptListResponse(items=items, count=len(items))


def run_device_script(req: DeviceRunRequest) -> str:
    _require_cli()
    try:
        with flipper_cli.Flipper() as f:
            res = f.sub_from_file(req.path, req.repeat, req.device)
            return res or "OK"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running device script: {e}")
