import logging

import nextcord
from nextcord.ext import commands

from messages.economy import *
from objects.economy.account import EconomyAccount


class Economy(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bal(self, ctx):
        """Returns your account balance.
        
        Example Usage: s!bal"""
        target = ctx.author

        # Get current economy account
        account = EconomyAccount.get_economy_account(
            target,
            self.bot.db_session
        )
        await ctx.send(CMD_BAL.format(target, account.get_balance()))

    @commands.command()
    @commands.is_owner()
    async def registerall(self, ctx):
        """(Owner) Gives all users in guild economy accounts.
        
        Example Usage: s!registerall"""
        registered = 0
        for member in ctx.guild.members:

            # Avoid account creation for bots
            if member.bot:
                continue

            # Check if user exists, else create
            k = EconomyAccount.get_economy_account(
                member,
                self.bot.db_session,
                create_if_not_exists=False
            )

            if k is None:
                k = EconomyAccount.create_economy_account(
                    member, self.bot.db_session,
                    member.bot or member.system, commit_on_execution=False
                )
                registered += 1

        # Commit to DB
        self.bot.db_session.commit()

        # Logs
        logging.info("Registered {0} new accounts in the Economy database.".format(registered))
    
    @commands.command()
    @commands.is_owner()
    async def removeplayer(self, ctx, target: nextcord.Member):
        """Returns target account's balance."""
        if target is None:
            await ctx.send("No account found.")

        # Find targeted account
        account = EconomyAccount.delete_economy_account(
            target,
            self.bot.db_session
        )

        # Commit to DB
        self.bot.db_session.commit()

        # Logs
        logging.info("Deleted account {0}".format(target))

        await ctx.send(
            CMD_REMOVE_PLAYER.format(target)
        )


def setup(bot):
    bot.add_cog(Economy(bot))
