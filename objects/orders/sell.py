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


class SellOrder(Base):
    __tablename__ = 'sellorder'

    id = Column(Integer, primary_key = True)
    account_id = Column(BigInteger, ForeignKey('economy_accounts.id'))
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    sell_price = Column(BigInteger)
    sell_quantity = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<ID = {0.id}, Account id = {0.accountid}, Stock id = {0.stock_id}, Sell Price = {0.sell_price}, Quantity = {0.sell_quantity}>".format(self)

    @staticmethod
    def create_sellorder(account_id, stock_id, price, quantity, session:Session) -> SellOrder:
        """Create new row on sellorder table"""

        # Initialize new SellOrder object
        new_sellorder = SellOrder(
            account_id = account_id,
            stock_id = stock_id,
            sell_price = price,
            sell_quantity = quantity
        )

        # Commit new SellOrder object to DB
        session.add(new_sellorder)
        session.commit()

        return new_sellorder

    @staticmethod
    def delete_sellorder(id, session:Session, commit = True):
        """Delete a SellOrder row"""

        session.query(SellOrder).filter(SellOrder.id == id).delete()
        if(commit):
            session.commit()

    @staticmethod
    def get_all_sellorders(id, session:Session) -> List[SellOrder]:
        """Returns all SellOrders of a certain account"""
        result = session.query(SellOrder).filter(SellOrder.account_id == id).order_by(SellOrder.stock_id, SellOrder.buy_quantity, SellOrder.buy_price).all()
        return result
    
    @staticmethod
    def get_stock_sellorders(id, stock, session:Session) -> List[SellOrder]:
        """Returns all SellOrders of a certain account of a specific stock"""
        object = Stock.get_stock(stock, session)
        if(object is None):
            return []
        result = session.query(SellOrder).filter(SellOrder.account_id == id, SellOrder.stock_id == object.id).order_by(SellOrder.buy_price).all()
        return result

