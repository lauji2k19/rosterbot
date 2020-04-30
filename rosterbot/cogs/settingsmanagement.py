import discord
import asyncio
from discord.ext import commands
from discord.utils import get
from rosterbot.rosterbot import settings, roster_sheet
from rosterbot.models import singleunit

class SettingsManagement(commands.Cog, name='Settings Management'):
    """Commands related to adjusting the settings for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        embed = discord.Embed(
            title = 'Settings',
            description = f"All available settings. Use {local_settings['bot_prefix']}setting_name to change a setting."
        )
        embed.add_field(name="division_name", value=f"{local_settings['division_name']}", inline=False)
        embed.add_field(name="roster_channel_id", value=f"{local_settings['roster_channel_id']}", inline=False)
        embed.add_field(name="co_comms_channel_id", value=f"{local_settings['co_comms_channel_id']}", inline=False)
        embed.add_field(name="log_channel_id", value=f"{local_settings['bot_log_channel_id']}", inline=False)
        embed.add_field(name="command_channel_id", value=f"{local_settings['bot_command_channel_id']}", inline=False)
        embed.add_field(name="command_prefix", value=f"{local_settings['bot_prefix']}", inline=False)
        embed.add_field(name="co_role_name", value=f"{local_settings['co_role_name']}", inline=False)
        embed.add_field(name="roster_manager_role_name", value=f"{local_settings['roster_manager_role_name']}", inline=False)
        embed.add_field(name="enlisted_role_name", value=f"{local_settings['enlisted_role_name']}", inline=False)
        embed.add_field(name="loa_role_name", value=f"{local_settings['loa_role_name']}", inline=False)
        embed.add_field(name="check_role_name", value=f"{local_settings['check_role_name']}", inline=False)
        await ctx.channel.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def division_name(self, ctx, division_name):
        settings.set_division_name(ctx.guild.id, division_name)
        await ctx.channel.send(f"Division Name set to: {division_name.upper()}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def roster_channel_id(self, ctx, channel_id):
        settings.set_roster_channel_id(ctx.guild.id, channel_id)
        await ctx.channel.send(f"Roster Channel ID set to: {channel_id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def co_comms_channel_id(self, ctx, channel_id):
        settings.set_co_comms_channel_id(ctx.guild.id, channel_id)
        await ctx.channel.send(f"CO Comms Channel ID set to: {channel_id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def log_channel_id(self, ctx, channel_id):
        settings.set_bot_log_channel_id(ctx.guild.id, channel_id)
        await ctx.channel.send(f"Bot Log Channel ID set to: {channel_id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def command_channel_id(self, ctx, channel_id):
        settings.set_bot_command_channel_id(ctx.guild.id, channel_id)
        await ctx.channel.send(f"Bot Command Channel ID set to: {channel_id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def command_prefix(self, ctx, prefix):
        settings.set_bot_prefix(ctx.guild.id, prefix)
        await ctx.channel.send(f"Bot Prefix set to: {prefix}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def co_role_name(self, ctx, role):
        settings.set_co_role_name(ctx.guild.id, role)
        await ctx.channel.send(f"CO Role Name set to: {role}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def roster_manager_role_name(self, ctx, role):
        settings.set_roster_manager_role_name(ctx.guild.id, role)
        await ctx.channel.send(f"Roster Manager Role Name set to: {role}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enlisted_role_name(self, ctx, role):
        settings.set_enlisted_role_name(ctx.guild.id, role)
        await ctx.channel.send(f"Enlisted Role Name set to: {role}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def loa_role_name(self, ctx, role):
        settings.set_loa_role_name(ctx.guild.id, role)
        await ctx.channel.send(f"LOA Role Name set to: {role}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def check_role_name(self, ctx, role):
        settings.set_check_role_name(ctx.guild.id, role)
        await ctx.channel.send(f"Check Role Name set to: {role}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def syncdatabase(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        desired_role = get(ctx.guild.roles, name=local_settings["enlisted_role_name"])
        loa_role = get(ctx.guild.roles, name=local_settings["loa_role_name"])
        check_role = get(ctx.guild.roles, name=local_settings["check_role_name"])

        if roster_sheet.get_division_gid(local_settings["division_name"]) == None:
            roster_sheet.add_division_sheet(local_settings["division_name"])
        for member in ctx.guild.members:
            if desired_role in member.roles and roster_sheet.find_in_roster_user_id(local_settings["division_name"], member.id) == None:
                is_loa = loa_role in member.roles
                check_completed = check_role in member.roles
                unit = singleunit.SingleUnit(member.display_name, None, member.id, check_completed, is_loa)
                roster_sheet.push_to_roster(local_settings["division_name"], unit)
        roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])


def setup(bot):
    bot.add_cog(SettingsManagement(bot))