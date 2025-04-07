from app.repositories.task_repository import TaskRepository
from app.repositories.task_logger_repository import TaskLoggerRepository
from datetime import date

def get_tasks_by_date(target_date):
    return TaskLoggerRepository.get_by_date(target_date)

def log_daily_tasks():
    today = date.today()
    active_tasks = TaskRepository.get_all_active()
    logged_count = 0
    
    for task in active_tasks:
        if not TaskLoggerRepository.exists(task.id, today):
            TaskLoggerRepository.create(task.id, task.status)
            logged_count += 1
    
    return logged_count