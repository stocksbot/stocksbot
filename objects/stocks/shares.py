from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
from typing import Optional
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
    def create_shareholder(account_id, symbol, amount, session:Session) -> Optional[Shares]:
        """Create new row on shares table returns shareholder object on success, else returns none"""

        # Get stock id
        stock = Stock.get_stock(symbol, session)
        if(stock == None):
            logging.error("[ERROR] stock does not exist")
            return None
        stock_id = stock.id        

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
    def create_shareholder_with_id(account_id, stock_id, amount, session:Session, commit = True) -> Shares:
        """Create new row on shares table (but with a stock ID instead of a symbol)"""

        # Initialize new Shares object
        new_shareholder = Shares(
            account_id = account_id,
            stock_id = stock_id,
            amount_held = amount
        )

        # Commit new shares object to DB
        session.add(new_shareholder)
        if(commit):
            session.commit()

        return new_shareholder

    @staticmethod
    def get_shares_held(account_id, symbol, session:Session) -> int:
        """Return amount of specific shares held by an account"""

        # Get stock id
        stock = Stock.get_stock(symbol, session)
        if(stock == None):
            logging.error("[ERROR] stock does not exist")
            return -1
        stock_id = stock.id
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
    def increment_shares(account_id, stock_id, amount, session:Session, commit = True):
        """Increment shares held by account on a specific stock"""

        shareQuery = session.query(Shares).filter(
            Shares.account_id == account_id, 
            Shares.stock_id == stock_id
        ).first()
        if(shareQuery == None):
            shareQuery = Shares.create_shareholder_with_id(account_id,stock_id,amount,session,commit)
        else:
            shareQuery.amount_held += amount
        if(commit):
            session.commit()
        return shareQuery

    @staticmethod
    def buy_shares(account_id, symbol, buy_quantity, buy_price, session:Session):
        """Increase owned shares while decreasing corresponding balance"""

        #Check if account balance can do order
        econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == account_id).first()
        if(econaccount == None):
            logging.error("[ERROR] Account does not exist")
            # Account does not exist
            return 1
        if(buy_quantity * buy_price > econaccount.get_balance):
            # Account does not have enough balance to place such buy order
            return 2
        stockobject = Stock.get_stock(symbol, session)
        if(stockobject == None):
            # Stock does not exist
            return 3
        currentprice = stockobject.price # store price to avoid race conditions
        if(currentprice <= buy_price):
            # Do an instant buy order
            econaccount.balance -= buy_quantity*currentprice
            stock_id = stockobject.id
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
