from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
import csv
import json
import pandas as pd
from app.models import TaskManager,User,TaskLogger
from app.schemas import TaskCreateSchema, TaskUpdateSchema
from pydantic import ValidationError
from app.services import task_manager_service, tasklogger_service
from app.tasks.tasklogger_tasks import log_active_tasks_to_logger
from app.utils.role_guard import jwt_required
from app.extensions import db ,redis_client, limiter
from app.utils.serializer import serialize_task
from datetime import datetime

bp = Blueprint("tasks", __name__, url_prefix="/")

@bp.route("/")
def index():
    """
    Welcome endpoint for the TaskTrackerPro API.
    
    **Response:**
    - 200: Returns welcome message
      ```json
      {"message": "Welcome to TaskTrackerPro!"}
      ```
    """
    return {"message": "Welcome to TaskTrackerPro!"}

@bp.route("/ping", methods=["GET"])
def ping():
    """
    Health check endpoint.
    
    **Response:**
    - 200: Returns service status
      ```json
      {"message": "pong!"}
      ```
    """
    return {"message": "pong!"}, 200

@bp.route("/task", methods=["POST"])
@jwt_required(roles=["admin"])
def create_task():
    """
    Create a new task in the TaskManager.

    **Expected Input (JSON):**
    {
        "task_name": "string",          # Required: Name of the task
        "description": "string",         # Optional: Description of the task
        "status": true/false,            # Optional: Task status (default is false)
        "priority": "string",           # Required: Priority level (e.g., High, Medium, Low)
        "created_at": "YYYY-MM-DD",      # Required: Date the task was created
        "assigned_user": "string"        # Required: Username of the assigned user
    }

    **Authorization:**
    - Requires JWT token with "admin" role.

    **Rate Limiting:**
    - Limited to 10 requests per minute per user.

    **Responses:**
    - 201: Task successfully created
    - 400: Validation error or bad input
    - 401: Unauthorized (missing/invalid token)
    - 403: Forbidden (role not authorized)
    """
    try:
        validated_data = TaskCreateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    task = task_manager_service.create_task(validated_data.dict())
    return jsonify({"id": task.id, "task_name": task.task_name}), 201

@bp.route("/tasks", methods=["GET"])
@limiter.limit("60 per minute")
def get_tasks():
    """
    Retrieve paginated tasks with optional date filtering.

    **Query Parameters:**
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    - date: Filter by date (format: YYYY-MM-DD)

    **Response:**
    - 200: Returns paginated task list
      ```json
      {
        "tasks": [{
          "id": 1,
          "task_id": 1,
          "date_logged": "2025-04-01",
          "status": true,
          "task": {
            "task_name": "Sample",
            "description": "Details"
          }
        }],
        "total": 100,
        "page": 1,
        "pages": 10
      }
      ```
    - 400: Invalid date format
      ```json
      {"error": "Invalid date format. Use YYYY-MM-DD."}
      ```
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    date_str = request.args.get("date")

    cache_key = f"tasks:{date_str}:{page}:{per_page}" if date_str else f"tasks:all:{page}:{per_page}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data)), 200

    query = TaskLogger.query.options(joinedload(TaskLogger.task))
    
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(db.func.date(TaskLogger.date_logged) == date_obj)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    paginated = query.order_by(TaskLogger.date_logged.desc()).paginate(page=page, per_page=per_page, error_out=False)
    result = {
        "tasks": [serialize_task(task) for task in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages
    }

    redis_client.setex(cache_key, 60, json.dumps(result))
    return jsonify(result), 200


@bp.route("/tasklogger/<int:log_id>", methods=["GET"])
@limiter.limit("20/minute")
def get_logged_task(log_id):
    """
    Get detailed information about a specific task log entry.

    **Parameters:**
    - log_id: TaskLogger ID (required)

    **Response:**
    - 200: Returns task log details
      ```json
      {
        "log_id": 1,
        "date_logged": "2025-04-01",
        "status": true,
        "task": {
          "id": 1,
          "task_name": "Sample",
          "description": "Details",
          "priority": "high",
          "created_at": "2025-04-01",
          "assigned_user": "admin"
        }
      }
      ```
    - 404: Task log not found
      ```json
      {"message": "Task log not found"}
      ```
    """
    log = TaskLogger.query.options(
        joinedload(TaskLogger.task).joinedload(TaskManager.user)
    ).filter_by(id=log_id).first()

    if not log:
        return jsonify({"message": "Task log not found"}), 404

    task = log.task
    return jsonify({
        "log_id": log.id,
        "date_logged": log.date_logged.strftime("%Y-%m-%d"),
        "status": log.status,
        "task": {
            "id": task.id,
            "task_name": task.task_name,
            "description": task.description,
            "priority": task.priority,
            "created_at": task.created_at.strftime("%Y-%m-%d") if task.created_at else None,
            "assigned_user": task.user.username if task.user else None
        }
    }), 200

@bp.route("/task/<int:task_id>", methods=["PUT"])
@jwt_required(roles=["admin"])
def update_task(task_id):
    """
    Update an existing task.

    **Authorization:**
    - Requires JWT token with "admin" role

    **Parameters:**
    - task_id: Task ID to update (required)

    **Request Body (JSON):**
    ```json
    {
        "task_name": "string (optional)",
        "description": "string (optional)",
        "status": "boolean (optional)",
        "priority": "string (optional, enum: low/medium/high)",
        "assigned_user": "string (optional)"
    }
    ```

    **Responses:**
    - 200: Task updated successfully
      ```json
      {"message": "Task updated"}
      ```
    - 400: Validation error
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Task not found
      ```json
      {"message": "Task not found"}
      ```
    """
    try:
        data = request.get_json()
        validated_data = TaskUpdateSchema.model_validate(data)
        update_data = validated_data.model_dump(exclude_unset=True)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    task = task_manager_service.update_task(task_id, update_data)
    if not task:
        return {"message": "Task not found"}, 404
    return jsonify({"message": "Task updated"})


@bp.route("/task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Soft delete a task (sets status to False).

    **Parameters:**
    - task_id: Task ID to delete (required)

    **Response:**
    - 200: Task soft-deleted
      ```json
      {"message": "Task soft-deleted"}
      ```
    - 404: Task not found
      ```json
      {"message": "Task not found"}
      ```
    """
    task = task_manager_service.delete_task(task_id)
    if not task:
        return {"message": "Task not found"}, 404
    
    # Soft delete by marking status as False
    task.status = False
    db.session.commit()
    return jsonify({"message": "Task soft-deleted"})

@bp.route("/activetasks", methods=["GET"])
def get_all_tasks():
    """
    Get all active tasks (status=True).

    **Response:**
    - 200: Returns list of active tasks
      ```json
      [{"id": 1, "task_name": "Task 1"}, ...]
      ```
    """
    tasks = task_manager_service.get_all_tasks()
    return jsonify([{"id": t.id, "task_name": t.task_name} for t in tasks])

@bp.route("/upload-csv", methods=["POST"])
@limiter.limit("10/hour")
def upload_csv():
    """
    Bulk upload tasks from CSV file.

    **Request:**
    - Form-data with CSV file attachment

    **CSV Format:**
    ```
    task_name,description,status,priority,created_at,assigned_user
    Task 1,Description 1,true,high,04/01/2025,user1
    ```

    **Responses:**
    - 200: CSV processed successfully
      ```json
      {"message": "X tasks uploaded successfully"}
      ```
    - 400: Invalid request
      ```json
      {"error": "CSV file is required"}
      ```
    """
    if 'file' not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    file = request.files['file']

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file format. Upload a CSV file."}), 400

    stream = file.stream.read().decode("utf-8").splitlines()
    reader = csv.DictReader(stream)

    success_count = 0

    for row in reader:
        try:
            username = row["assigned_user"].strip()
            user = User.query.filter_by(username=username).first()

            # If user doesn't exist, create one
            if not user:
                user = User(
                    username=username,
                    email=f"{username}@example.com",
                    password="default123",  # Can change it later
                    role="user"
                )
                db.session.add(user)
                db.session.flush()  # Get user.id without full commit

            task = TaskManager(
                task_name=row["task_name"].strip(),
                description=row.get("description", "").strip(),
                status=row["status"].strip().lower() in ["true", "1", "yes"],
                priority=row["priority"].strip(),
                created_at=datetime.strptime(row["created_at"].strip(), "%m/%d/%Y").date(),
                user_id=user.id
            )

            db.session.add(task)
            success_count += 1

        except Exception as e:
            print(f"Error processing row: {row} — {e}")
            continue

    db.session.commit()

    return jsonify({"message": f"{success_count} tasks uploaded successfully"})

@bp.route("/log-tasks", methods=["POST"])
def trigger_task_logging():
    """
    Manually trigger the daily task logging process.

    **Response:**
    - 202: Logging process initiated
      ```json
      {"message": "Logging of active tasks has been triggered."}
      ```
    """
    log_active_tasks_to_logger.delay()  # Asynchronous task execution
    return jsonify({"message": "Logging of active tasks has been triggered."}), 202

@bp.route("/tasks", methods=["GET"])
def get_logged_tasks_paginated():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    paginated_logs = TaskLogger.query.paginate(page=page, per_page=per_page, error_out=False)
    
    data = []
    for log in paginated_logs.items:
        task = log.task  # from relationship
        data.append({
            "log_id": log.id,
            "date_logged": log.date_logged.strftime("%Y-%m-%d"),
            "status": log.status,
            "task": {
                "id": task.id,
                "task_name": task.task_name,
                "description": task.description,
                "priority": task.priority,
                "created_at": task.created_at.strftime("%Y-%m-%d") if task.created_at else None,
                "assigned_user": task.user.username if task.user else None
            }
        })

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": paginated_logs.total,
        "pages": paginated_logs.pages,
        "logs": data
    }), 200
