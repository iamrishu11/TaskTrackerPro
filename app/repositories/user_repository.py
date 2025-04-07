from app.models import User
from app.extensions import db

class UserRepository:
    @staticmethod
    def create(username, email, password, role):
        user = User(
            username=username,
            email=email,
            password=password,  # You'll hash this later
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)