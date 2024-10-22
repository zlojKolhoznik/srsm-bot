import sqlite3
from aiogram.types import User


class BotDB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.conn = None
        self.cur = None

    def insert_user(self, user: User):
        self.cur.execute("INSERT INTO personal_data (telegram_id, first_name, last_name) VALUES (?, ?, ?)",
                         (user.id, user.first_name, user.last_name))
        self.conn.commit()

    def set_accommodation(self, user: User, dormitory: int, room_number: str | None = None):
        self.cur.execute("UPDATE personal_data SET dormitory_number=? WHERE telegram_id=?", (dormitory, user.id))
        if room_number is not None:
            self.cur.execute("UPDATE personal_data SET room_number=? WHERE telegram_id=?", (room_number, user.id))
        self.conn.commit()

    def get_user_info(self, telegram_id: int):
        self.cur.execute("SELECT * FROM personal_data WHERE telegram_id=?", (telegram_id,))
        data = self.cur.fetchone()
        return {
            "id": data[0],
            "first_name": data[1],
            "last_name": data[2],
            "dormitory": data[3],
            "room_number": data[4]
        }

    def user_exists(self, telegram_id: int):
        self.cur.execute("SELECT * FROM personal_data WHERE telegram_id=?", (telegram_id,))
        data = self.cur.fetchone()
        return data is not None
    

    def get_users_subscribed_for(self, punkt_id: str):
        self.cur.execute("SELECT UNIQUE user_id FROM user_punkt WHERE gurt=?", (punkt_id,))
        return [row[0] for row in self.cur.fetchall()]
    

    def get_active_punkts(self):
        self.cur.execute("SELECT * FROM punkty WHERE is_active=1")
        return self.cur.fetchall()
    

    def get_inactive_punkts(self):
        self.cur.execute("SELECT * FROM punkty WHERE is_active=0")
        return self.cur.fetchall()
    

    def get_all_punkts(self):
        self.cur.execute("SELECT * FROM punkty")
        return self.cur.fetchall()
    

    def activate_punkt(self, punkt_id: str):
        self.cur.execute("UPDATE punkty SET is_active=1 WHERE punkt_id=?", (punkt_id,))
        self.conn.commit()


    def deactivate_punkt(self, punkt_id: str):
        self.cur.execute("UPDATE punkty SET is_active=0 WHERE punkt_id=?", (punkt_id,))
        self.conn.commit()


    def is_user_subscribed_for_punkt(self, user_id: int, punkt_id: str):
        self.cur.execute("SELECT * FROM user_punkt WHERE user_id=? AND punkt_id=?", (user_id, punkt_id))
        return self.cur.fetchone() is not None
    

    def subscribe_user_to_punkt(self, user_id: int, punkt_id: str):
        if self.is_user_subscribed_for_punkt(user_id, punkt_id):
            return
        self.cur.execute("INSERT INTO user_punkt (user_id, punkt_id) VALUES (?, ?)", (user_id, punkt_id))
        self.conn.commit()
    

    def unsubscribe_user_from_punkt(self, user_id: int, punkt_id: str):
        self.cur.execute("DELETE FROM user_punkt WHERE user_id=? AND punkt_id=?", (user_id, punkt_id))
        self.conn.commit()
