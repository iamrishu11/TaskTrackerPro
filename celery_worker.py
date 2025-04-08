from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

celery_app = Celery(
    __name__,
    backend=os.getenv("REDIS_URL"),
    broker=os.getenv("REDIS_URL")
)

celery_app.autodiscover_tasks(['app.tasks'])

def init_celery(app):
    celery_app.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
