"""
FastAPI routes for task management
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, HealthResponse
from auth import extract_user_id
from logger import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)
router = APIRouter()


def get_current_user_id(x_init_data: str = Header(None)) -> int:
    """Dependency to get authenticated user ID"""
    if not x_init_data:
        logger.warning("Missing X-Init-Data header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Init-Data header"
        )
    return extract_user_id(x_init_data)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check called")
    return HealthResponse(status="ok", version="1.0.0")


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new task"""
    try:
        logger.debug(f"Creating task for user {user_id}: {task.text[:50]}")
        
        db_task = Task(
            user_id=user_id,
            text=task.text,
            reminder_date=task.reminder_date,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        logger.info(f"Task created: id={db_task.id}, user_id={user_id}, text={db_task.text[:50]}")
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating task for user {user_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to create task") from e


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int = Depends(get_current_user_id),
    completed: bool = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get user's tasks with optional filtering"""
    try:
        logger.debug(f"Fetching tasks for user {user_id} (skip={skip}, limit={limit}, completed={completed})")
        
        query = db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc())
        
        if completed is not None:
            query = query.filter(Task.completed == completed)
        
        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        completed_count = db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == True
        ).count()
        
        logger.debug(f"Retrieved {len(tasks)} tasks for user {user_id} ({completed_count} completed)")
        return TaskListResponse(tasks=tasks, total=total, completed_count=completed_count)
    except Exception as e:
        logger.error(f"Error fetching tasks for user {user_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to fetch tasks") from e


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific task"""
    logger.debug(f"Fetching task {task_id} for user {user_id}")
    
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise NotFoundError("Task")
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update a task"""
    try:
        logger.debug(f"Updating task {task_id} for user {user_id}")
        
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise NotFoundError("Task")

        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"Task updated: id={task_id}, user_id={user_id}")
        return task
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Error updating task {task_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to update task") from e


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    try:
        logger.debug(f"Deleting task {task_id} for user {user_id}")
        
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise NotFoundError("Task")

        db.delete(task)
        db.commit()
        
        logger.info(f"Task deleted: id={task_id}, user_id={user_id}")
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to delete task") from e


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Mark a task as completed"""
    try:
        logger.debug(f"Completing task {task_id} for user {user_id}")
        
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise NotFoundError("Task")

        task.completed = True
        db.commit()
        db.refresh(task)
        
        logger.info(f"Task completed: id={task_id}, user_id={user_id}")
        return task
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Error completing task {task_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to complete task") from e
