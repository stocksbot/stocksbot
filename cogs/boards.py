import logging
from nextcord import User, Member

import nextcord
from typing import Union
from nextcord.ext import commands
from bot import BotCore

from objects.economy.account import EconomyAccount
from objects.stocks.shares import Shares
from objects.stocks.stock import Stock

from table2ascii import table2ascii as t2a, PresetStyle


class Boards(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot


    @commands.command()
    async def localboard(self, ctx:commands.Context, size=10):
        """Shows the Local Leaderboard. If size of board is not specified, the bot returns a leaderboard of size 10 by default.
        To avoid spamming, the maximum size of board is limited to 40."""
        target = ctx.author

        # avoid spamming the discord channel from someone requesting a gigantic leaderboard (limit size to 40)
        size = min(size, 40)

        # Get the list of users in the guild and sort by balance
        users = EconomyAccount.get_guild_accounts(
            self,
            self.bot.db_session,
            target.guild.id
        )

        ordered_users = users.order_by(EconomyAccount.balance)

        # Build the local board
        local_leaderboard = []
        
        # Add players in the guild to the localboard
        for player in ordered_users:
            temp = []
            temp.append(player.name)
            temp.append(str(player.tag))
            # Calculate the player net_worth
            net_worth = 0

            # Add player balance to net_worth
            net_worth += player.balance / 10000 # Convert to database-friendly format

            # Get all shares of player
            shares = Shares.get_all_shares(
                player.id,
                self.bot.db_session
            )

            # Get monetary value obtained from all shares
            for share in shares:
                # Get symbol
                sym = Stock.get_symbol(
                    share.stock_id,
                    self.bot.db_session
                )
                # Get stock
                stock = Stock.get_stock(
                    sym,
                    self.bot.db_session
                )
                # Get price
                price = Stock.get_price(
                    stock
                )

                # Add the monetary value from the share to the net_worth
                net_worth += (share.amount_held * price)

            temp.append(str(net_worth))
            local_leaderboard.append(temp)

        # sort leaderboard by decreasing net worth
        sorted_local_board = sorted(local_leaderboard, key=lambda x:float(x[2]), reverse=True)

        # Append empty local board contents (for aesthetics in case there are less players than the size of board)
        if len(sorted_local_board) < size:
            for i in range(size - len(sorted_local_board)):
                sorted_local_board.append(["----","----","----"])
    
        # output according to the desired size
        output = sorted_local_board[:size]

        # insert ranks to the output
        for rank in range(size):
            output[rank].insert(0, str(rank+1))

        # create the table
        table = t2a(
            header = ["Rank", "Username", "Tag", "Net Worth"],
            body = output,
            style=PresetStyle.thin_compact
            )
        
        await ctx.send(f"```\n{table}\n```")
        


def setup(bot:BotCore):
    bot.add_cog(Boards(bot))

