from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger
import sys

from app.api.routes.subghz import router as subghz_router
from app.core.config import settings

app = FastAPI(title="Flipper API")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Routers
app.include_router(subghz_router, prefix="/subghz", tags=["subghz"]) 

@app.on_event("startup")
def setup_logging():
    # Configure Loguru based on settings
    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL, enqueue=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
