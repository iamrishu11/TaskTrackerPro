from app import create_app
from celery_worker import init_celery

app = create_app()
init_celery(app)

if __name__ == "__main__":
    app.run(debug=True)
