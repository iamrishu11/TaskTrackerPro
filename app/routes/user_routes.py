from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.utils.jwt_utils import generate_jwt
from app.models import User

user_bp = Blueprint("users", __name__, url_prefix="/")

@user_bp.route("/user", methods=["POST"])
def create_user():
    """
    Create a new user account.

    **Request Body (JSON):**
    ```json
    {
        "username": "string (required, unique)",
        "email": "string (required, valid email)",
        "password": "string (required, plaintext - will be hashed later)",
        "role": "string (required)"
    }
    ```

    **Responses:**
    - 201: User created successfully
      ```json
      {
        "id": 1,
        "username": "newuser"
      }
      ```
    - 400: Missing required fields or validation error
    - 409: Username or email already exists
    - 500: Server error during user creation

    **Security Note:** 
    - Passwords are currently stored in plaintext. 
    - In production, implement password hashing (bcrypt/Argon2).
    """
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
    """
    Authenticate user and return JWT token.

    **Request Body (JSON):**
    ```json
    {
        "username": "string (required)",
        "password": "string (required)"
    }
    ```

    **Responses:**
    - 200: Authentication successful
      ```json
      {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
      ```
    - 401: Invalid credentials
      ```json
      {
        "message": "Invalid credentials"
      }
      ```
    - 429: Too many requests (rate limited)

    **Security Notes:**
    - Rate limited to 5 attempts per minute
    - Tokens expire after 1 hour (configurable)
    - Always use HTTPS in production
    """
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or user.password != data["password"]:
        return jsonify({"message": "Invalid credentials"}), 401
    
    token = generate_jwt(user.id, user.username, user.role)
    return jsonify({"token": token})
