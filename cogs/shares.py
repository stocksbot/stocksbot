import logging

import nextcord
from nextcord import User
from nextcord.ext import commands

from messages.economy import *
from messages.income import *
from objects.stocks.shares import Shares
from objects.economy.account import EconomyAccount
from bot import BotCore


class SharesInfo(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def viewshares(self, ctx: commands.Context):
        """Returns your account's shares."""
        account = ctx.author
        if(isinstance(account, User)):
            await ctx.send(CMD_NO_GUILD)
            return
        # Get Economy Account
        econaccount = EconomyAccount.get_economy_account(account,self.bot.db_session,False)
        embed = nextcord.Embed(title="Your Shares", color=0xff1155)

        shares = Shares.get_all_shares(econaccount.id, self.bot.db_session)
        for share in shares:
            embed.add_field(name=share.stock.symbol, value=share.amount_held)
    
        await ctx.send(embed=embed)


def setup(bot:BotCore):
    bot.add_cog(SharesInfo(bot))
