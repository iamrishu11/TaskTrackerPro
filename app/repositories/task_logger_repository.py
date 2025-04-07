from app.models import TaskLogger
from app.extensions import db
from datetime import datetime, date

class TaskLoggerRepository:
    @staticmethod
    def create(task_id, status):
        log = TaskLogger(
            task_id=task_id,
            status=status,
            date_logged=datetime.utcnow().date()
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_by_date(log_date):
        return TaskLogger.query.filter_by(date_logged=log_date).all()

    @staticmethod
    def get_paginated(page=1, per_page=10, date_filter=None):
        query = TaskLogger.query
        if date_filter:
            query = query.filter_by(date_logged=date_filter)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def exists(task_id, log_date):
        return db.session.query(
            TaskLogger.query.filter_by(
                task_id=task_id,
                date_logged=log_date
            ).exists()
        ).scalar()