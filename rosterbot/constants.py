import os

BOT_TOKEN = os.environ.get('ROSTER_BOT_TOKEN')
DEVELOPER_USER_ID = int(os.environ.get('DEVELOPER_USER_ID'))

MASTER_GUILD_ID = int(os.environ.get('MASTER_GUILD_ID'))
MASTER_BOT_LOG_ID = int(os.environ.get('MASTER_BOT_LOG_ID'))

ROSTER_SPREADSHEET_ID = os.environ.get('ROSTERBOT_SPREADSHEET_ID')
MARIA_DB_USER = os.environ.get('MARIA_DB_USER')
MARIA_DB_PASSWORD = os.environ.get('MARIA_DB_PASSWORD')