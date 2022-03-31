from decimal import Context
from typing import Union
import logging

import nextcord
from nextcord import User
from nextcord.ext import commands
from datetime import datetime, timedelta

from messages.economy import *
from messages.income import *
from objects.stocks.stock import Stock
from bot import BotCore


class StocksInfo(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def stockprices(self, ctx: commands.Context):
        """Returns target account's income."""
        embed = nextcord.Embed(title="Stock Prices", color=0xff1155)

        stocks = Stock.get_all(self.bot.db_session)
        for stock in stocks:
            embed.add_field(name=stock.symbol, value=stock.get_price())
    
        await ctx.send(embed=embed)


def setup(bot:BotCore):
    bot.add_cog(StocksInfo(bot))
