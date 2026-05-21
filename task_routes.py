from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import Task
from schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: db_dependency, current_user: user_dependency):
    try:
        new_task = Task(**task.model_dump(), user_id=current_user["id"])
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create task")

@router.get("/", response_model=list[TaskResponse])
def get_tasks(db: db_dependency, current_user: user_dependency):
    try:
        return db.query(Task).filter(Task.user_id == current_user["id"]).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve tasks")

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: db_dependency, current_user: user_dependency):
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["id"]).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve task")

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: db_dependency, current_user: user_dependency):
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["id"]).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update task")

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: db_dependency, current_user: user_dependency):
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["id"]).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        db.delete(task)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete task")