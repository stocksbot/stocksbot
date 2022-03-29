from enum import Enum
import logging

from sqlalchemy.orm import Session

from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from objects.economy.account import EconomyAccount
from objects.orders.buy import BuyOrder

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
            Shares.stock_id == stock_id, Shares.account_id == account.id
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
