from celery_worker import celery_app
from app.repositories.task_repository import TaskRepository
from app.repositories.task_logger_repository import TaskLoggerRepository
from datetime import datetime

@celery_app.task
def log_active_tasks_to_logger():
    today = datetime.now().date()
    active_tasks = TaskRepository.get_all_active()
    
    for task in active_tasks:
        if not TaskLoggerRepository.exists(task.id, today):
            TaskLoggerRepository.create(task.id, task.status)