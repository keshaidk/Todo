"""
Database models using SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    text = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False, index=True)
    reminder_date = Column(DateTime, nullable=True, index=True)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for efficient reminder queries
    __table_args__ = (
        Index("ix_tasks_reminder", "user_id", "reminder_date", "reminder_sent", "completed"),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, text={self.text}, completed={self.completed})>"
    reminder_date: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    user_id: str
    text: str
    completed: bool
    reminder_date: Optional[str] = None
    created_at: str
    updated_at: str


def row_to_task(row) -> TaskResponse:
    return TaskResponse(
        id=row["id"],
        user_id=row["user_id"],
        text=row["text"],
        completed=bool(row["completed"]),
        reminder_date=row["reminder_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_task_db(user_id: str, text: str, reminder_date: Optional[str]) -> TaskResponse:
    conn = get_db()
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        "INSERT INTO tasks (user_id, text, completed, reminder_date, created_at, updated_at) VALUES (?, ?, 0, ?, ?, ?)",
        (user_id, text, reminder_date, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return row_to_task(row)


def get_tasks_db(user_id: str) -> list[TaskResponse]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [row_to_task(r) for r in rows]


def complete_task_db(task_id: int, user_id: str) -> Optional[TaskResponse]:
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    ).fetchone()
    if not task:
        conn.close()
        return None
    new_status = 0 if task["completed"] else 1
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE tasks SET completed = ?, updated_at = ? WHERE id = ?",
        (new_status, now, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_task(row)


def edit_task_db(task_id: int, user_id: str, updates: TaskEdit) -> Optional[TaskResponse]:
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    ).fetchone()
    if not task:
        conn.close()
        return None

    fields = []
    values = []
    if updates.text is not None:
        fields.append("text = ?")
        values.append(updates.text)
    if updates.completed is not None:
        fields.append("completed = ?")
        values.append(1 if updates.completed else 0)
    if updates.reminder_date is not None:
        fields.append("reminder_date = ?")
        fields.append("reminder_sent = 0")
        values.append(updates.reminder_date)

    if fields:
        now = datetime.utcnow().isoformat()
        fields.append("updated_at = ?")
        values.append(now)
        values.extend([task_id, user_id])
        conn.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id = ? AND user_id = ?",
            values,
        )
        conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_task(row)


def delete_task_db(task_id: int, user_id: str) -> bool:
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_due_reminders() -> list[dict]:
    """Get tasks that have reminders due and not yet sent."""
    conn = get_db()
    now = datetime.utcnow().isoformat()
    rows = conn.execute(
        """
        SELECT * FROM tasks
        WHERE reminder_date IS NOT NULL
          AND reminder_date <= ?
          AND reminder_sent = 0
          AND completed = 0
        """,
        (now,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_reminder_sent(task_id: int):
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET reminder_sent = 1 WHERE id = ?",
        (task_id,),
    )
    conn.commit()
    conn.close()
