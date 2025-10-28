from celery import Celery
from core.config import settings

# Create Celery instance
celery_app = Celery(
    "quflux",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.publishing", 
        "tasks.ai_generation", 
        "tasks.notifications"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "tasks.publishing.*": {"queue": "publishing"},
        "tasks.ai_generation.*": {"queue": "ai_generation"},
        "tasks.notifications.*": {"queue": "notifications"},
    },
    beat_schedule={
        # Add scheduled tasks here
    },
)

if __name__ == "__main__":
    celery_app.start()