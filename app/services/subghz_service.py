import subprocess
import sys
import time
from pathlib import Path
from typing import List

from fastapi import HTTPException

from app.core.config import settings
from app.schemas.subghz import RunResponse, ScriptItem

from loguru import logger

def _allowed_exts() -> set[str]:
    exts = {e.strip().lower() for e in settings.SUBGHZ_ALLOWED_EXTS.split(",") if e.strip()}
    # ensure leading dot
    normalized = {e if e.startswith(".") else f".{e}" for e in exts}
    return normalized


def _safe_join(base: Path, name: str) -> Path:
    # Prevent path traversal
    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid script name")
    p = (base / name).resolve()
    if not str(p).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="Invalid script path")
    return p


def list_scripts() -> List[ScriptItem]:
    base = Path(settings.SUBGHZ_DIR).resolve()
    allowed = _allowed_exts()
    logger.debug("Listing scripts: base='{}', recursive={}, allowed_exts={}", base, settings.SUBGHZ_RECURSIVE, allowed)
    if not base.exists():
        logger.warning("SUBGHZ_DIR does not exist: {}", base)
        return []

    items: List[ScriptItem] = []
    iterable = base.rglob("*") if settings.SUBGHZ_RECURSIVE else base.iterdir()
    for entry in sorted(iterable):
        try:
            if entry.is_dir():
                if settings.SUBGHZ_RECURSIVE:
                    logger.trace("Skip directory (recursive walk continues): {}", entry)
                else:
                    logger.trace("Skip directory (non-recursive): {}", entry)
                continue
            if entry.name.startswith("."):
                logger.trace("Skip hidden file: {}", entry)
                continue
            if entry.suffix.lower() not in allowed:
                logger.trace("Skip by extension '{}': {}", entry.suffix, entry)
                continue
            items.append(ScriptItem(name=entry.name, path=str(entry)))
            logger.trace("Added script: {}", entry)
        except Exception as e:
            logger.exception("Error while processing {}: {}", entry, e)
    logger.debug("Total scripts found: {}", len(items))
    return items


def run_script(script_name: str, args: List[str]) -> RunResponse:
    base = Path(settings.SUBGHZ_DIR).resolve()
    path = _safe_join(base, script_name)

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Script not found: {script_name}")
    allowed = _allowed_exts()
    if path.suffix.lower() not in allowed:
        raise HTTPException(status_code=400, detail=f"Extension not allowed: {path.suffix}")

    if path.suffix == ".py":
        cmd = [sys.executable, "-u", str(path)] + list(args or [])
    elif path.suffix == ".sh":
        cmd = ["/bin/bash", str(path)] + list(args or [])
    else:
        raise HTTPException(status_code=400, detail="Unsupported script type")

    start = time.time()
    logger.info("Executing script: '{}' cmd={} cwd='{}' timeout={}s", script_name, cmd, base, settings.SCRIPT_TIMEOUT_SEC)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(base),
            capture_output=True,
            text=True,
            timeout=settings.SCRIPT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Script timed out after {settings.SCRIPT_TIMEOUT_SEC}s")

    duration_ms = int((time.time() - start) * 1000)
    logger.info("Script finished: '{}' exit_code={} duration_ms={}", script_name, proc.returncode, duration_ms)
    if proc.stderr:
        logger.debug("stderr (truncated to 2k): {}", proc.stderr[:2000])

    return RunResponse(
        script=script_name,
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_ms=duration_ms,
    )
