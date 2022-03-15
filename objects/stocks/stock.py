from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging
from typing import Optional

from sqlalchemy import BigInteger, Column, Integer, Float, DateTime, String, or_
from sqlalchemy.orm import Session

from objects.base import Base


class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    symbol = Column(String(20), unique=True)
    price = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<Stock id={0.id}, name={0.name}, price={0.price}>".format(self)

    @staticmethod
    def get_stock(symbol, session:Session) -> Optional[Stock]:
        """Search for a Stock entry using Stock.symbol"""

        result = session.query(Stock).filter(
            Stock.symbol == symbol
        ).first()
        if(result == None):
            logging.warning("[WARNING] Stock symbol does not exist")
        return result

    @staticmethod
    def update_stocks(clean_stock_data, session:Session):
        """Update stock prices.
        We assume stock exists c/o seeder
        """

        stock_mappings = []
        for stock in clean_stock_data:
            target = Stock.get_stock(
                stock['symbol'],
                session
            )
            if(target == None):
                logging.error("[ERROR] Stock does not exist")
                continue
            stock_mappings.append(
                {
                    'id':target.id,
                    'price': stock['price']
                }
            )
        
        # To-do: Standardize clean_stock_data as object
        session.bulk_update_mappings(
            Stock,
            stock_mappings
        )

        session.commit()

        logging.info("Updated {0} stock prices.".format(
            len(clean_stock_data)
        ))

    @staticmethod
    def get_all(session: Session):
        return session.query(Stock).all()

    def get_price(self):
        return self.price / 10000 # Convert to database-friendly format
