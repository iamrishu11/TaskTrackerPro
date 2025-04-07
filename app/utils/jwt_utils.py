import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import current_app
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt(user_id, username, role, expires_in=None):
    if expires_in is None:
        expires_in = int(os.getenv("JWT_EXP_DELTA_SECONDS", 3600))  # Default: 1 hour

    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")



def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
