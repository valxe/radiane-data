import os
import sqlite3
import asyncio
import json
import threading
from typing import Any, Dict

data_dir = os.path.join('data')
db_path = os.path.join(data_dir, 'database.db')
os.makedirs(data_dir, exist_ok=True)

class DataCache:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.connection = self.connect_db()
        self.init_db()

    def connect_db(self):
        return sqlite3.connect(db_path, check_same_thread=False)

    def init_db(self) -> None:
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_name TEXT PRIMARY KEY,
                    user_pfp TEXT,
                    messages TEXT
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS top_users (
                    user_name TEXT PRIMARY KEY,
                    message_count INTEGER
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS total_messages (
                    id INTEGER PRIMARY KEY,
                    count INTEGER
                )
            ''')
            if not self.connection.execute('SELECT count(*) FROM total_messages').fetchone()[0]:
                self.connection.execute('INSERT INTO total_messages (count) VALUES (0)')

    def load_total_messages(self) -> int:
        with self.connection:
            return self.connection.execute('SELECT count FROM total_messages WHERE id=1').fetchone()[0]

    def load_top_users(self) -> Dict[str, int]:
        with self.connection:
            result = self.connection.execute('SELECT user_name, message_count FROM top_users').fetchall()
            return {row[0]: row[1] for row in result}

    def save_user_message(self, user_name: str, message: Any) -> None:
        user_message = {
            'message_time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': message.content
        }
        current_pfp = str(message.author.avatar.url) if message.author.avatar else None

        with self.lock, self.connection:
            existing_data = self.connection.execute('SELECT user_pfp, messages FROM users WHERE user_name = ?', (user_name,)).fetchone()
            if existing_data:
                user_pfp, messages = existing_data
                messages = json.loads(messages)
                if current_pfp and user_pfp != current_pfp:
                    user_pfp = current_pfp
                messages.append(user_message)
            else:
                user_pfp = current_pfp
                messages = [user_message]

            self.connection.execute('''
                INSERT OR REPLACE INTO users (user_name, user_pfp, messages)
                VALUES (?, ?, ?)
            ''', (user_name, user_pfp, json.dumps(messages)))

            self.update_top(user_name)
            self.connection.execute('UPDATE total_messages SET count = count + 1 WHERE id = 1')

    def update_top(self, user_name: str) -> None:
        with self.connection:
            existing_count = self.connection.execute('SELECT message_count FROM top_users WHERE user_name = ?', (user_name,)).fetchone()
            if existing_count:
                self.connection.execute('UPDATE top_users SET message_count = message_count + 1 WHERE user_name = ?', (user_name,))
            else:
                self.connection.execute('INSERT INTO top_users (user_name, message_count) VALUES (?, 1)', (user_name,))
            self.top_users = self.load_top_users()

    def save_to_disk(self) -> None:
        with self.lock:
            pass

    def clear_cache(self) -> None:
        pass

async def periodic_save(data_cache: DataCache) -> None:
    while True:
        await asyncio.sleep(20)
        threading.Thread(target=data_cache.save_to_disk).start()