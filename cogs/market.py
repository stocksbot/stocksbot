from typing import Union

import nextcord
from nextcord import User, Member
from nextcord.ext import commands
from datetime import datetime, timedelta

from objects.orders.buy import BuyOrder
from messages.economy import *
from messages.income import *
from objects.economy.account import EconomyAccount
from bot import BotCore
from objects.orders.buy import BuyOrder
from managers.sharesmanager import SharesManager, SharesManagerCodes


class Market(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def buy(self, ctx:commands.Context, symbol, quantity, price):
        """Command for buying stocks"""
        account = ctx.author
        if(isinstance(account,User)):
            await ctx.send(CMD_NO_GUILD)
            return
        status = SharesManager.buy_shares(account, symbol, quantity, price, self.bot.db_session)
        if status == SharesManagerCodes.SUCCESS_INSTANT:
            await ctx.send(CMD_INST_BO)
        elif status == SharesManagerCodes.SUCCESS_PENDING:
            await ctx.send(CMD_PEND_BO)
        elif status == SharesManagerCodes.ERR_ACC_DNE:
            await ctx.send(CMD_ACC_MISSING)
        elif status == SharesManagerCodes.ERR_BAL_INSF:
            await ctx.send(CMD_NO_BALANCE)
        elif status == SharesManagerCodes.ERR_STOCK_DNE:
            await ctx.send(CMD_NO_STOCK)
        else:
            await ctx.send("Error, something happened")
    @commands.command()
    async def viewbuys(self, ctx:commands.Context, stock = None):
        """View all your pending buy orders"""
        account = ctx.author
        BuyOrder.get_all_buyorders(account.id, self.bot.db_session)
        

def setup(bot:BotCore):
    bot.add_cog(Market(bot))
