from rosterbot.rosterbot import settings

class MariaSettingsService:
    def __init__(self):
        self.db = pymysql.connect(host="localhost", user=MARIA_DB_USER, passwd=MARIA_DB_PASSWORD, db="economy", autocommit=True)
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def query(self, query):
        self.db.ping(reconnect=True)
        self.cursor.execute(query)

    def retrieve_server_settings(self, guild_id):
        server_settings = settings.get_server_settings(guild_id)
        if (server_settings is None):
            raise ValueError("This server has no settings.")
        return server_settings

    def add_user(self, user_id):
        try:
            server_settings = self.retrieve_server_settings(guild_id)
            self.query(f"INSERT INTO {server_settings['economy_table']}(user_id) VALUES ({user_id})")
        except MySQLError:
            self.db.rollback()

    def get_user(self, user_id):
        self.add_user(user_id)
        self.query(f"SELECT * FROM users WHERE user_id={user_id} LIMIT 1")
        return self.cursor.fetchone()

    def add_credits(self, guild_id, user_id, credits):
        try:
            server_settings = retrieve_server_settings(self, guild_id)
            if (self.get_user(user_id) is not None):
                self.query(f"UPDATE users SET credits = credits + {credits} WHERE user_id={user_id}")
        except MySQLError:
            self.db.rollback()