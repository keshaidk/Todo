"""
Telegram Bot for To-Do Mini App
Handles /start command and sends push reminders
"""
import logging
from datetime import datetime, timedelta, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from database import SessionLocal
from models import Task

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with a button to open the Web App"""
    if not update.message:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="📱 Open To-Do App",
                web_app=WebAppInfo(url=settings.WEBAPP_URL),
            )
        ],
    ])

    await update.message.reply_text(
        "👋 <b>Welcome!</b> I'm your To-Do Bot Helper!\n\n"
        "📝 Create tasks, set reminders, and get notifications right in Telegram.\n\n"
        "Click the button below to open the app:",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    logger.info(f"Start command called by user {update.effective_user.id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    if not update.message:
        return

    help_text = (
        "<b>Available Commands:</b>\n\n"
        "/start - Open the To-Do app\n"
        "/help - Show this message\n"
        "/stats - Your statistics\n\n"
        "💡 Tip: All task management happens in the app!"
    )

    await update.message.reply_text(help_text, parse_mode="HTML")


async def check_reminders(app: Application):
    """Check for due reminders and send them via the bot"""
    try:
        db = SessionLocal()
        now = datetime.now(timezone.utc)
        
        # Find tasks with reminders due in next 5 minutes
        tasks = db.query(Task).filter(
            Task.reminder_date <= now,
            Task.reminder_sent == False,
            Task.completed == False,
        ).all()
        
        for task in tasks:
            try:
                message = f"🔔 <b>Reminder!</b>\n\n📝 {task.text}"
                await app.bot.send_message(
                    chat_id=task.user_id,
                    text=message,
                    parse_mode="HTML"
                )
                task.reminder_sent = True
                logger.info(f"Reminder sent for task {task.id}")
            except TelegramError as e:
                logger.error(f"Failed to send reminder to {task.user_id}: {e}")
        
        db.commit()
        db.close()
    except Exception as e:
        logger.error(f"Error in check_reminders: {e}")


async def set_bot_commands(app: Application):
    """Set bot commands menu"""
    commands = [
        BotCommand("start", "Open To-Do app"),
        BotCommand("help", "Show help"),
    ]
    await app.bot.set_my_commands(commands)


async def post_init(app: Application):
    """Initialize bot after creation"""
    await set_bot_commands(app)
    logger.info("Bot commands initialized")


def create_bot() -> Application:
    """Create and configure the bot application"""
    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")
    
    app = Application.builder().token(settings.BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Set post init callback
    app.post_init = post_init

    # Add job to check reminders every minute
    app.job_queue.run_repeating(check_reminders, interval=60, first=10)

    return app

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
