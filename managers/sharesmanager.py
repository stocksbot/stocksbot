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
    def buy_shares(account_id, symbol, buy_quantity, buy_price, session:Session):
        """Increase owned shares while decreasing corresponding balance"""

        #Check if account balance can do order
        econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == account_id).first()
        if(econaccount == None):
            logging.error("[ERROR] Account does not exist")
            # Account does not exist
            return SharesManagerCodes.ERR_ACC_DNE
        if(buy_quantity * buy_price > econaccount.get_balance):
            # Account does not have enough balance to place such buy order
            return SharesManagerCodes.ERR_BAL_INSF
        stockobject = Stock.get_stock(symbol, session)
        if(stockobject == None):
            # Stock does not exist
            return SharesManagerCodes.ERR_STOCK_DNE
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
            session.commit()
            return SharesManagerCodes.SUCCESS_INSTANT
        else:
            # Do a pending buy order
            econaccount.balance -= buy_quantity*buy_price # Reserve balance from account for pending buy order
            BuyOrder.create_buyorder(econaccount.id, stockobject.id, buy_price, buy_quantity, session)
            session.commit()
            return SharesManagerCodes.SUCCESS_PENDING
