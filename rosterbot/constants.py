import os
import json

with open('./config.json') as f:
    env_vars = json.loads(f.read())

BOT_TOKEN = env_vars['botToken']
DEVELOPER_USER_ID = env_vars['developerUserId']

MASTER_GUILD_ID = env_vars['masterGuildId']
MASTER_BOT_LOG_ID = env_vars['developerUserId']

ROSTER_SPREADSHEET_ID = env_vars['rosterSpreadsheetId']
MARIA_DB_USER = env_vars['mariaDbUser']
MARIA_DB_PASSWORD = env_vars['mariaDbPassword']