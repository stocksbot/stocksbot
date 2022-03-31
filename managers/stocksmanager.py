import logging

from sqlalchemy.orm import Session

from objects.stocks.stock import Stock


class StocksManager():

    @staticmethod
    def update_stock_prices(session:Session, fetcher):
        """Checks and executes candidate buyorders"""
        logging.info("Running stock price fetch.")
        fetcher.run()

        logging.debug(fetcher.clean_data)
        print(fetcher.clean_data)
        logging.info("Updating stock prices.")
        Stock.update_stocks(
            fetcher.clean_data, 
            session
        )
