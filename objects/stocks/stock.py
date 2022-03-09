from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging

from sqlalchemy import Column, Integer, Float, DateTime, String, or_

from objects.base import Base


class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    symbol = Column(String(20), unique=True)
    price = Column(Float)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<Stock id={0.id}, name={0.name}, price={0.price}>".format(self)

    @staticmethod
    def get_stock(symbol, session) -> Stock:
        """Search for a Stock entry using Stock.symbol"""

        result = session.query(Stock).filter(
            Stock.symbol == symbol
        ).first()

        return result

    @staticmethod
    def update_stocks(clean_stock_data):
        pass
