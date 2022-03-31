from random import randint
import logging

from objects.stocks.stock import Stock
from fetch.yahoo import YahooFetcher
from sqlalchemy.orm import Session

# To-do: Automate stocks seed generation for several data sources 
fetcher = YahooFetcher()

def seed(session:Session):
    fetcher.run()

    existing_stocks = [i.symbol for i in session.query(Stock).all()]
    stocks = fetcher.clean_data
    if(stocks == None):
        logging.error("[ERROR] No stocks seeded")
        return
    for stock in stocks:
        # Skip if exists
        if stock["symbol"] in existing_stocks:
            continue

        session.add(Stock(
            name = stock["name"],
            symbol = stock["symbol"],
            price = stock["price"],
        ))

    session.commit()
