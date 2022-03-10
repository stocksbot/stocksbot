from random import randint

from objects.stocks.stock import Stock
from fetch.yahoo import YahooFetcher

# To-do: Automate stocks seed generation for several data sources 
fetcher = YahooFetcher()

def seed(session):
    fetcher.run()

    existing_stocks = [i.symbol for i in session.query(Stock).all()]
    stocks = fetcher.clean_data
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
