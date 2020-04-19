import traceback
from discord.ext import commands
from rosterbot.rosterbot import logger
from rosterbot.constants import DEVELOPER_USER_ID

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)
        await self.bot.get_user(DEVELOPER_USER_ID).send(f"User {ctx.message.author.display_name} experienced error: ```{error}``` The traceback: ```{traceback.print_exception(type(error), error, error.__traceback__)}```")
        await logger.log(error)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await self.bot.get_user(DEVELOPER_USER_ID).send(f"An error has occured for {event}: ```{traceback.format_exc()}```")
        logger.log(traceback.format_exc())

def setup(bot):
    bot.add_cog(Errors(bot))