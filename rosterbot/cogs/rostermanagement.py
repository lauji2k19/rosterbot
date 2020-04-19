import discord
import asyncio
from discord.ext import commands
from discord.utils import get
from rosterbot.rosterbot import roster_sheet, logger, settings
from rosterbot.constants import DEVELOPER_USER_ID, MASTER_GUILD_ID, MASTER_BOT_LOG_ID
from rosterbot.models import singleunit
from rosterbot.utils.generalhelpers import GeneralHelpers
from rosterbot.utils.ranks import Rank

class RosterManagement(commands.Cog, name='Roster Management'):
    """Commands related to the roster."""
    
    def __init__(self, bot):
        self.bot = bot

    async def has_privilege(self, ctx, role):
        desired_role = get(ctx.guild.roles, name=role)
        if desired_role in ctx.message.author.roles:
            return True
        else:
            await ctx.channel.send(f"The {role} role is needed to run this command.")
            return False

    @commands.command(help="Display the number of units currently in the division.")
    async def unitcount(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        channel = ctx.message.channel
        roster = roster_sheet.read_roster(local_settings["division_name"])
        await channel.send(f"There are currently {len(roster)} units.") 

    @commands.command(help="Refresh the roster.")
    async def refreshroster(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        valid_privilege = await self.has_privilege(ctx, local_settings['co_role_name'])
        if valid_privilege:
            channel = ctx.message.channel
            if channel.id == local_settings['roster_channel_id']:
                roster = roster_sheet.read_roster(local_settings["division_name"])
                await GeneralHelpers.display_roster(channel, roster, roster_sheet.get_check_active(local_settings["division_name"]), local_settings['bot_prefix'])
            else:
                await channel.send(f"This command can only be run in <#{local_settings['roster_channel_id']}>.")

    @commands.command(help="Set a unit's SteamID.")
    async def setsteamid(self, ctx, digits, steam_id):
        local_settings = settings.get_server_settings(ctx.guild.id)
        valid_privilege = await self.has_privilege(ctx, local_settings['co_role_name'])
        if valid_privilege:
            response = roster_sheet.set_unit_steamid(local_settings["division_name"], digits, steam_id)
            await ctx.channel.send(response)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])

    # @commands.command(help="Restore the roster to its latest backup (backups occur every 24 hours).")
    # @commands.has_permissions(manage_roles=True)
    # async def restoreroster(self, ctx):
    #     ballista_role = get(ctx.guild.roles, name='MPF BALLISTA')
    #     nco_role = get(ctx.guild.roles, name='NCO')
    #     co_role = get(ctx.guild.roles, name='MPF BALLISTA CO')
    #     saved_units = roster_sheet.read_roster_backup()
    #     for unit in saved_units:
    #         try:
    #             member = ctx.guild.get_member(int(unit.user_id))
    #             if not ballista_role in member.roles:
    #                 await member.remove_roles(*[role for role in member.roles if not 'everyone' in role.name])
    #                 await member.add_roles(ballista_role)
    #                 if unit.rank.value >= Rank.THREE.value and unit.rank.value < Rank.TOFC.value:
    #                     await member.add_roles(nco_role)
    #                 if unit.rank.value >= Rank.TOFC.value:
    #                     await member.add_roles(co_role)
    #         except AttributeError as ex:
    #             logger.exception(ex)
    #             continue
    #     await ctx.channel.send("The roster has been restored.")
    #     await self.bot.get_user(DEVELOPER_USER_ID).send(f"{ctx.message.author.display_name} ran {BOT_PREFIX}restoreroster")

    @commands.command(help="Sort the roster.")
    async def sortroster(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        valid_privilege = await self.has_privilege(ctx, local_settings['co_role_name'])
        if valid_privilege:
            response = roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
            await ctx.channel.send("The roster spreadsheet has been sorted.")

    @commands.command(help="Find a particular unit by digits.")
    async def find(self, ctx, digits):
        channel = ctx.message.channel
        unit = roster_sheet.find_in_roster(digits)
        if unit != None:
            await channel.send(f'```Name: {unit.name}\n'
                                    f'SteamID: {unit.steam_id}\n'
                                    f'LOA: {unit.loa}\n' 
                                    f'Long LOA: {unit.long_loa}\n' 
                                    f'Activity Check: {unit.activity_check}```')
        else:
            await channel.send(f'```Could not find unit.```')

    @commands.command(help="List all units on LOA. Units marked with '***' have been on LOA for an extensive amount of time.")
    async def listloa(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        channel = ctx.message.channel
        units = roster_sheet.list_loa(local_settings["division_name"])
        
        if (len(units) == 1):
            botMsg = 'There is 1 unit on LOA. ```'
        else:
            botMsg = f'There are {len(units)} units on LOA. ```'

        if units != []:
            for unit in units:
                if (unit.long_loa == 'TRUE'):
                    botMsg += f'{unit.name}**\n'
                else:
                    botMsg += f'{unit.name}\n'
            botMsg += '```'
            await channel.send(botMsg)
        else:
            await channel.send(f'```No units are on LOA.```')

    @commands.command(help="Start an activity check.")
    async def startcheck(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        valid_privilege = await self.has_privilege(ctx, local_settings["co_role_name"])
        if valid_privilege:
            roster_sheet.set_check_active(local_settings["division_name"], True)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
            await ctx.channel.send("You started an activity check.")

    @commands.command(help="Stop an activity check.")
    async def stopcheck(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        valid_privilege = await self.has_privilege(ctx, local_settings["co_role_name"])
        if valid_privilege:
            roster_sheet.set_check_active(local_settings["division_name"], False)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
            await ctx.channel.send("You stopped an activity check.")

    @commands.command(help="List all units who have not yet completed either an activity check or LOA request.")
    async def listincompletechecks(self, ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        enlisted_role = get(ctx.guild.roles, name=local_settings['enlisted_role_name'])
        co_role = get(ctx.guild.roles, name=local_settings['co_role_name'])
        loa_role = get(ctx.guild.roles, name=local_settings['loa_role_name'])
        check_role = get(ctx.guild.roles, name=local_settings['check_role_name'])
        incompleted_units = [f"{member.display_name}\n" for member in ctx.guild.members if enlisted_role in member.roles and check_role not in member.roles and loa_role not in member.roles and co_role not in member.roles]
        if (len(incompleted_units) > 0):
            msg = "```" + ''.join(incompleted_units) + "```"
        else:
            msg = "All units have completed the activity check."
        await ctx.channel.send(msg)

    # @commands.command(help="Remove all units who have not yet completed either an activity check or LOA request. You will be DMed with a confirmation prompt and list of users to be removed.")
    # @commands.has_role('MPF BALLISTA CO')
    # async def removeinactiveunits(self, ctx):
    #     runner = ctx.message.author
    #     ballista_role = get(ctx.guild.roles, name='MPF BALLISTA')
    #     advisor_role = get(ctx.guild.roles, name='Advisor')
    #     co_role = get(ctx.guild.roles, name='MPF BALLISTA CO')
    #     loa_role = get(ctx.guild.roles, name='LOA')
    #     check_role = get(ctx.guild.roles, name='Check Completed')
    #     incompleted_units = [member for member in ctx.guild.members if ballista_role in member.roles and check_role not in member.roles and loa_role not in member.roles and co_role not in member.roles and advisor_role not in member.roles]
    #     bot_msg = await self.bot.get_channel(BOT_COMMAND_CHANNEL_ID).send(f"<@{runner.id}>\n Check your DMs for the removal prompt.")
    #     if (len(incompleted_units) > 0):
    #         msg = "```" + ''.join(f"\n{member.display_name}" for member in incompleted_units) + "\n--> UNION (failed the activity check)```"
    #     else:
    #         msg = "All units have completed the activity check.\n"

    #     initial_prompt = await runner.send("The following have not completed the activity check: " + msg +
    #                                     "React \u2705 to remove automatically or \u274C to abort.")
    #     reaction = await InputHelpers.get_user_reaction_private(self.bot, runner, initial_prompt, 60, ['\u2705', '\u274C'])

    #     if reaction.emoji == '\u2705':
    #         incompleted_unit_ids = [unit.id for unit in incompleted_units]
    #         roster_sheet.remove_from_roster(incompleted_unit_ids)
    #         for unit in incompleted_units:
    #             await unit.remove_roles(*[role for role in unit.roles if not "everyone" in role.name])
    #             await unit.add_roles(get(ctx.guild.roles, name='Guest'))
    #             await unit.send("You were removed from BALLISTA for failing to complete the activity check. To appeal, DM a CO with a good justification or evidence that you were active.")
    #         await runner.send(f"All units from the above list were removed. If a mistake was made, run {BOT_PREFIX}restoreroster to restore the last saved roster. Also, remember to post the log above into <#{CVR_SUBDIVISION_CHANNEL_ID}> in the Combine Discord.")
    #     else:
    #         await runner.send("You chose to abort. You may remove units manually.")
    #     await ctx.message.delete()
    #     await bot_msg.delete()
    #     await self.bot.get_user(DEVELOPER_USER_ID).send(f"{ctx.message.author.display_name} ran {BOT_PREFIX}removeinactiveunits")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        local_settings = settings.get_server_settings(before.guild.id)
        enlisted_role = get(before.guild.roles, name=local_settings["enlisted_role_name"])

        if GeneralHelpers.has_gotten_role(before, after, enlisted_role):
            unit = singleunit.SingleUnit(after.display_name, None, after.id)
            push_result = roster_sheet.push_to_roster(local_settings["division_name"], unit)
            if 'FAILED' in push_result.upper():
                await self.bot.get_channel(local_settings["bot_command_channel_id"]).send(f"<@{after.id}>\n" + push_result)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
        
        if GeneralHelpers.has_lost_role(before, after, enlisted_role):
            roster_sheet.remove_from_roster(local_settings["division_name"], after.id)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
        
        if GeneralHelpers.has_role(after, enlisted_role) and before.display_name != after.display_name:
            push_result = roster_sheet.set_unit_name(local_settings["division_name"], before.display_name.split()[-1], after.display_name, after.id)
            if 'FAILED' in push_result.upper() or 'COULD NOT BE FOUND' in push_result.upper():
                await self.bot.get_channel(local_settings["bot_command_channel_id"]).send(f"<@{after.id}>\n" + push_result)
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])

        if GeneralHelpers.has_role(after, enlisted_role):            
            loa_role = get(before.guild.roles, name=local_settings["loa_role_name"])
            check_role = get(before.guild.roles, name=local_settings["check_role_name"])

            if GeneralHelpers.has_gotten_role(before, after, loa_role):
                response = roster_sheet.manual_loa_status(local_settings["division_name"], after.id, True)
                roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
                await self.bot.get_channel(local_settings["bot_log_channel_id"]).send(f"{after.display_name} is now on LOA.")
        
            if GeneralHelpers.has_lost_role(before, after, loa_role):
                response = roster_sheet.manual_loa_status(local_settings["division_name"], after.id, False)
                roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
                await self.bot.get_channel(local_settings["bot_log_channel_id"]).send(f"{after.display_name} is off LOA.")

            if GeneralHelpers.has_gotten_role(before, after, check_role):
                response = roster_sheet.set_activity_check(local_settings["division_name"], after.id, True)
                await self.bot.get_channel(local_settings["bot_log_channel_id"]).send(f"{after.display_name} has completed the activity check.")
                roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])

            if GeneralHelpers.has_lost_role(before, after, check_role):
                response = roster_sheet.set_activity_check(local_settings["division_name"], after.id, False)
                roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        local_settings = settings.get_server_settings(member.guild.id)
        enlisted_role = get(member.guild.roles, name=local_settings["enlisted_role_name"])
        co_role = get(member.guild.roles, name=local_settings["co_role_name"])

        if enlisted_role in member.roles:
            removed_unit = roster_sheet.remove_from_roster(local_settings["division_name"], member.id)[0]
            roster_sheet.sort_roster_spreadsheet(local_settings["division_name"])
            await self.bot.get_channel(CO_COMMS_CHANNEL_ID).send(f"{co_role.mention}\n{member.display_name} ({removed_unit.steam_id}) left the Discord with the MPF BALLISTA role.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id == MASTER_GUILD_ID and message.channel.id == MASTER_BOT_LOG_ID and message.author.bot and "ROSTER CHANGE" in message.content.upper():
            division_name = message.content.split(":")[0]
            await message.delete()
            division_settings = settings.get_server_settings_by_division(division_name)
            roster_channel = self.bot.get_channel(division_settings['roster_channel_id'])
            roster = roster_sheet.read_roster(division_name)
            await GeneralHelpers.display_roster(roster_channel, roster, roster_sheet.get_check_active(division_name), self.bot.command_prefix)

def setup(bot):
    bot.add_cog(RosterManagement(bot))