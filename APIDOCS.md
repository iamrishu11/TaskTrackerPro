# TaskTrackerPro API Documentation

## Base URL
`http://127.0.0.1:5000/`

## Authentication
- JWT Bearer Token
- Required for protected endpoints
- Obtain token via `/login` endpoint

## Error Responses
| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |

---

## User Endpoints

### Login
`POST /login`

**Request:**
```json
{
  "username": "string",
  "password": "string",
  "role": "string"
}
```

**Response:**
```json
{
  "token": "jwt.token.here"
}
```
### Create User
POST /user

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "newuser"
}
```

## Task Endpoints

### Create Task
POST /task <br>
Requires admin role

**Request:**
```json
{
  "task_name": "string",
  "description": "string",
  "status": true,
  "priority": "high",
  "created_at": "2025-04-01",
  "assigned_user": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "task_name": "New Task"
}
```

### Get Tasks (Paginated)
GET /tasks?date=2025-04-07

**Query Parameters:**
- page (default: 1)
- per_page (default: 10)
- date (optional filter by date)

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "task_id": 1,
      "date_logged": "2025-04-01",
      "status": true,
      "task": {
        "task_name": "Sample Task",
        "description": "Task description"
      }
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 2
}
```

### Get Task Log Details
GET /tasklogger/<<int:log_id>>

**Response:**
```json
{
  "log_id": 1,
  "date_logged": "2025-04-01",
  "status": true,
  "task": {
    "id": 1,
    "task_name": "Sample Task",
    "description": "Task details",
    "priority": "high",
    "created_at": "2025-04-01",
    "assigned_user": "username"
  }
}
```

### Update Task
PUT /task/<<int:task_id>> <br>
Requires admin role

**Request:**
```json
{
  "task_name": "Updated Name",
  "priority": "medium"
}
```

**Response:**
```json
{
  "message": "Task updated"
}
```

### Delete Task
DELETE /task/<<int:task_id>>

**Response:**
```json
{
  "message": "Task soft-deleted successfully",
  "task_id": "task.id",
  "status": "task.status"
}
```

## Bulk Operations

### Upload Tasks via CSV
POST /upload-csv <br>
Rate limited to 10/hour

**Request:**

- Add Header 'Content-Type: multipart/form-data'
- Form-data with CSV file (see sample below)

```bash
task_name,description,status,priority,created_at,assigned_user
Task 1,Description 1,true,high,04/01/2025,user1
Task 2,Description 2,false,medium,04/02/2025,user2
```

**Response:**
```json
{
  "message": "5 tasks uploaded successfully"
}
```

## Trigger Daily Task Logging
POST /log-tasks

**Response:**
```json
{
  "message": "Logging of active tasks has been triggered."
}
```

##  System Endpoints

### Health Check
GET /ping

**Response:**
```json
{
  "message": "pong!"
}
```

### Welcome
GET / 

**Response:**
```json
{
  "message": "Welcome to TaskTrackerPro!"
}
```

## Rate Limits

| Endpoint        | Limit     |
|-----------------|-----------|
| /login          | 5/minute  |
| /tasks          | 60/minute |
| /upload-csv     | 10/hour   |
| Other endpoints | 30/minute |

## Data Validation

All endpoints use Pydantic schemas with these rules:

- Priority: must be "low", "medium", or "high"
- Dates: must be in YYYY-MM-DD format
- Status: boolean
- Required fields marked in schemas

## Redis Working proof 

<img src="assets\Redis working.png" description="Imgae of redis serever rendereing in 3600 seconds">
