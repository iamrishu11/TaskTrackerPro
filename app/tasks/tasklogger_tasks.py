from celery_worker import celery_app
from app.extensions import db
from app.models.task_manager import TaskManager
from app.models.task_logger import TaskLogger
from datetime import datetime

@celery_app.task
def log_active_tasks_to_logger():
    active_tasks = TaskManager.query.filter_by(status=True).all()
    logged_count = 0

    for task in active_tasks:
        already_logged = TaskLogger.query.filter_by(task_id=task.id, date_logged=datetime.now().date()).first()
        if not already_logged:
            log = TaskLogger(task_id=task.id, status=task.status)
            db.session.add(log)
            logged_count += 1

    db.session.commit()
    return f"{logged_count} tasks logged to TaskLogger."
