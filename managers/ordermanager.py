from __future__ import annotations
import logging
from typing import List, Optional

from objects.economy.account import EconomyAccount
from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from objects.orders.buy import BuyOrder
from objects.orders.sell import SellOrder
from sqlalchemy.orm import Session
from sqlalchemy.types import BigInteger

class OrderManager():

    @staticmethod
    def checkex_buyorders(session:Session):
        """Checks and executes candidate buyorders"""
        BuyOrders = session.query(BuyOrder).all() # type: List[BuyOrder]
        for order in BuyOrders:
            stock = session.query(Stock).filter(Stock.id == order.stock_id).first() # type: Optional[Stock]
            if(stock == None):
                logging.error("[ERROR] Stock does not exist")
                continue
            currentprice = stock.price
            if(currentprice <= order.buy_price):
                econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == order.account_id).first() # type: Optional[EconomyAccount]
                if(econaccount == None):
                    continue
                Shares.increment_shares(order.account_id, order.stock_id, order.buy_quantity, session, False)
                econaccount.increasebalance(session,(order.buy_quantity*(order.buy_price - currentprice)), True, False) #refund reserved balance
                BuyOrder.delete_buyorder(order.id,session,False)
                session.commit()

    @staticmethod
    def checkex_sellorders(session:Session):
        """Checks and executes candidate sellorders"""
        SellOrders = session.query(SellOrder).all() # type: List[SellOrder]
        for order in SellOrders:
            stock = session.query(Stock).filter(Stock.id == order.stock_id).first() # type: Optional[Stock]
            if(stock == None):
                logging.error("[ERROR] Stock does not exist")
                continue
            currentprice = stock.price
            if(currentprice >= order.sell_price):
                econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == order.account_id).first() # type: Optional[EconomyAccount]
                if(econaccount == None):
                    continue
                econaccount.increasebalance(session,(order.sell_quantity*order.sell_price), True, False) #refund reserved balance
                SellOrder.delete_sellorder(order.id,session,False)
                session.commit()

    @staticmethod
    def cancel_buyorder(session:Session, EconAccount: EconomyAccount, OrderID: int):
        """
            Checks if you can cancel the buyorder and then does so if possible
            return statuses
            0 = successful
            1 = something went wrong
        """
        EconID = EconAccount.id
        BuyOrders = BuyOrder.get_all_buyorders(EconID, session)
        targetOrder = None
        for order in BuyOrders:
            if order.id == OrderID:
                targetOrder = order
                break
        if targetOrder is None:
            return 1
        else:
            refund = targetOrder.buy_price * targetOrder.buy_quantity
            EconAccount.increasebalance(session, refund, True, False)
            rows_deleted = targetOrder.delete(session, False)
            if rows_deleted > 0:
                session.commit()
                return 0
            else:
                session.rollback()
                return 1

    @staticmethod
    def cancel_sellorder(session:Session, EconAccount: EconomyAccount, OrderID: int):
        """
            Checks if you can cancel the sellorder and then does so if possible
            return statuses
            0 = successful
            1 = something went wrong
        """
        EconID = EconAccount.id
        SellOrders = SellOrder.get_all_sellorders(EconID, session)
        targetOrder = None
        for order in SellOrders:
            if order.id == OrderID:
                targetOrder = order
                break
        if targetOrder is None:
            return 1
        else:
            Shares.increment_shares(EconID, targetOrder.stock_id, targetOrder.sell_quantity, session, False)
            rows_deleted = targetOrder.delete(session, False)
            if rows_deleted > 0:
                session.commit()
                return 0
            else:
                session.rollback()
                return 1
