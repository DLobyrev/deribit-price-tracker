"""
Celery-задача для периодического получения цен с Deribit.
"""

from celery import Celery
from .client import get_index_price
from .database import SessionLocal
from .models import PriceRecord

celery_app = Celery(
    "price_tracker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.fetch_and_save_prices",
        "schedule": 60.0,
    }
}
celery_app.conf.timezone = "UTC"


TICKERS = ["btc_usd", "eth_usd"]

@celery_app.task
def fetch_and_save_prices():
    db = SessionLocal()
    try:
        for ticker in TICKERS:
            data = get_index_price(ticker)
            if data:
                record = PriceRecord(
                    ticker=data["ticker"],
                    price=data["price"],
                    timestamp=data["timestamp"]
                )
                db.add(record)
                print(f"Сохранено: {data['ticker']} = {data['price']}")
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
    finally:
        db.close()