"""
Combined runner: starts both FastAPI server and Telegram Bot in the same process.
"""
import os
import asyncio
import logging
from threading import Thread

import uvicorn

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_api(port: int):
    """Run FastAPI server in a separate thread."""
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def main():
    port = int(os.getenv("PORT", "8000"))

    # Start API in a background thread
    api_thread = Thread(target=run_api, args=(port,), daemon=True)
    api_thread.start()
    logger.info(f"🚀 API server starting on port {port}")

    # Run bot in the main thread
    from bot import main as bot_main
    bot_main()


if __name__ == "__main__":
    main()
