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
    return {"message": "Welcome to TaskTrackerPro!"}

@bp.route("/ping", methods=["GET"])
def ping():
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
    task = task_manager_service.delete_task(task_id)
    if not task:
        return {"message": "Task not found"}, 404
    
    # Soft delete by marking status as False
    task.status = False
    db.session.commit()
    return jsonify({"message": "Task soft-deleted"})

@bp.route("/activetasks", methods=["GET"])
def get_all_tasks():
    tasks = task_manager_service.get_all_tasks()
    return jsonify([{"id": t.id, "task_name": t.task_name} for t in tasks])

@bp.route("/upload-csv", methods=["POST"])
@limiter.limit("10/hour")
def upload_csv():
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
                    password="default123",  # You can later hash/change this
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
