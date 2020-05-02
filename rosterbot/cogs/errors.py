import traceback
from discord.ext import commands
from discord.utils import get
from rosterbot.models import customerrors
from rosterbot.rosterbot import logger, settings
from rosterbot.constants import DEVELOPER_USER_ID

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, customerrors.NotCOError):
            local_settings = settings.get_server_settings(ctx.guild.id)
            co_role = get(ctx.guild.roles, name=local_settings['co_role_name'])
            if co_role is not None:
                await ctx.channel.send(f"The {co_role} role is needed to run this command.")
            else:
                await ctx.channel.send("The co_role_name setting is invalid or not configured.")
        elif isinstance(error, customerrors.NotRosterManagerError):
            local_settings = settings.get_server_settings(ctx.guild.id)
            roster_manager_role = get(ctx.guild.roles, name=local_settings['roster_manager_role_name'])
            co_role = get(ctx.guild.roles, name=local_settings['co_role_name'])
            if roster_manager_role is not None and co_role is not None:
                await ctx.channel.send(f"The {roster_manager_role} or {co_role} roles are needed to run this command.")
            else:
                await ctx.channel.send("Either the roster_manager_role_name or co_role_name settings are invalid or not configured.")
        else:
            await ctx.channel.send(error)
            await self.bot.get_user(DEVELOPER_USER_ID).send(f"User {ctx.message.author.display_name} experienced error: ```{error}``` The traceback: ```{traceback.print_exception(type(error), error, error.__traceback__)}```")
            await logger.log(error)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await self.bot.get_user(DEVELOPER_USER_ID).send(f"An error has occured for {event}: ```{traceback.format_exc()}```")
        logger.log(traceback.format_exc())

def setup(bot):
    bot.add_cog(Errors(bot))