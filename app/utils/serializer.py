def serialize_task(task_logger):
    return {
        "id": task_logger.id,
        "task_id": task_logger.task_id,
        "date_logged": task_logger.date_logged.isoformat(),
        "status": task_logger.status,
        "task": {
            "task_name": task_logger.task.task_name,
            "description": task_logger.task.description,
            # Add more fields as needed
        }
    }
