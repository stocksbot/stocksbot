import logging

import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta

from messages.economy import *
from messages.income import CMD_CLAIM, CMD_CLAIMFAILHOURS, CMD_CLAIMFAILMINUTES, CMD_INCOME
from objects.economy.account import EconomyAccount


class Income(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def showincome(self, ctx, target: nextcord.Member=None):
        """Returns target account's income."""
        if target is None:
            target = ctx.author
        # Get current economy account
        account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        await ctx.send(CMD_INCOME.format(target, account.get_income()))

    @commands.command()
    async def claimincome(self, ctx):
        """Dispenses income to author's account"""
        account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        status = account.dispense_income(self.bot.db_session)
        if(status == 0):
            await ctx.send(CMD_CLAIM.format(ctx.author, account.get_income(), account.get_balance()))
        else:
            nextready = account.lastclaim + timedelta(days=1)
            timediff = nextready - datetime.now()
            hours = timediff.seconds//3600
            minutes = (timediff.seconds//60)%60
            if(hours >= 1):
                await ctx.send(CMD_CLAIMFAILHOURS.format(hours,minutes))
            else:
                await ctx.send(CMD_CLAIMFAILMINUTES.format(minutes))


def setup(bot):
    bot.add_cog(Income(bot))