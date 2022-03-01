import logging

import nextcord
from nextcord.ext import commands

from messages.economy import *
from objects.economy.account import EconomyAccount


class Economy(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bal(self, ctx, target: nextcord.Member=None):
        """Returns target account's balance."""
        if target is None:
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
        """(Owner) Gives all users in guild economy accounts."""
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


def setup(bot):
    bot.add_cog(Economy(bot))
