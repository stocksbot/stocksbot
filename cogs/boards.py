import logging
from nextcord import User, Member

import nextcord
from typing import Union
from nextcord.ext import commands
from bot import BotCore

from objects.economy.account import EconomyAccount
from objects.boards.local import LocalLeaderboard

from table2ascii import table2ascii as t2a, PresetStyle


class Boards(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot


    @commands.command()
    async def localboard(self, ctx:commands.Context):
        target = ctx.author
        leaderboard = LocalLeaderboard.get_local_leaderboard(
            target,
            self.bot.db_session
        )
        rank = [str(num+1) for num in range(leaderboard.size)]
        top_users_name = leaderboard.top_users_name.split(' ')
        top_users_tag = leaderboard.top_users_tag.split(' ')
        points = leaderboard.points.split(' ')
        size = leaderboard.size

        output = t2a(
        header=["Rank", "Username", "Tag", "Points"],
        body=list(zip(rank, top_users_name, top_users_tag, points)),
        style=PresetStyle.thin_compact
        )
        
        await ctx.send(f"```\n{output}\n```")
   
        


def setup(bot:BotCore):
    bot.add_cog(Boards(bot))

