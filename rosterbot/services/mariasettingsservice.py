import asyncio
import pymysql
import os
from rosterbot.constants import MARIA_DB_USER, MARIA_DB_PASSWORD

class MariaSettingsService:
    def __init__(self):
        self.db = pymysql.connect(host="localhost", user=MARIA_DB_USER, passwd=MARIA_DB_PASSWORD, db="server_settings", autocommit=True)
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
        
    def query(self, query):
        self.db.ping(reconnect=True)
        self.cursor.execute(query)
    
    def get_version(self):
        self.query("SELECT VERSION()")
        return self.cursor.fetchone()

    def add_server(self, server_id):
        self.query(f"INSERT IGNORE INTO settings(server_id) VALUES ({server_id})")

    def get_all_servers(self):
        self.query(f"SELECT * FROM settings")
        return self.cursor.fetchall()

    def get_server_settings(self, server_id):
        self.add_server(server_id)
        self.query(f"SELECT * FROM settings WHERE server_id={server_id}")
        return self.cursor.fetchone()
    
    def get_server_settings_by_division(self, division_name):
        self.query(f"SELECT * FROM settings WHERE division_name='{division_name.upper()}'")
        return self.cursor.fetchone()

    def set_division_name(self, server_id, division_name):
        self.query(f"UPDATE settings SET division_name='{division_name.upper()}' WHERE server_id={server_id}")

    def set_roster_channel_id(self, server_id, channel_id):
        self.query(f"UPDATE settings SET roster_channel_id={channel_id} WHERE server_id={server_id}")
    
    def set_co_comms_channel_id(self, server_id, channel_id):
        self.query(f"UPDATE settings SET co_comms_channel_id={channel_id} WHERE server_id={server_id}")

    def set_bot_log_channel_id(self, server_id, channel_id):
        self.query(f"UPDATE settings SET bot_log_channel_id={channel_id} WHERE server_id={server_id}")

    def set_bot_command_channel_id(self, server_id, channel_id):
        self.query(f"UPDATE settings SET bot_command_channel_id={channel_id} WHERE server_id={server_id}")

    def set_bot_prefix(self, server_id, prefix):
        self.query(f"UPDATE settings SET bot_prefix='{prefix}' WHERE server_id={server_id}")

    def set_co_role_name(self, server_id, role):
        self.query(f"UPDATE settings SET co_role_name='{role}' WHERE server_id={server_id}")
    
    def set_roster_manager_role_name(self, server_id, role):
        self.query(f"UPDATE settings SET roster_manager_role_name='{role}' WHERE server_id={server_id}")
    
    def set_enlisted_role_name(self, server_id, role):
        self.query(f"UPDATE settings SET enlisted_role_name='{role}' WHERE server_id={server_id}")

    def set_loa_role_name(self, server_id, role):
        self.query(f"UPDATE settings SET loa_role_name='{role}' WHERE server_id={server_id}")

    def set_check_role_name(self, server_id, role):
        self.query(f"UPDATE settings SET check_role_name='{role}' WHERE server_id={server_id}")

    def close_connection(self):
        self.db.close()