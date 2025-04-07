from app.extensions import db,redis_client
from app.models.task_logger import TaskLogger
from app.utils.serializer import serialize_task
from app.models.task_manager import TaskManager
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from flask import abort
from datetime import date, datetime

import json

CACHE_TTL = 60 * 60  # 1 hour cache time

def get_tasks_by_date(date):
    cache_key = f"tasks:{date}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("Serving from cache")
        return json.loads(cached_data)

    # Else, query from DB
    tasks = (
        db.session.query(TaskLogger)
        .filter(TaskLogger.date_logged == date)
        .options(joinedload(TaskLogger.task))
        .all()
    )
    serialized_tasks = [serialize_task(task) for task in tasks]

    # Store in Redis cache
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(serialized_tasks))
    
    return serialized_tasks

def log_daily_tasks():
    today = date.today()
    
    # Get active tasks (status=True)
    active_tasks = TaskManager.query.filter_by(status=True).all()

    if not active_tasks:
        return 0

    new_logs = []
    for task in active_tasks:
        log_entry = TaskLogger(
            task_id=task.id,
            date_logged=today,
            status=task.status  # copying current status
        )
        new_logs.append(log_entry)

    db.session.bulk_save_objects(new_logs)
    db.session.commit()

    return len(new_logs)
