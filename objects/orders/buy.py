from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging

from discord import ButtonStyle
from typing import Optional, List


from objects.economy.account import EconomyAccount
from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Float, DateTime, String, or_
from sqlalchemy.orm import Session

from objects.base import Base


class BuyOrder(Base):
    __tablename__ = 'buyorder'

    id = Column(Integer, primary_key = True)
    account_id = Column(BigInteger, ForeignKey('economy_accounts.id'))
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    buy_price = Column(BigInteger)
    buy_quantity = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<ID = {0.id}, Account id = {0.accountid}, Stock id = {0.stock_id}, Buy Price = {0.buy_price}, Quantity = {0.buy_quantity}>".format(self)

    @staticmethod
    def create_buyorder(account_id, stock_id, price, quantity, session:Session) -> BuyOrder:
        """Create new row on buyorder table"""

        # Initialize new BuyOrder object
        new_buyorder = BuyOrder(
            account_id = account_id,
            stock_id = stock_id,
            buy_price = price,
            buy_quantity = quantity
        )

        # Commit new BuyOrder object to DB
        session.add(new_buyorder)
        session.commit()

        return new_buyorder

    @staticmethod
    def delete_buyorder(id, session:Session, commit = True):
        """Delete a buyorder row"""

        session.query(BuyOrder).filter(BuyOrder.id == id).delete()
        if(commit):
            session.commit()

    @staticmethod
    def get_all_buyorders(id, session:Session) -> List[BuyOrder]:
        """Returns all buyorders of a certain account"""
        result = session.query(BuyOrder).filter(BuyOrder.account_id == id).order_by(BuyOrder.stock_id, BuyOrder.buy_quantity, BuyOrder.buy_price).all()
        return result
    
    @staticmethod
    def get_stock_buyorders(id, stock, session:Session) -> List[BuyOrder]:
        """Returns all buyorders of a certain account of a specific stock"""
        object = Stock.get_stock(stock, session)
        if(object is None):
            return []
        result = session.query(BuyOrder).filter(BuyOrder.account_id == id, BuyOrder.stock_id == object.id).order_by(BuyOrder.buy_price).all()
        return result

