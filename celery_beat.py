from celery import Celery
from app.tasks import fetch_and_save_prices

# Используем тот же брокер, что и в tasks.py
celery_app = Celery(broker="redis://localhost:6379/0")

# Настройка расписания
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.fetch_and_save_prices",
        "schedule": 60.0,  # каждые 60 секунд
    }
}
celery_app.conf.timezone = "UTC"

if __name__ == "__main__":
    celery_app.start()