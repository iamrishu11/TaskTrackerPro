from app.repositories.task_repository import TaskRepository
from app.repositories.task_logger_repository import TaskLoggerRepository
from datetime import datetime

def create_task(data):
    return TaskRepository.create(
        task_name=data["task_name"],
        description=data.get("description", ""),
        status=data.get("status", False),
        priority=data["priority"],
        user_id=data["assigned_user"]
    )

def get_all_tasks():
    return TaskRepository.get_all_active()

def get_task(task_id):
    return TaskRepository.get_with_logs(task_id)

def update_task(task_id, data):
    task = TaskRepository.update(task_id, **data)
    if "status" in data:
        TaskLoggerRepository.create(task_id, data["status"])
    return task

def delete_task(task_id):
    return TaskRepository.soft_delete(task_id)