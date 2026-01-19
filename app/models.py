"""
Модель данных для хранения цен с Deribit.
Создаёт таблицу 'price_records' в PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, Float
from .database import Base


class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)      # например: 'btc_usd'
    price = Column(Float, nullable=False)    # цена в USD
    timestamp = Column(Integer, nullable=False)  # UNIX timestamp (секунды)