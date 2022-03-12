from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging
import typing as ty

from discord import ButtonStyle

from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from objects.economy.account import EconomyAccount
from sqlalchemy import Column, ForeignKey, Integer, Float, DateTime, String, or_
from sqlalchemy.orm import Session

from objects.base import Base


class BuyOrder(Base):
    __tablename__ = 'BuyOrder'

    id = Column(Integer, primary_key = True)
    account_id = Column(Integer, ForeignKey('economy_accounts.id'))
    stock_id = Column(stock_id = Column(String(20), ForeignKey('stocks.id')))
    buy_price = Column(Integer)
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
    def check_buyorders(session:Session):
        """Returns list of executable buyorders"""
        BuyOrders = session.query(BuyOrder).all()
        for order in BuyOrders:
            stock = session.query(Stock).filter(Stock.id == order.stock_id)