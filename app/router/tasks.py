from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import User,Task
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate,TaskStatusUpdate,UserResponse,TaskResponse
from app.dependencies import get_current_user, require_admin, require_user
from app.websocket import websocket_manager ,WebSocket,WebSocketDisconnect

router = APIRouter()
# WebSocket endpoint to connect users for real-time updates
@router.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_current_user)):
    await websocket_manager.connect(websocket, user.id)

    try:
        while True:
            await websocket.receive_text()  # Keep connection open
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user.id)


# Function to send task updates via WebSocket to a specific user
async def notify_user_update(user_id: int, task_data: TaskResponse):
    await websocket_manager.send_personal_message(task_data.dict(), user_id)

# Admin-only routes
@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    new_task = Task(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    await notify_user_update(new_task.assigned_to, TaskResponse.from_orm(new_task))
    
    return {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "completed": getattr(new_task, "completed", False),  # Default to False if not defined
        "priority": new_task.priority,
        "due_date": new_task.due_date.isoformat() if new_task.due_date else None,  # Convert datetime to string
        "assigned_to": new_task.assigned_to,  # Return ID if expecting an integer in TaskResponse
        "status": new_task.status
    }

@router.put("/tasks/{task_id}", response_model=TaskUpdate)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    await notify_user_update(db_task.assigned_to, TaskResponse.from_orm(db_task))
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

# User-only route to update task status
@router.patch("/tasks/{task_id}/status", response_model=TaskStatusUpdate)
def update_task_status(task_id: int, status: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task

# Common route for both Admin and User to view tasks
@router.get("/tasks/", response_model=List[TaskResponse])
def get_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.assigned_to==user.id).offset(skip).limit(limit).all()
    tasks_response = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date.isoformat() if task.due_date else None,  # Convert to string
            assigned_to=task.assigned_to,
            status=task.status
        )
        for task in tasks
    ]
    
    return tasks_response

# for addmin to view all the task they have assigned 

@router.get("/tasks/admin/", response_model=List[TaskResponse])
def get_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    tasks_response = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date.isoformat() if task.due_date else None,  # Convert to string
            assigned_to=task.assigned_to,
            status=task.status
        )
        for task in tasks
    ]
    
    return tasks_response

@router.get("/tasks/{task_id}",response_model=List[TaskResponse])
def get_task_by_id( task_id: int,skip: int = 0, limit: int = 10,db: Session= Depends(get_db),user: User=Depends(get_current_user)):
    tasks=db.query(Task).filter(Task.id==task_id,Task.assigned_to==user.id).offset(skip).limit(limit).all()
    # if not tasks:
    #     raise HTTPException(status_code=404,detail="Task you are looking for not found")
    tasks_response = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date.isoformat() if task.due_date else None,  # Convert to string
            assigned_to=task.assigned_to,
            status=task.status
        )
        for task in tasks
    ]
    return tasks_response

# for admin - to view all priority tasks

@router.get("/tasks",response_model=List[TaskResponse])
def get_task_by_priority( priority: str,skip: int = 0, limit: int = 10,db: Session= Depends(get_db),user: User=Depends(require_admin)):
    tasks=db.query(Task).filter(Task.priority==str(priority.strip())).offset(skip).limit(limit).all()
    print( db.query(Task).filter(Task.priority.ilike(priority)).all())
    # if not tasks:
    #     raise HTTPException(status_code=404,detail="Task you are looking for not found")
    tasks_response = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date.isoformat() if task.due_date else None,  # Convert to string
            assigned_to=task.assigned_to,
            status=task.status
        )
        for task in tasks
    ]
    return tasks_response

# for users - to view their tasks with their priority choices
@router.get("/tasks/user/",response_model=List[TaskResponse])
def get_task_by_priority( priority: str,skip: int = 0, limit: int = 10,db: Session= Depends(get_db),user: User=Depends(require_user)):
    tasks=db.query(Task).filter(Task.priority==str(priority.strip()),Task.assigned_to==user.id).offset(skip).limit(limit).all()
    print( db.query(Task).filter(Task.priority.ilike(priority),Task.assigned_to==user.id).all())
    # if not tasks:
    #     raise HTTPException(status_code=404,detail="Task you are looking for not found")
    tasks_response = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date.isoformat() if task.due_date else None,  # Convert to string
            assigned_to=task.assigned_to,
            status=task.status
        )
        for task in tasks
    ]
    return tasks_response
