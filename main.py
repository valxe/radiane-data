import discord
import time
import asyncio
import json
import os
import logging
import threading
from commands.top import send_top
from commands.total import send_total
from commands.blacklist import send_blacklist, add_to_blacklist, remove_from_blacklist
from commands.user_info import get_user_info
from commands.help import send_help_embed
from commands.remove import remove_user
from commands.random import send_random_user_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

secret_path = os.path.join('data', 'secret.json')
blacklist_path = os.path.join('data', 'blacklist.json')
users_dir = os.path.join('data', 'users')
top_path = os.path.join('data', 'top.json')
total_path = os.path.join('data', 'total.json')

os.makedirs(users_dir, exist_ok=True)

def load_token():
    with open(secret_path, 'r') as file:
        return json.load(file).get('bot_token')

def load_blacklist():
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as file:
            return json.load(file)
    return []

def count_users():
    return sum(len(files) for _, _, files in os.walk(users_dir))

class DataCache:
    def __init__(self):
        self.user_data = {}
        self.top_users = self.load_top_users()
        self.total_messages = self.load_total_messages()
        self.lock = threading.Lock()

    def load_total_messages(self):
        if os.path.exists(total_path):
            with open(total_path, 'r') as file:
                return json.load(file).get('count', 0)
        return 0

    def load_top_users(self):
        if os.path.exists(top_path):
            with open(top_path, 'r') as file:
                return json.load(file)
        return {}

    def save_user_message(self, user_name, message):
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

    def update_top(self, user_name):
        self.top_users[user_name] = self.top_users.get(user_name, 0) + 1
        self.top_users = dict(sorted(self.top_users.items(), key=lambda item: item[1], reverse=True))

    def save_to_disk(self):
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

    def clear_cache(self):
        self.user_data = {}
        self.top_users = self.load_top_users()
        self.total_messages = self.load_total_messages()

async def periodic_save():
    while True:
        await asyncio.sleep(20)
        threading.Thread(target=data_cache.save_to_disk).start()

def read_total():
    if os.path.exists(total_path):
        with open(total_path, 'r') as file:
            return json.load(file).get('count', 0)
    return 0

token = load_token()
blacklisted = load_blacklist()
intents = discord.Intents.all()

class MyClient(discord.Client):
    async def on_ready(self):
        total_messages_logged = read_total()
        total_users = count_users()
        logger.info(f'Logged in as {self.user}')
        logger.info(f'Total messages logged: {total_messages_logged}')
        logger.info(f'Total users: {total_users}')
        await self.change_presence(status=discord.Status.dnd)

        self.loop.create_task(periodic_save())

    async def on_message(self, message):
        if message.author == self.user:
            return

        try:
            if message.content.startswith('!'):
                await self.handle_command(message)

            blacklisted_users = load_blacklist()
            author_username = f"{message.author.name}#{message.author.discriminator}"
            if message.author.name in blacklisted_users or author_username in blacklisted_users:
                return

            if data_cache.lock.locked():
                await asyncio.to_thread(self.process_message, message)
            else:
                await asyncio.to_thread(self.process_message, message)
        except Exception as e:
            logger.error(f"Error processing message from {message.author.name}: {e}")

    def process_message(self, message):
        data_cache.save_user_message(message.author.name, message)

    async def handle_command(self, message):
        command = message.content.lower().split(' ')[0]
        valid_commands = ['!help', '!user', '!top', '!total', '!bl', '!bladd', '!blremove', '!remove', '!random']
        
        if command not in valid_commands:
            return

        msg = await message.reply("Processing...")
        try:
            if command == '!help':
                await send_help_embed(message.channel)
            elif command.startswith('!user'):
                parts = message.content.split(' ', 1)
                if len(parts) == 1:
                    username = ""
                else:
                    username = parts[1].strip()
                await get_user_info(message, username)
            elif command == '!top':
                await send_top(message.channel)
            elif command == '!total':
                await send_total(message.channel)
            elif command == '!bl':
                await send_blacklist(message.channel)
            elif command.startswith('!bladd'):
                await add_to_blacklist(message)
            elif command.startswith('!blremove'):
                await remove_from_blacklist(message)
            elif command.startswith('!remove'):
                username = message.content.split(' ', 1)[1]
                await remove_user(message, username)
            elif command == '!random':
                await send_random_user_info(message.channel)
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            await msg.edit(content=f"Error handling command {command}")
        else:
            await msg.delete()

if __name__ == "__main__":
    data_cache = DataCache()
    client = MyClient(intents=intents)
    client.run(token)