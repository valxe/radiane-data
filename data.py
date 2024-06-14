import os
import json
import asyncio
import threading
from typing import Any, Dict

data_dir = os.path.join('data')
users_dir = os.path.join(data_dir, 'users')
top_path = os.path.join(data_dir, 'top.json')
total_path = os.path.join(data_dir, 'total.json')

os.makedirs(users_dir, exist_ok=True)

class DataCache:
    def __init__(self) -> None:
        self.user_data: Dict[str, Dict[str, Any]] = {}
        self.top_users: Dict[str, int] = self.load_top_users()
        self.total_messages: int = self.load_total_messages()
        self.lock = threading.Lock()

    def load_total_messages(self) -> int:
        if os.path.exists(total_path):
            with open(total_path, 'r') as file:
                return json.load(file).get('count', 0)
        return 0

    def load_top_users(self) -> Dict[str, int]:
        if os.path.exists(top_path):
            with open(top_path, 'r') as file:
                return json.load(file)
        return {}

    def save_user_message(self, user_name: str, message: Any) -> None:
        user_file = os.path.join(users_dir, f'{user_name}.json')
        current_pfp = str(message.author.avatar.url) if message.author.avatar else None

        if user_name not in self.user_data:
            if os.path.exists(user_file):
                with open(user_file, 'r') as file:
                    existing_data = json.load(file)
            else:
                existing_data = {
                    "user_pfp": current_pfp,
                    "messages": []
                }

            self.user_data[user_name] = existing_data

        if current_pfp and self.user_data[user_name].get("user_pfp") != current_pfp:
            self.user_data[user_name]["user_pfp"] = current_pfp

        user_message = {
            'message_time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': message.content
        }
        self.user_data[user_name]["messages"].append(user_message)
        
        self.update_top(user_name)
        self.total_messages += 1

    def update_top(self, user_name: str) -> None:
        self.top_users[user_name] = self.top_users.get(user_name, 0) + 1
        self.top_users = dict(sorted(self.top_users.items(), key=lambda item: item[1], reverse=True))

    def save_to_disk(self) -> None:
        with self.lock:
            user_data_copy = self.user_data.copy()
            top_users_copy = self.top_users.copy()

            for user_name, data in user_data_copy.items():
                user_file = os.path.join(users_dir, f'{user_name}.json')
                with open(user_file, 'w') as file:
                    json.dump(data, file, indent=4)

            with open(top_path, 'w') as file:
                json.dump(top_users_copy, file, indent=4)

            with open(total_path, 'w') as file:
                json.dump({'count': self.total_messages}, file, indent=4)

            self.clear_cache()

    def clear_cache(self) -> None:
        self.user_data = {}
        self.top_users = self.load_top_users()
        self.total_messages = self.load_total_messages()

async def periodic_save(data_cache: DataCache) -> None:
    while True:
        await asyncio.sleep(20)
        threading.Thread(target=data_cache.save_to_disk).start()