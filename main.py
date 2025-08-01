from fastapi import FastAPI
from routers import submission, debug_router
from utils.logger import get_logger
from utils.exception_handlers import register_exception_handlers

logger = get_logger("main_file_logger")

app = FastAPI(
    title="CBS Submission System",
    description="A FastAPI-based submission processing system that handles form submissions with complex table relationships and foreign key mappings.",
    version="1.0.0"
)

logger.info("Starting FastAPI application")

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(submission.router, prefix="/form", tags=["submission"])
app.include_router(debug_router.router)

