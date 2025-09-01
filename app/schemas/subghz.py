from typing import List

from pydantic import BaseModel, Field


class DeviceScriptItem(BaseModel):
    name: str  # without .sub extension
    path: str  # full device path, e.g. /ext/subghz/Win_stop.sub


class DeviceScriptListResponse(BaseModel):
    items: List[DeviceScriptItem]
    count: int


class DeviceRunRequest(BaseModel):
    path: str = Field(..., description="Full path on device, e.g. /ext/subghz/Win_stop.sub")
    repeat: int = Field(1, ge=1, le=100, description="Number of repeats")
    device: int = Field(0, ge=0, le=3, description="RF device index")
