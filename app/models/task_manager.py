from app.extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime

class TaskManager(db.Model):
    __tablename__ = 'task_manager'
    __table_args__ = (
    db.Index("ix_created_at", "created_at"),
    db.Index("ix_user_id", "user_id"),
    )


    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    priority = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.Date, default=datetime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = relationship("User", back_populates="tasks")
    logs = relationship("TaskLogger", back_populates="task", cascade="all, delete-orphan",lazy="dynamic",passive_deletes=True)

    def __repr__(self):
        return f"<TaskManager {self.task_name}>"
