from app.models import TaskManager
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import joinedload

class TaskRepository:
    @staticmethod
    def create(task_name, description, status, priority, user_id, created_at=None):
        task = TaskManager(
            task_name=task_name,
            description=description,
            status=status,
            priority=priority,
            created_at=created_at or datetime.utcnow(),
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def get_by_id(task_id):
        return TaskManager.query.get(task_id)

    @staticmethod
    def get_all_active():
        return TaskManager.query.filter_by(status=True).all()

    @staticmethod
    def update(task_id, **kwargs):
        task = TaskManager.query.get(task_id)
        if not task:
            return None
        for key, value in kwargs.items():
            setattr(task, key, value)
        db.session.commit()
        return task

    @staticmethod
    def soft_delete(task_id):
        task = TaskManager.query.get(task_id)
        if task:
            task.status = False
            db.session.commit()
        return task

    @staticmethod
    def get_with_logs(task_id):
        return TaskManager.query.options(
            joinedload(TaskManager.logs)
        ).get(task_id)