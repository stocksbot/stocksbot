import logging

import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta

from messages.economy import *
from messages.income import CMD_CLAIM, CMD_CLAIMFAILHOURS, CMD_CLAIMFAILMINUTES, CMD_INCOME, CMD_SUCCESS_UPDATEINCOME
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

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def updateincome(self, ctx, target: nextcord.Member=None, newincome: float=None):
        """(Owner/Admin) Updates a player's income status."""
        if newincome is None:
            await ctx.send("Invalid command usage. Try **s!help updateincome** for help regarding this command.")
        else:
            # Check if targeted account exists
            account_checked = EconomyAccount.get_economy_account(
                target,
                self.bot.db_session,
                False
            )

            # Update income status of targeted account (if it exists)
            if account_checked is None:
                await ctx.send(ACC_DNE.format(target))
            
            else:
                account = EconomyAccount.updateincome(
                    account_checked,
                    self.bot.db_session,
                    newincome
                )
    
                await ctx.send(CMD_SUCCESS_UPDATEINCOME.format(target, newincome))


def setup(bot):
    bot.add_cog(Income(bot))