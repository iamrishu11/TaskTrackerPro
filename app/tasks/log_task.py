from celery_worker import celery_app
from app.services.tasklogger_service import log_active_tasks_daily

@celery_app.task
def log_tasks_daily():
    log_active_tasks_daily()
