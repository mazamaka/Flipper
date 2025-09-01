from fastapi import APIRouter, HTTPException

from app.schemas.subghz import (
    DeviceScriptListResponse,
    DeviceRunRequest,
)
from app.services.flipper_service import (
    list_device_subghz,
    run_device_script,
)

router = APIRouter()


@router.get("/scripts", response_model=DeviceScriptListResponse, summary="List .sub scripts on Flipper device under /ext/subghz")
def get_device_scripts():
    return list_device_subghz()


@router.post("/scripts/{name}/run", summary="Run a .sub script by name on the Flipper device")
def run_device_by_name(name: str, repeat: int = 1, device: int = 0):
    listing = list_device_subghz()
    match = next((x for x in listing.items if x.name == name or x.name == f"{name}.sub"), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Script not found: {name}")
    req = DeviceRunRequest(path=match.path, repeat=repeat, device=device)
    result = run_device_script(req)
    return {"result": result}
