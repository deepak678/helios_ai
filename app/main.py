import logging
from fastapi import FastAPI
from app.routes.analyze import router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("helios_ai")

app = FastAPI(
    title="Helios AI Non-Financial Risk Intelligence",
    description="Analyze operational risk issues with clustering, duplicate detection, and hygiene scoring.",
    version="0.1.0",
)

app.include_router(analyze_router)


@app.get("/health")
def health_check():
    """Health endpoint for quick readiness checks."""
    logger.info("Health check requested")
    return {"status": "ok", "service": "helios_ai"}
