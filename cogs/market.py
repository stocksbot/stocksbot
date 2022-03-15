from symtable import Symbol
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
from objects.stocks.stock import Stock

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
        embed = nextcord.Embed()
        account = ctx.author
        if(stock == None):
            orders = BuyOrder.get_all_buyorders(account.id, self.bot.db_session)
            if(not orders):
                await ctx.send("You have no pending buy orders")
                return
            embed = nextcord.Embed(title="{0.s}'s Buy Orders".format(ctx.author.display_name), color=0xff1155)
            for order in orders:
                embed.add_field(name = order.id, value = "{Symbol}: {Quantity} Shares @ ${Price}".format(
                    Symbol = Stock.get_symbol(order.stock_id,self.bot.db_session), 
                    Quantity = order.buy_quantity,
                    Price = order.buy_price / 10000
                    )
                )
        else:
            if(Stock.get_stock(stock,self.bot.db_session) == None):
                await ctx.send(CMD_NO_STOCK)
                return
            orders = BuyOrder.get_stock_buyorders(account.id, stock, self.bot.db_session)
            if(not orders):
                await ctx.send("You have no pending {} buy orders".format(stock))
                return
            embed = nextcord.Embed(title="{0.s}'s {} Buy Orders".format(ctx.author.display_name, stock), color=0xff1155)
            for order in orders:
                embed.add_field(name = order.id, value = "{Quantity} Shares @ ${Price}".format( 
                    Quantity = order.buy_quantity,
                    Price = order.buy_price / 10000
                    )
                )
        await ctx.send(embed=embed)
        

def setup(bot:BotCore):
    bot.add_cog(Market(bot))
