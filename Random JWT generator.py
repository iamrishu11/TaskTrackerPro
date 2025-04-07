from app.utils.jwt_utils import generate_jwt

token = generate_jwt(7, "someuser", "user")
print(token)

