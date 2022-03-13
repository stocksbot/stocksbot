from __future__ import annotations
import logging

from objects.economy.account import EconomyAccount
from objects.stocks.stock import Stock
from objects.stocks.shares import Shares
from objects.orders.buy import BuyOrder
from sqlalchemy.orm import Session

class OrderManager():

    @staticmethod
    def checkex_buyorders(session:Session):
        """Checks and executes candidate buyorders"""
        BuyOrders = session.query(BuyOrder).all()
        for order in BuyOrders:
            stock = session.query(Stock).filter(Stock.id == order.stock_id).first()
            if(stock == None):
                logging.error("[ERROR] Stock does not exist")
                continue
            currentprice = stock.price
            if(currentprice <= order.buy_price):
                econaccount = session.query(EconomyAccount).filter(EconomyAccount.id == order.account_id).first()
                if(econaccount == None):
                    continue
                Shares.increment_shares(order.account_id, order.stock_id, order.buy_quantity, session, False)
                econaccount.balance += order.buy_quantity*(order.buy_price - currentprice) #refund reserved balance, IGNORE THIS
                BuyOrder.delete_buyorder(order.id,session,False)
                session.commit()