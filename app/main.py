"""
FastAPI-сервер для получения сохранённых цен с Deribit.
"""

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from . import models, database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте
    models.Base.metadata.create_all(bind=database.engine)
    yield
    # Здесь можно закрыть соединения (если нужно)

app = FastAPI(title="Deribit Price Tracker API", lifespan=lifespan)

@app.get("/prices/", response_model=List[dict])
def get_prices_by_ticker(
    ticker: str = Query(..., description="Тикер: btc_usd или eth_usd"),
    db: Session = Depends(database.get_db)
):
    """Получить все сохранённые цены по указанному тикеру."""
    records = db.query(models.PriceRecord).filter(models.PriceRecord.ticker == ticker).all()
    return [
        {
            "ticker": r.ticker,
            "price": r.price,
            "timestamp": r.timestamp
        }
        for r in records
    ]


@app.get("/prices/latest/", response_model=dict)
def get_latest_price(
    ticker: str = Query(..., description="Тикер: btc_usd или eth_usd"),
    db: Session = Depends(database.get_db)
):
    """Получить последнюю (самую свежую) цену по тикеру."""
    record = (
        db.query(models.PriceRecord)
        .filter(models.PriceRecord.ticker == ticker)
        .order_by(models.PriceRecord.timestamp.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Цена не найдена")
    return {
        "ticker": record.ticker,
        "price": record.price,
        "timestamp": record.timestamp
    }


@app.get("/prices/by-date/", response_model=List[dict])
def get_prices_by_date(
    ticker: str = Query(..., description="Тикер: btc_usd или eth_usd"),
    date: str = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(database.get_db)
):
    """Получить цены по тикеру за указанную дату."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD")

    # Преобразуем дату во временные метки (начало и конец дня)
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    records = (
        db.query(models.PriceRecord)
        .filter(
            models.PriceRecord.ticker == ticker,
            models.PriceRecord.timestamp >= start_ts,
            models.PriceRecord.timestamp <= end_ts
        )
        .all()
    )
    return [
        {
            "ticker": r.ticker,
            "price": r.price,
            "timestamp": r.timestamp
        }
        for r in records
    ]