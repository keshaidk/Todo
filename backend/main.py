import os
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_all_objects, Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com/todo")
DATABASE_URL = "sqlite:///./todo.db"

# --- Database ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    text = Column(String)
    completed = Column(Boolean, default=False)
    reminder_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- Pydantic Models ---
class TaskCreate(BaseModel):
    text: str
    reminder_date: Optional[datetime] = None
    user_id: int

class TaskUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    reminder_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    text: str
    completed: bool
    reminder_date: Optional[datetime]
    created_at: datetime
    class Config:
        from_attributes = True

# --- FastAPI App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create_task", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/get_tasks/{user_id}", response_model=List[TaskResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    return db.query(TaskModel).filter(TaskModel.user_id == user_id).all()

@app.post("/complete_task/{task_id}")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    return {"status": "ok"}

@app.delete("/delete_task/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "ok"}

@app.put("/edit_task/{task_id}")
def edit_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

# --- Telegram Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Open To-Do App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Manage your tasks and reminders with the button below:",
        reply_markup=reply_markup
    )

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))

# --- Scheduler for Reminders ---
def check_reminders():
    db = SessionLocal()
    now = datetime.utcnow()
    # Find uncompleted tasks with reminders in the past that haven't been notified (you might want a 'notified' flag)
    # For simplicity, we just check tasks due in the last minute
    tasks = db.query(TaskModel).filter(
        TaskModel.completed == False,
        TaskModel.reminder_date <= now
    ).all()
    
    for task in tasks:
        # Send message via bot
        try:
            # Note: This is synchronous inside the scheduler, 
            # for production use an async scheduler or a separate process.
            import asyncio
            asyncio.run(bot_app.bot.send_message(
                chat_id=task.user_id,
                text=f"⏰ Reminder: {task.text}"
            ))
            # Optionally mark as notified
            task.completed = True # Or some other logic
            db.commit()
        except Exception as e:
            print(f"Error sending reminder: {e}")
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    # Start bot in the background
    # Note: In a real production setup, you'd run the bot and the web app separately
    import threading
    threading.Thread(target=bot_app.run_polling, daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
