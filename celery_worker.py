from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

celery_app = Celery(
    __name__,
    backend=os.getenv("REDIS_URL"),
    broker=os.getenv("REDIS_URL")
)

celery_app.autodiscover_tasks(['app.tasks'])

# Celery Beat configuration for periodic tasks
# This task will run daily at midnight UTC
celery_app.conf.beat_schedule = {
    'log-tasks-daily': {
        'task': 'app.tasks.log_task.log_tasks_daily',
        'schedule': crontab(hour=0, minute=0),
    },
}

celery_app.conf.timezone = 'UTC'

def init_celery(app):
    celery_app.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask