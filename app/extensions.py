from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from dotenv import load_dotenv
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address 

import os

load_dotenv()  # Load environment variables from .env file

redis_client = Redis.from_url(os.getenv("REDIS_URL"))
limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",  # or "redis://localhost:6379" for production
)
db = SQLAlchemy()
migrate = Migrate()
