from decimal import Context
from typing import Union, Optional
import logging

import nextcord
from nextcord import User
from nextcord.ext import commands
from datetime import datetime, timedelta

from messages.economy import *
from messages.income import CMD_CLAIM, CMD_CLAIMFAILHOURS, CMD_CLAIMFAILMINUTES, CMD_INCOME, CMD_SUCCESS_UPDATEINCOME
from objects.economy.account import EconomyAccount
from objects.boards.local import LocalLeaderboard
from bot import BotCore


class Income(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def showincome(self, ctx:commands.Context, target: Union[nextcord.User, nextcord.Member, None]=None):
        """Returns target account's income."""
        if target is None:
            target = ctx.author
        # Get current economy account
        if isinstance(target, User):
            await ctx.send(CMD_NO_GUILD)
            return
        account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        if(account == None):
            await ctx.send(CMD_ACC_MISSING)
            return
        await ctx.send(CMD_INCOME.format(target, account.get_income()))

    @commands.command()
    async def claimincome(self, ctx:commands.Context):
        """Dispenses income to author's account"""
        target = ctx.author
        if isinstance(target,User):
            await ctx.send(CMD_NO_GUILD)
            return
        account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        if(account == None):
            await ctx.send(CMD_ACC_MISSING)
            return
        status = account.dispense_income(self.bot.db_session)
        if(status == 0):
            await ctx.send(CMD_CLAIM.format(ctx.author, account.get_income(), account.get_balance()))
            # Update the local leaderboard
            rank = LocalLeaderboard.update_local_leaderboard(target, self.bot.db_session)

            # Inform player of his/her placement on the leaderboard
            if rank != 0:
                await ctx.send("🎉 Congratulations! You've earned a spot on the Local Leaderboard. **s!localboard** to know your position.")

        else:
            timediff = status - datetime.now()
            hours = timediff.seconds//3600
            minutes = (timediff.seconds//60)%60
            if(hours >= 1):
                await ctx.send(CMD_CLAIMFAILHOURS.format(hours,minutes))
            else:
                await ctx.send(CMD_CLAIMFAILMINUTES.format(minutes))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True)) # type: ignore
    async def updateincome(self, ctx, target: Union[nextcord.Member,nextcord.User,None]=None, newincome: Optional[float]=None):
        """(Owner/Admin) Updates a player's income status."""
        if newincome is None:
            await ctx.send("Invalid command usage. Try **s!help updateincome** for help regarding this command.")
        else:
            # Check if target is Member
            if not isinstance(target, nextcord.Member):
                await ctx.send(CMD_NO_GUILD)
                return

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


def setup(bot:BotCore):
    bot.add_cog(Income(bot))
