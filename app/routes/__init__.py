# Initialization file for the routes module

from .task_routes import bp as task_bp
from .user_routes import user_bp

__all__ = ['task_bp', 'user_bp']