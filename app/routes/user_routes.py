from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.utils.jwt_utils import generate_jwt
from app.models import User

user_bp = Blueprint("users", __name__, url_prefix="/")

@user_bp.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],  # ideally hash it later
        role=data["role"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username}), 201

@user_bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or user.password != data["password"]:
        return jsonify({"message": "Invalid credentials"}), 401
    
    token = generate_jwt(user.id, user.username, user.role)
    return jsonify({"token": token})
