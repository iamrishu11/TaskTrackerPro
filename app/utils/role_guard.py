from functools import wraps
from flask import request, jsonify
from app.utils.jwt_utils import decode_jwt

def jwt_required(roles=[]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Missing Authorization header"}), 401

            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid Authorization format"}), 401

            decoded = decode_jwt(token)
            if "error" in decoded:
                return jsonify(decoded), 401

            if roles and decoded.get("role") not in roles:
                return jsonify({"error": "Forbidden"}), 403

            request.user = decoded  # Attach user info to request context
            return f(*args, **kwargs)
        return wrapper
    return decorator
