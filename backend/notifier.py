"""
Sends Telegram notifications via the Bot API.
Used by the FastAPI server to notify users of task completions.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_completion_notification(user_id: str, task_text: str):
    """Send a notification when a task is completed."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.info(f"[DEV] Would notify {user_id}: task '{task_text}' completed")
        return

    message = f'✅ Задача "<b>{task_text}</b>" выполнена! 🎉'

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": user_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
            )
            if response.status_code != 200:
                logger.error(f"Failed to send notification: {response.text}")
            else:
                logger.info(f"Completion notification sent to {user_id}")
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
