from symtable import Symbol
from typing import Union

import nextcord
import math
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
from typing import Optional

class Market(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def buy(self, ctx:commands.Context, symbol: str, quantity: int, price: float):
        """Command for buying stocks"""
        # Check if values are valid
        member = ctx.author
        if(isinstance(member,User)):
            await ctx.send(CMD_NO_GUILD)
            return
        if(quantity<=0):
            await ctx.send(CMD_QTY_NP)
            return
        if(price < 0):
            await ctx.send(CMD_PRC_NN)
            return
        # Convert to raw
        price *= 10000
        price = math.floor(price)
        # Get economy account
        account = EconomyAccount.get_economy_account(member, self.bot.db_session, False)
        if(account == None):
            await ctx.send(CMD_ACC_MISSING)
            return
        # Call buy_shares and handle status return
        status = SharesManager.buy_shares(account, symbol, quantity, price, self.bot.db_session)
        if status == SharesManagerCodes.SUCCESS_INSTANT:
            await ctx.send(CMD_INST_BO)
        elif status == SharesManagerCodes.SUCCESS_PENDING:
            await ctx.send(CMD_PEND_BO)
        elif status == SharesManagerCodes.ERR_BAL_INSF:
            await ctx.send(CMD_NO_BALANCE)
        elif status == SharesManagerCodes.ERR_STOCK_DNE:
            await ctx.send(CMD_NO_STOCK)
        else:
            await ctx.send("Error, something happened")

    @commands.command()
    async def viewbuys(self, ctx:commands.Context, stock: Optional[str] = None):
        """View all your pending buy orders"""
        embed = nextcord.Embed()
        account = ctx.author
        if(isinstance(account,User)):
            await ctx.send(CMD_NO_GUILD)
            return
        # Get Economy Account
        econaccount = EconomyAccount.get_economy_account(account,self.bot.db_session,False)
        if(econaccount == None):
            await ctx.send(CMD_ACC_MISSING)
            return
        # Show all buy orders
        if(stock == None):
            orders = BuyOrder.get_all_buyorders(econaccount.id, self.bot.db_session)
            if(not orders):
                await ctx.send("You have no pending buy orders")
                return
            embed = nextcord.Embed(title="{}'s Buy Orders".format(ctx.author.display_name), color=0xff1155)
            for order in orders:
                embed.add_field(name = "Order ID: {}".format(order.id), value = "{Symbol}: {Quantity} Shares @ ${Price}".format(
                    Symbol = Stock.get_symbol(order.stock_id,self.bot.db_session), 
                    Quantity = order.buy_quantity,
                    Price = order.buy_price / 10000
                    )
                )
        # Show all buy orders of a specific stock
        else:
            if(Stock.get_stock(stock,self.bot.db_session) == None):
                await ctx.send(CMD_NO_STOCK)
                return
            orders = BuyOrder.get_stock_buyorders(econaccount.id, stock, self.bot.db_session)
            if(not orders):
                await ctx.send("You have no pending {} buy orders".format(stock))
                return
            embed = nextcord.Embed(title="{}'s {} Buy Orders".format(ctx.author.display_name, stock), color=0xff1155)
            for order in orders:
                embed.add_field(name = "Order ID: {}".format(order.id), value = "{Quantity} Shares @ ${Price}".format( 
                    Quantity = order.buy_quantity,
                    Price = order.buy_price / 10000
                    )
                )
        await ctx.send(embed=embed)

    @commands.command()
    async def sell(self, ctx:commands.Context, symbol: str, quantity: int, price: float):
        """Command for buying stocks"""
        # Check if values are valid
        member = ctx.author
        if(isinstance(member,User)):
            await ctx.send(CMD_NO_GUILD)
            return
        if(quantity <= 0):
            await ctx.send(CMD_QTY_NP)
            return
        if(price < 0):
            await ctx.send(CMD_PRC_NN)
            return
        # Convert to raw
        price *= 10000
        price = math.floor(price)
        # Get economy account
        account = EconomyAccount.get_economy_account(member, self.bot.db_session, False)
        if(account == None):
            await ctx.send(CMD_ACC_MISSING)
            return
        # Call sell_shares and handle status return
        status = SharesManager.sell_shares(account, symbol, quantity, price, self.bot.db_session)
        if status == SharesManagerCodes.SUCCESS_INSTANT:
            await ctx.send(CMD_INST_SO)
        elif status == SharesManagerCodes.SUCCESS_PENDING:
            await ctx.send(CMD_PEND_SO)
        elif status == SharesManagerCodes.ERR_BAL_INSF:
            await ctx.send(CMD_NO_SHARES)
        elif status == SharesManagerCodes.ERR_STOCK_DNE:
            await ctx.send(CMD_NO_STOCK)
        else:
            await ctx.send("Error, something happened")
        

def setup(bot:BotCore):
    bot.add_cog(Market(bot))
