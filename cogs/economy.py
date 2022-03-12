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
        """Shows target account's balance. If target account is not specified, the bot shows your balance instead.
        
        Example Usage: s!bal <player_name>"""
        if target is None:
            target = ctx.author

        # Avoid inquiring balance of bots / Prevent bot account creation
        if target.bot:
            await ctx.send("Cannot inquire for bot's balance.")
            
        # Get current economy account
        else:
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
    
    @commands.command()
    @commands.is_owner()
    async def removeplayer(self, ctx, target: nextcord.Member):
        """Removes a player from the game.
        Note: Removing a player deletes the player's account data including all of his assets. Proceed with caution.
        
        Example Usage: s!removeplayer <player_name>"""
        if target is None:
            await ctx.send("No account found.")

        # Check if account targeted exists
        account_checked = EconomyAccount.get_economy_account(
            target,
            self.bot.db_session,
            False
        )

        # Delete targeted account (if it exists)

        if account_checked is None:
            await ctx.send("Account is not registered or does not exist.")
        
        else:
            account_deleted = EconomyAccount.delete_economy_account(
                target,
                self.bot.db_session
            )

            await ctx.send(
                CMD_REMOVE_PLAYER.format(target)
            )

            # Commit to DB
            self.bot.db_session.commit()

            # Logs
            logging.info("Deleted account {0}".format(target))

        


def setup(bot):
    bot.add_cog(Economy(bot))
