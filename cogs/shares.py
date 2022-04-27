import logging

import nextcord
from nextcord import User
from nextcord.ext import commands

from messages.economy import *
from messages.income import *
from objects.stocks.shares import Shares
from objects.economy.account import EconomyAccount
from bot import BotCore

from datetime import datetime


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
        embed = nextcord.Embed(
            title="{}'s Shares".format(ctx.author.display_name), 
            color=0xFFD700
        )

        shares = Shares.get_all_shares(econaccount.id, self.bot.db_session)
        for share in shares:
            embed.add_field(
                name=share.stock.symbol,
                value="Amount: {}".format(share.amount_held),
                inline=True
            )
    
        now = datetime.utcnow()
        now_as_string = now.strftime("%m/%d/%Y %H:%M:%S")
        footer_text = "as of {} UTC".format(now_as_string)
        embed.set_footer(text=footer_text)

        await ctx.send(embed=embed)


def setup(bot:BotCore):
    bot.add_cog(SharesInfo(bot))
