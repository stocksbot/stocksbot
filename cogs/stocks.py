import logging
import nextcord

from nextcord.ext import commands, tasks
from objects.stocks.stock import Stock

from fetch.yahoo import YahooFetcher

fetcher = YahooFetcher()


class StocksManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stock_prices.start()

    @tasks.loop(minutes=15.0)
    async def update_stock_prices(self):
        logging.info("Running stock price fetch.")
        fetcher.run()

        logging.debug(fetcher.clean_data)
        print(fetcher.clean_data)
        logging.info("Updating stock prices.")
        Stock.update_stocks(
            fetcher.clean_data, 
            self.bot.db_session
        )


def setup(bot):
    bot.add_cog(StocksManager(bot))