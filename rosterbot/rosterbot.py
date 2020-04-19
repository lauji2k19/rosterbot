import discord
import asyncio
import logging
from os import listdir
from os.path import isfile, join, splitext
from discord.ext import tasks, commands
from rosterbot.services.rostersheetservice import RosterSheetService
from rosterbot.services.mariasettingsservice import MariaSettingsService
from rosterbot.utils.generalhelpers import GeneralHelpers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

roster_sheet = RosterSheetService()
settings = MariaSettingsService()

async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        prefix = settings.get_server_settings(guild.id)["bot_prefix"]
        if prefix != None:
            return prefix
        else:
            return "_"
    else:
        return "_"

bot = commands.Bot(
    command_prefix = determine_prefix,
    activity=discord.Game(name=f"Beep",
    max_messages=10000)
)

cogs = [splitext(cog)[0] for cog in listdir("./rosterbot/cogs") if isfile(join("./rosterbot/cogs", cog))]
for cog in cogs:
    if cog != "__init__":
        bot.load_extension(f"rosterbot.cogs.{cog}")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')