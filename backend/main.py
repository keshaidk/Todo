"""
Telegram To-Do Mini App - FastAPI Backend
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError

from config import settings
from database import init_db
from api import router as api_router
from bot import create_bot
from logger import (
    setup_logging,
    log_request,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    AppException,
)

# Configure logging
logger = setup_logging()

# Initialize bot
bot_app = create_bot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - startup and shutdown"""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Telegram To-Do API Server")
    logger.info(f"Environment: {settings.LOG_LEVEL}")
    logger.info(f"Bot Token: {'*' * 10}...{settings.BOT_TOKEN[-4:] if settings.BOT_TOKEN else 'MISSING'}")
    logger.info(f"Webapp URL: {settings.WEBAPP_URL}")
    
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Start bot polling in background
    try:
        await bot_app.initialize()
        await bot_app.start()
        logger.info("Telegram Bot started")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down server...")
    try:
        await bot_app.stop()
        await bot_app.shutdown()
        logger.info("Telegram Bot stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("To-Do API Server stopped")
    logger.info("=" * 60)


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add middleware - Order matters!
# Request logging
app.middleware("http")(log_request)

# Trust hosts that are behind a proxy
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware - restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Include routers
app.include_router(api_router, prefix="/api", tags=["tasks"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telegram To-Do Mini App API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
    )
