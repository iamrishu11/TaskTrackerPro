from app.extensions import db
from app.models import TaskManager
from datetime import datetime

def create_task(data):
    task = TaskManager(
        task_name=data.get("task_name"),
        description=data.get("description"),
        status=data.get("status", False),
        priority=data.get("priority", "LOW"),
        created_at=datetime.now(),
        user_id=data["assigned_user"]
    )
    db.session.add(task)
    db.session.commit()
    return task

def get_all_tasks():
    return TaskManager.query.filter_by(status=True).all()

def get_task_by_id(task_id):
    return TaskManager.query.get(task_id)

def update_task(task_id, data):
    task = TaskManager.query.get(task_id)
    if not task:
        return None
    for key, value in data.items():
        setattr(task, key, value)
    db.session.commit()
    return task

def delete_task(task_id):
    task = TaskManager.query.get(task_id)
    if not task:
        return None
    db.session.delete(task)
    db.session.commit()
    return task
