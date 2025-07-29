from fastapi import FastAPI
from routers import submission, debug_router
from utils.logger import get_logger

logger = get_logger("main_file_logger")

app = FastAPI()

logger.info("Starting FastAPI application")
app.include_router(submission.router, prefix="/form", tags=["submission"])

app.include_router(debug_router.router)

