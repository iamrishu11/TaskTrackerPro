from app.extensions import db
from sqlalchemy.orm import relationship 

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    role = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    tasks = relationship("TaskManager", back_populates="user")


    def __repr__(self):
        return f"<User {self.username}>"
