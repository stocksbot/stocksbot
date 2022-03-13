import logging
from datetime import timedelta
from time import time

import nextcord
from nextcord.ext import commands
from bot import BotCore
from messages.core import *

start_time = time()


class Core(commands.Cog):
    def  __init__(self, bot:BotCore):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx:commands.Context):
        """Tests responsiveness."""
        latency_in_ms = "{} ms".format(int(self.bot.latency * 1000))
        await ctx.send(CMD_PING.format(latency_in_ms))

    
    @commands.command()
    async def help(self, ctx:commands.Context, command=None):
        """Shows all the features the bot is able to do."""
        all_commands = [cmd for cmd in self.bot.commands]
        if command == None:
            embed = nextcord.Embed(title="Commands for Stocks Bot", color=0xff1155)
            for cog in self.bot.cogs:

                # Exclude stocks cogs from help
                if str(cog) == "StocksManager": 
                    continue

                commands_for_cog = [f'`{c.name}`' for c in all_commands if not c.hidden and c.cog_name == cog]
                s = ' '.join(commands_for_cog)
                embed.add_field(name=cog, inline=False, value=s)
            await ctx.send("Do `s!help <command>` for more information.")
        else:
            if command not in [c.name for c in all_commands]:
                await ctx.send(MSG_CMD_NOT_FOUND.format(ctx.author))
                return
            cmd = [c for c in all_commands if c.name == command][0]
            if cmd.aliases:
                name = f'{cmd.name} [{"/".join(cmd.aliases)}]'
            else:
                name = cmd.name
            if cmd.clean_params:
                name += f' <{", ".join(cmd.clean_params)}>'
            name = '`{}`'.format(name)
            embed = nextcord.Embed(title=cmd.cog_name, color=0xff1155)
            embed.add_field(name=name, value=cmd.help)
        await ctx.send(embed=embed)


def setup(bot:BotCore):
    bot.add_cog(Core(bot))
