import discord
from rosterbot.utils.ranks import Rank
from discord.utils import get

class GeneralHelpers:
    @staticmethod    
    async def delete_bot_messages(channel):
        def is_not_hook(msg):
            return msg.author.id != 655213421163184171
        deleted = await channel.purge(limit=100, check=is_not_hook)
        return deleted

    @staticmethod
    def has_role(member, role):
        return role in member.roles
    
    @staticmethod
    def has_gotten_role(before, after, role):
        if not role in before.roles and role in after.roles:
            return True
        return False
    
    @staticmethod
    def has_lost_role(before, after, role):
        if role in before.roles and not role in after.roles:
            return True
        return False
    
    @staticmethod
    def get_embed_field(message, desired_field):
        if (len(message.embeds) > 0):
            embed_fields = message.embeds[0].fields
            return [field for field in embed_fields if field.name.upper() == desired_field.upper()]
        return None

    @staticmethod
    def generate_request_body(unit_property):
        body = {
            "majorDimension": "ROWS",
            "values": [[unit_property]]
        }
        return body

    @staticmethod
    def find_nth_substring(string, key, occurence):
        index = string.find(key)
        while index >= 0 and occurence > 1:
            index = string.find(key, index+len(key))
            occurence -= 1
        return index

    @staticmethod
    def split_str_at_index(string, begin, end):
        part1 = string[begin:end]
        part2 = string[end:len(string)]
        if part2 != '':
            return [string[begin:end], string[end:len(string)]]
        return string.split()

# FLAWED: If '\n' is not the last character, the method will end one character off.
    @staticmethod
    def partition_str(string, key, size):
        last_string_split_index = 0
        occurence = 0
        string_split = []
        while last_string_split_index >= 0: 
            current_string_split_index = GeneralHelpers.find_nth_substring(string, "\n", size*occurence+size)
            desired_substring = string[last_string_split_index:current_string_split_index]
            if desired_substring != "":
                string_split.append(string[last_string_split_index:current_string_split_index])
            occurence += 1
            last_string_split_index = current_string_split_index
        return string_split

    @staticmethod
    def build_roster_string(units):
        string = ""
        for unit in units:
            string += f"{unit.name} ({unit.steam_id})\n"
        return string

    @staticmethod
    def partition_list(list, size):
        return [list[i * size:(i + 1) * size] for i in range((len(list) + size - 1) // size)]

    @staticmethod
    async def display_roster(bot, settings, channel, roster, check_active, bot_prefix):
        current_guild = bot.get_guild(settings["server_id"])
        enlisted_role = get(current_guild.roles, name=settings["enlisted_role_name"])
        nco_role = get(current_guild.roles, name=settings["nco_role_name"])
        co_role = get(current_guild.roles, name=settings["co_role_name"])

        relevant_members = {member.id: member for member in current_guild.members if enlisted_role in member.roles}
        
        co_units = [unit for unit in roster if co_role in relevant_members[unit.user_id].roles and unit.loa.upper() == "FALSE"]
        nco_units = [unit for unit in roster if nco_role in relevant_members[unit.user_id].roles and co_role not in relevant_members[unit.user_id].roles and unit.loa.upper() == "FALSE"]
        enlisted_units = [unit for unit in roster if enlisted_role in relevant_members[unit.user_id].roles and not all(x in [nco_role, co_role] for x in relevant_members[unit.user_id].roles) and unit.loa.upper() == "FALSE"]
        loa_units = [unit for unit in roster if unit.loa.upper() == "TRUE"]
        checked_units = [unit for unit in roster if unit.activity_check.upper() == "TRUE"]

        size = 20
        co_unit_chunks = GeneralHelpers.partition_list(co_units, size)
        nco_unit_chunks = GeneralHelpers.partition_list(nco_units, size)
        enlisted_unit_chunks = GeneralHelpers.partition_list(enlisted_units, size)
        loa_unit_chunks = GeneralHelpers.partition_list(loa_units, size)
        checked_unit_chunks = GeneralHelpers.partition_list(checked_units, size)

        if check_active == 'TRUE':
            description = (
                f"There are currently {len(roster)} units.\n"
                f"{len(roster)-len(loa_units)} are active.\n"
                f"{len(loa_units)} are on LOA.\n"
                f"{len(checked_units)} have completed the activity check."
            )
        else:
            description = (
                f"There are currently {len(roster)} units.\n"
                f"{len(roster)-len(loa_units)} are active.\n"
                f"{len(loa_units)} are on LOA.\n"
            )

        embed = discord.Embed(
            title = 'Roster - Updates Automatically',
            description = description,
            color = 0x04C0FC
        )

        embed.set_thumbnail(url='https://cdn.discordapp.com/icons/437778436333895680/204cb99c599888186f402fbcbf1ea575.webp?size=128')
        for i in range(len(co_unit_chunks)):
            embed.add_field(name=f"Active Commissioned Officers - {len(co_units)} Units", value=GeneralHelpers.build_roster_string(co_unit_chunks[i]), inline=False)
        for i in range(len(nco_unit_chunks)):
            embed.add_field(name=f"Active Non-Commissioned Officers - {len(nco_units)} Units", value=GeneralHelpers.build_roster_string(nco_unit_chunks[i]), inline=False)
        for i in range(len(enlisted_unit_chunks)):
            embed.add_field(name=f"Active Enlisted - {len(enlisted_unit_chunks[i])}/{len(enlisted_units)} Units (Section {i+1})", value=GeneralHelpers.build_roster_string(enlisted_unit_chunks[i]), inline=False)
        for i in range(len(loa_unit_chunks)):
            embed.add_field(name=f"Units on LOA - {len(loa_units)} Units", value=GeneralHelpers.build_roster_string(loa_unit_chunks[i]), inline=False)
        if check_active == 'TRUE':
            for i in range(len(checked_unit_chunks)):
                embed.add_field(name=f"Units with Activity Check Completed - {len(checked_units)} Units", value=GeneralHelpers.build_roster_string(checked_unit_chunks[i]), inline=False)
        embed.add_field(name="Is the roster outdated?", value=f"You can refresh the roster with PREFIXrefreshroster command.\nYou can set a unit's SteamID with: PREFIXsetsteamid <DIGITS> <STEAMID>")
        await channel.purge()
        await channel.send(embed=embed)