# TaskTrackerPro 🧠🗂️

A high-performance, secure, and scalable task tracking backend system built with Flask. This system allows role-based task management, logging, CSV uploads, and automated daily tracking via Celery.

---

## 🚀 Features

- Modular Flask architecture (Blueprints, Services, Repositories)
- Role-based access control (RBAC)
- PostgreSQL database with SQLAlchemy
- Celery task for daily logging of active tasks
- Redis for caching and message brokering
- JWT Authentication
- CSV upload to seed tasks
- Pydantic-style validation with Marshmallow
- Soft-deletion, pagination, and filtered query support
- Rate limiting and secure API handling

---

## ⚙️ Tech Stack

| Layer       | Tech                      |
|------------|---------------------------|
| Backend     | Flask, SQLAlchemy, Celery |
| Database    | PostgreSQL                |
| Messaging   | Redis                     |
| Auth        | JWT (JSON Web Tokens)     |
| Deployment  | Docker                    |
| Testing     | Postman, DBeaver          |

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/TaskTrackerPro.git
cd TaskTrackerPro
```

### 2. Create .env file

```bash
FLASK_ENV=development
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<yourdb>
JWT_SECRET_KEY=your_jwt_secret
REDIS_URL=redis://localhost:6379/0
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start Services

- Run flask app

```bash
python main.py
```

- Celery Worker

```bash
celery -A app.celery worker --loglevel=info
```

- Run your redis server
- Run psql shell

## Project Structure

```bash
TaskTrackerPro/
├── app/
│   ├── auth/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── routes/
│   └── utils/
├── migrations/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔐 API Authentication

All protected endpoints require a JWT Bearer token:

```bash
Authorization: Bearer <your_token>
```
Use the login endpoint to obtain a token.

## 📡 API Endpoints Summary

| Method |        Endpoint        |             Description            |
|:------:|:----------------------:|:----------------------------------:|
| POST   | /upload-csv            | Upload CSV to populate TaskManager |
| GET    | /tasks                 | Get paginated task logs            |
| GET    | /tasks?date=YYYY-MM-DD | Filter logs by date (cached)       |
| GET    | /task/<logger_id>      | Get task details                   |
| POST   | /task                  | Create a task (admin/user)         |
| PUT    | /task/<task_id>        | Update a task                      |
| DELETE | /task/<task_id>        | Soft delete a task                 |

## 🧪 Testing

Use [Postman](https://postman.com) to test routes. Include the JWT token in headers where required.

## 🧼 Best Practices Followed

-Modular code architecture
-Input validation and error handling
-Secure database access
-Logging and auditing
-Avoiding duplicate task logs
-Docker-ready configuration

## 🔌 API

For detailed api explanation plese refer to [API Guide](APIDOCS.md)


## 👨‍💻 Author
Made with 💻 by Rishank Jain.

## 🧾 LICENSE 

This project is licensed under the [MIT License](LICENSE).