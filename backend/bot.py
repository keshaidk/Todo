"""
Telegram Bot for To-Do Mini App.
Handles /start command and sends push reminders via APScheduler.
"""
import os
import asyncio
import logging
from datetime import datetime, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models import init_db, get_due_reminders, mark_reminder_sent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://your-domain.com")

# Scheduler for reminders
scheduler = AsyncIOScheduler(timezone=timezone.utc)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with a button to open the Web App."""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="📱 Открыть To-Do App",
                web_app=WebAppInfo(url=f"{WEB_APP_URL.rstrip('/')}/todo"),
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ О боте",
                callback_data="about",
            )
        ],
    ])

    await update.message.reply_text(
        "👋 <b>Привет!</b> Я твой To-Do бот-помощник!\n\n"
        "📝 Создавай задачи, ставь напоминания и получай уведомления прямо в Telegram.\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение:",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the about button."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ <b>To-Do Telegram Mini App</b>\n\n"
        "📝 <b>Возможности:</b>\n"
        "• Создание задач с напоминаниями\n"
        "• Группировка по датам\n"
        "• Поиск и фильтрация\n"
        "• Push-уведомления в Telegram\n"
        "• Тёмная и светлая темы\n\n"
        "Используй кнопку «📱 Открыть To-Do App» для запуска!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="📱 Открыть To-Do App",
                web_app=WebAppInfo(url=f"{WEB_APP_URL.rstrip('/')}/todo"),
            )]
        ]),
    )


async def check_reminders(app: Application):
    """Check for due reminders and send them via the bot."""
    try:
        tasks = get_due_reminders()
        for task in tasks:
            user_id = task["user_id"]
            task_id = task["id"]
            text = task["text"]
            reminder_date = task.get("reminder_date")

            # Format reminder time
            time_str = ""
            if reminder_date:
                try:
                    dt = datetime.fromisoformat(reminder_date)
                    time_str = f" на {dt.strftime('%d.%m.%Y %H:%M')}"
                except ValueError:
                    pass

            message = f"🔔 <b>Напоминание!</b>\n\n📝 {text}{time_str}\n\nНе забудь выполнить задачу!"

            try:
                await app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="HTML",
                )
                logger.info(f"Reminder sent to {user_id} for task {task_id}")
            except Exception as e:
                logger.error(f"Failed to send reminder to {user_id}: {e}")
                # Don't mark as sent if failed - but avoid infinite retries
                if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                    mark_reminder_sent(task_id)
                continue

            mark_reminder_sent(task_id)
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")


async def send_completion_notification(app: Application, user_id: str, task_text: str):
    """Send a notification when a task is completed. Called from API or webhook."""
    try:
        await app.bot.send_message(
            chat_id=user_id,
            text=f'✅ Задача "<b>{task_text}</b>" выполнена! 🎉',
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Failed to send completion notification: {e}")


def main():
    """Run the bot."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not set! Set the BOT_TOKEN environment variable.")
        return

    # Initialize DB
    init_db()

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(about_callback, pattern="^about$"))

    # Schedule reminder checks every 30 seconds
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(seconds=30),
        args=[app],
        id="check_reminders",
        name="Check for due reminders every 30s",
        replace_existing=True,
    )
    scheduler.start()

    logger.info("✅ Bot started! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
