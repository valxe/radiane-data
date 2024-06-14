import json
import os
from typing import List

data_dir = os.path.join('data')
secret_path = os.path.join(data_dir, 'secret.json')
blacklist_path = os.path.join(data_dir, 'blacklist.json')
users_dir = os.path.join(data_dir, 'users')
total_path = os.path.join(data_dir, 'total.json')

def load_token() -> str:
    with open(secret_path, 'r') as file:
        return json.load(file).get('bot_token')

def load_blacklist() -> List[str]:
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as file:
            return json.load(file)
    return []

def count_users() -> int:
    return sum(len(files) for _, _, files in os.walk(users_dir))

def read_total() -> int:
    if os.path.exists(total_path):
        with open(total_path, 'r') as file:
            return json.load(file).get('count', 0)
    return 0