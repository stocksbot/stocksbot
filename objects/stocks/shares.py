from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging

from objects.stocks.stock import Stock
from objects.economy.account import EconomyAccount
from objects.orders.buy import BuyOrder
from sqlalchemy import Column, Integer, Float, DateTime, String, or_, ForeignKey
from sqlalchemy.orm import Session

from objects.base import Base


class Shares(Base):
    __tablename__ = 'shares'

    account_id = Column(Integer, ForeignKey('economy_accounts.id'), primary_key=True)
    stock_id = Column(String(20), ForeignKey('stocks.id'), primary_key=True)
    amount_held = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<Account ID={0.accountid}, Stock ID={0.stock_id}, Amount={0.amountheld}>".format(self)

    @staticmethod
    def create_shareholder(account_id, symbol, amount, session:Session) -> Shares:
        """Create new row on shares table"""
        # Get stock id
        stock_id = Stock.get_stock(symbol, session).id

        # Initialize new Shares object
        new_shareholder = Shares(
            account_id = account_id,
            stock_id = stock_id,
            amount_held = amount
        )

        # Commit new shares object to DB
        session.add(new_shareholder)
        session.commit()

        return new_shareholder

    @staticmethod
    def get_shares_held(account_id, symbol, session:Session) -> Integer:
        """Return amount of specific shares held by an account"""

        # Get stock id
        stock_id = Stock.get_stock(symbol, session).id
        result = session.query(Shares).filter(
            Shares.stock_id == stock_id, 
            Shares.account_id == account_id
        ).first()
        if(result == None):
            return 0
        return result.amount_held

    @staticmethod
    def get_all_shares(account_id, session:Session):
        """Return all existing shares of an account"""

        result = session.query(Shares).filter(Shares.account_id == account_id)
        return result

    @staticmethod
    def buy_shares(account_id, symbol, buy_quantity, buy_price, session:Session):
        """Increase owned shares while decreasing corresponding balance"""

        #Check if account balance can do order
        econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == account_id).first()
        if(buy_quantity * buy_price > econaccount.balance):
            # Account does not have enough balance to place such buy order
            return 1
        stockobject = Stock.get_stock(symbol, session)
        if(stockobject == None):
            # Stock does not exist
            return 2
        currentprice = stockobject.price # store price to avoid race conditions
        if(currentprice <= buy_price):
            # Do an instant buy order
            econaccount.balance -= buy_quantity*currentprice
            stock_id = Stock.get_stock(symbol, session).id
            shareQuery = session.query(Shares).filter(
            Shares.stock_id == stock_id, Shares.account_id == account_id
            ).first()
            if(shareQuery == None):
                shareQuery = Shares.create_shareholder(account_id, symbol, buy_quantity, session)
            else:
                shareQuery.amount_held += buy_quantity
        else:
            # Do a pending buy order
            econaccount.balance -= buy_quantity*buy_price # Reserve balance from account for pending buy order
            BuyOrder.create_buyorder(econaccount.id, stockobject.id, buy_price, buy_quantity, session)
        session.commit()
        return 0
