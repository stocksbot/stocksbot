from enum import Enum
from typing import Optional
import logging

from sqlalchemy.orm import Session

from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from objects.economy.account import EconomyAccount
from objects.orders.buy import BuyOrder
from objects.orders.sell import SellOrder

class SharesManagerCodes(Enum):
    SUCCESS_INSTANT = 0
    SUCCESS_PENDING = 1
    ERR_ACC_DNE = 2
    ERR_BAL_INSF = 3
    ERR_STOCK_DNE = 4

class SharesManager():
    @staticmethod
    def buy_shares(account:EconomyAccount, symbol: str, buy_quantity: int, buy_price: int, session:Session):
        """Increase owned shares while decreasing corresponding balance"""

        #Check if account balance can do order
        if(buy_quantity * buy_price > account.balance):
            # Account does not have enough balance to place such buy order
            return SharesManagerCodes.ERR_BAL_INSF
        stockobject = Stock.get_stock(symbol, session)
        if(stockobject == None):
            # Stock does not exist
            return SharesManagerCodes.ERR_STOCK_DNE
        currentprice = stockobject.price # store price to avoid race conditions
        if(currentprice <= buy_price):
            # Do an instant buy order
            account.decreasebalance(session, buy_quantity*currentprice, True, False)
            stock_id = stockobject.id
            shareQuery = session.query(Shares).filter(
            Shares.stock_id == stock_id, 
            Shares.account_id == account.id
            ).first()
            if(shareQuery == None):
                shareQuery = Shares.create_shareholder(account.id, symbol, buy_quantity, session)
            else:
                shareQuery.increment_shares(account.id,stock_id,buy_quantity,session,False)
            session.commit()
            return SharesManagerCodes.SUCCESS_INSTANT
        else:
            # Do a pending buy order
            account.decreasebalance(session, buy_quantity*buy_price, True, False) # Reserve balance from account for pending buy order
            BuyOrder.create_buyorder(account.id, stockobject.id, buy_price, buy_quantity, session)
            session.commit()
            return SharesManagerCodes.SUCCESS_PENDING

    @staticmethod
    def sell_shares(account:EconomyAccount, symbol: str, sell_quantity: int, sell_price: int, session:Session):
        """Decrease owned shares while increasing corresponding balance"""

        # Get stock object
        stockobject = Stock.get_stock(symbol, session)
        if(stockobject == None):
            # Stock does not exist
            return SharesManagerCodes.ERR_STOCK_DNE
        
        # Check if seller has enough shares
        sharesheld = Shares.get_shares_held(account.id, symbol, session)
        if(sharesheld < sell_quantity):
            # Not enough shares
            return SharesManagerCodes.ERR_BAL_INSF

        # Get share object
        stock_id = stockobject.id
        shareQuery = session.query(Shares).filter(
            Shares.stock_id == stock_id, Shares.account_id == account.id
            ).first() # type: Optional[Shares]
            
        if(shareQuery == None):
            # Some really bad race condition happened
            session.rollback()
            return SharesManagerCodes.ERR_BAL_INSF

        currentprice = stockobject.price # store price to avoid race conditions
        if(currentprice >= sell_price):
            # Do an instant sell order
            account.increasebalance(session, sell_quantity*currentprice, True, False)
            status = shareQuery.decrement_shares(account.id, stock_id, sell_quantity, session, False) 
            if(status == -1):
                # Some Really Bad Race Condition Happened
                session.rollback()
                return SharesManagerCodes.ERR_BAL_INSF
            session.commit()
            return SharesManagerCodes.SUCCESS_INSTANT
        else:
            # Do a pending sell order
            shareQuery.decrement_shares(account.id, stock_id, sell_quantity, session, False) # Reserve shares from account for pending sell order
            SellOrder.create_sellorder(account.id, stockobject.id, sell_price, sell_quantity, session)
            session.commit()
            return SharesManagerCodes.SUCCESS_PENDING