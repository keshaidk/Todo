from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

from sqlalchemy import Integer, String, Boolean, DateTime, Index, select, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.engine import create_engine

# 1. Настройка базы данных (для примера используем SQLite)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Функция получения текущего времени с UTC (замена устаревшему utcnow)
def get_utc_now():
    return datetime.now(timezone.utc)

# 2. Описание декларативной базы SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    # Использование Mapped автоматически типизирует поля и обрабатывает Optional как nullable
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Поле даты теперь принимает полноценный datetime (или None)
    reminder_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True, default=None)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    __table_args__ = (
        Index("ix_tasks_reminder", "user_id", "reminder_date", "reminder_sent", "completed"),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, text={self.text[:20]}, completed={self.completed})>"


# 3. Pydantic Схемы (Валидация данных)
class TaskEdit(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    reminder_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    text: str
    completed: bool
    reminder_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        # Позволяет Pydantic автоматически читать данные из объектов SQLAlchemy
        from_attributes = True


# 4. Бизнес-логика (ORM операции вместо сырого SQL)

def create_task_db(user_id: str, text: str, reminder_date: Optional[datetime] = None) -> TaskResponse:
    db = get_db()
    db_task = Task(
        user_id=user_id,
        text=text,
        reminder_date=reminder_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return TaskResponse.model_validate(db_task)


def get_tasks_db(user_id: str) -> List[TaskResponse]:
    db = get_db()
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = db.scalars(stmt).all()
    return [TaskResponse.model_validate(t) for t in tasks]


def complete_task_db(task_id: int, user_id: str) -> Optional[TaskResponse]:
    db = get_db()
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = db.scalars(stmt).first()
    
    if not db_task:
        return None
        
    db_task.completed = not db_task.completed
    db_task.updated_at = get_utc_now()
    db.commit()
    db.refresh(db_task)
    return TaskResponse.model_validate(db_task)


def edit_task_db(task_id: int, user_id: str, updates: TaskEdit) -> Optional[TaskResponse]:
    db = get_db()
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = db.scalars(stmt).first()
    
    if not db_task:
        return None

    if updates.text is not None:
        db_task.text = updates.text
    if updates.completed is not None:
        db_task.completed = updates.completed
    if updates.reminder_date is not None:
        db_task.reminder_date = updates.reminder_date
        db_task.reminder_sent = False  # Сбрасываем флаг отправки при изменении даты

    db_task.updated_at = get_utc_now()
    db.commit()
    db.refresh(db_task)
    return TaskResponse.model_validate(db_task)


def delete_task_db(task_id: int, user_id: str) -> bool:
    db = get_db()
    stmt = delete(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0


def get_due_reminders() -> List[TaskResponse]:
    """Получить задачи, для которых пришло время напоминания и они еще не отправлены."""
    db = get_db()
    now = get_utc_now()
    stmt = select(Task).where(
        Task.reminder_date.is_not(None),
        Task.reminder_date <= now,
        Task.reminder_sent == False,
        Task.completed == False
    )
    tasks = db.scalars(stmt).all()
    return [TaskResponse.model_validate(t) for t in tasks]


def mark_reminder_sent(task_id: int) -> None:
    db = get_db()
    stmt = update(Task).where(Task.id == task_id).values(reminder_sent=True)
    db.execute(stmt)
    db.commit()
