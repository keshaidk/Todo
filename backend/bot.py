"""
Telegram Bot for To-Do Mini App
Handles /start command and sends push reminders
"""
import logging
from datetime import datetime, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

from config import settings
from database import SessionLocal
from models import Task

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с кнопкой запуска Web App"""
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
    """Отправляет сообщение со справкой"""
    if not update.message:
        return

    help_text = (
        "<b>Available Commands:</b>\n\n"
        "/start - Open the To-Do app\n"
        "/help - Show this message\n\n"
        "💡 Tip: All task management happens in the app!"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая задача для проверки и отправки напоминаний"""
    app = context.application
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Находим невыполненные задачи, время напоминания которых пришло
        tasks = db.query(Task).filter(
            Task.reminder_date <= now,
            Task.reminder_sent == False,
            Task.completed == False,
        ).all()
        
        for task in tasks:
            try:
                message = f"🔔 <b>Reminder!</b>\n\n📝 {task.text}"
                await app.bot.send_message(
                    chat_id=int(task.user_id), # Преобразуем в int для Telegram API
                    text=message,
                    parse_mode="HTML"
                )
                task.reminder_sent = True
                logger.info(f"Reminder sent for task {task.id} to user {task.user_id}")
            except TelegramError as e:
                logger.error(f"Failed to send reminder to {task.user_id}: {e}")
                # Если пользователь заблокировал бота, помечаем, чтобы не пытаться бесконечно
                if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                    task.reminder_sent = True
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in check_reminders: {e}")
    finally:
        db.close()


async def send_completion_notification(bot, user_id: str, task_text: str):
    """Отправляет уведомление, когда задача выполнена (вызывается из API)"""
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text=f'✅ Задача "<b>{task_text}</b>" выполнена!',
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Failed to send completion notification: {e}")


async def set_bot_commands(app: Application):
    """Настройка меню команд бота"""
    commands = [
        BotCommand("start", "Open To-Do app"),
        BotCommand("help", "Show help"),
    ]
    await app.bot.set_my_commands(commands)


async def post_init(app: Application):
    """Инициализация после старта бота"""
    await set_bot_commands(app)
    logger.info("Bot commands initialized")


def create_bot() -> Application:
    """Создание и конфигурация инстанса приложения бота"""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT_TOKEN не установлен в файле конфигурации или .env")
    
    # Инициализируем приложение
    app = Application.builder().token(settings.BOT_TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Добавляем callback инициализации
    app.post_init = post_init

    # Настраиваем фоновую проверку напоминаний каждые 30 секунд через встроенный job_queue
    if app.job_queue:
        app.job_queue.run_repeating(check_reminders, interval=30, first=10)
    else:
        logger.warning("JobQueue недоступен. Проверьте, установлен ли пакет python-telegram-bot[job-queue]")

    return app
