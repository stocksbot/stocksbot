import nextcord, schedule, logging

from nextcord.ext import commands

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class BotCore(commands.AutoShardedBot):

    # TODO: Remove hardcoding on engine URI
    engine = create_engine("sqlite:///data.db", echo=False)
    SQLSession = sessionmaker(bind=engine, expire_on_commit=False)
    db_session = SQLSession()

    async def on_ready(self):
        logging.info("Logged on as [{}]".format(self.user))
        logging.info("Using nextcord version {}".format(nextcord.__version__))

    async def on_message(self, message):
        logging.debug("Message from {0.author}: {0.content}".format(message))
        schedule.run_pending()

        await self.process_commands(message)

    async def on_command_error(self, ctx, err):
        if type(err) == nextcord.ext.commands.errors.CommandOnCooldown:
            await ctx.send("{0.mention}: **__{1}__**".format(ctx.author, err))
            return
        logging.error("Command error: {0} [author: {1.author}][cmd: {1.command}]".format(err, ctx))
        await ctx.send("**{0.mention}, that's an invalid command format.**".format(ctx.author))
