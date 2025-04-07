from app.extensions import db
from datetime import datetime

class TaskLogger(db.Model):
    __tablename__ = 'task_logger'
    __table_args__ = (
    db.Index("ix_date_logged", "date_logged"),
    )

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_manager.id', ondelete="CASCADE"), nullable=False)
    date_logged = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)

    task = db.relationship("TaskManager", back_populates="logs")

    def __repr__(self):
        return f"<TaskLogger {self.id} - Task {self.task_id}>"
