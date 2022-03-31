import logging
import nextcord

from bot import BotCore
from nextcord.ext import commands, tasks
from objects.stocks.stock import Stock

from fetch.yahoo import YahooFetcher
from managers.stocksmanager import StocksManager
from managers.ordermanager import OrderManager

fetcher = YahooFetcher()


class Tasks(commands.Cog):
    def __init__(self, bot:BotCore):
        self.bot = bot
        self.game_logic_tasks.start()

    @tasks.loop(minutes=15.0)
    async def game_logic_tasks(self):
        # Run all functions called below every 15 minutes
        fetcher = YahooFetcher()
        StocksManager.update_stock_prices(self.bot.db_session, fetcher)
        OrderManager.checkex_buyorders(self.bot.db_session)
        OrderManager.checkex_sellorders(self.bot.db_session)

def setup(bot:BotCore):
    bot.add_cog(Tasks(bot))
