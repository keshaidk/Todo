from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Схема для проверки здоровья API
class HealthResponse(BaseModel):
    status: str = "ok"

# Схема для создания задачи (то, что прилетает от клиента)
class TaskCreate(BaseModel):
    text: str = Field(..., max_length=500)
    reminder_date: Optional[datetime] = None

# Схема для обновления задачи
class TaskUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    reminder_date: Optional[datetime] = None

# Схема ответа для одной задачи (то, что мы отдаем клиенту)
class TaskResponse(BaseModel):
    id: int
    user_id: str
    text: str
    completed: bool
    reminder_sent: bool
    reminder_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Схема для списка задач
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
