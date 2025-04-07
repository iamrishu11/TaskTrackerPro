import jwt
from dotenv import load_dotenv
import os

load_dotenv()

# Load the secret key from environment variables
SECRET = os.getenv("JWT_SECRET_KEY")

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3LCJ1c2VybmFtZSI6InNvbWV1c2VyIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NDQwNjE1ODZ9.9umiP2YSrSg9uy5r9tntYRR9wdLatQbIVrRUPYpPGAk"
decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
print(decoded)
