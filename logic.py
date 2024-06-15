import json
import os
import sqlite3
from typing import List

data_dir = os.path.join('data')
secret_path = os.path.join(data_dir, 'secret.json')
blacklist_path = os.path.join(data_dir, 'blacklist.json')
db_path = os.path.join(data_dir, 'database.db')

def load_token() -> str:
    with open(secret_path, 'r') as file:
        return json.load(file).get('bot_token')

def load_blacklist() -> List[str]:
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as file:
            return json.load(file)
    return []

def count_users() -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def read_total() -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM total_messages WHERE id = 1")
        result = cursor.fetchone()
        return result[0] if result else 0