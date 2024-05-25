import discord
import asyncio
import json
import os
from commands.top import send_top
from commands.total import send_total
from commands.blacklist import send_blacklist, add_to_blacklist, remove_from_blacklist
from commands.user_info import get_user_info
from commands.help import send_help_embed
from commands.remove import remove_user

MAX_CHUNK_SIZE_MB = 24
CHUNK_SIZE = MAX_CHUNK_SIZE_MB * 1024 * 1024

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
        if user_name not in self.user_data:
            self.user_data[user_name] = []

        user_pfp = str(message.author.avatar.url) if not self.user_data[user_name] else None
        if user_pfp:
            self.user_data[user_name].insert(0, {"user_pfp": user_pfp})

        self.user_data[user_name].append({
            'message_time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': message.content
        })

        self.update_top(user_name)
        self.total_messages += 1

    def update_top(self, user_name):
        self.top_users[user_name] = self.top_users.get(user_name, 0) + 1
        self.top_users = dict(sorted(self.top_users.items(), key=lambda item: item[1], reverse=True))

    async def save_to_disk(self):
        for user_name, messages in self.user_data.items():
            user_file = os.path.join(users_dir, f'{user_name}.json')
            if os.path.exists(user_file):
                with open(user_file, 'r') as file:
                    existing_data = json.load(file)
                messages = existing_data + messages

            with open(user_file, 'w') as file:
                json.dump(messages, file, indent=4)
        
        with open(top_path, 'w') as file:
            json.dump(self.top_users, file, indent=4)

        with open(total_path, 'w') as file:
            json.dump({'count': self.total_messages}, file, indent=4)

        self.clear_cache()

    def clear_cache(self):
        self.user_data = {}
        self.top_users = self.load_top_users()
        self.total_messages = self.load_total_messages()

data_cache = DataCache()

async def periodic_save():
    while True:
        await asyncio.sleep(20)
        await data_cache.save_to_disk()

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
        print(f'Logged in as {self.user}')
        print(f'Total messages logged: {total_messages_logged}')
        print(f'Total users: {total_users}')
        await self.change_presence(status=discord.Status.dnd)

        self.loop.create_task(self.update_presence_message())
        self.loop.create_task(periodic_save())

    async def update_presence_message(self):
        while True:
            new_status_message = f"{read_total()} messages saved!"
            await self.change_presence(activity=discord.Game(new_status_message), status=discord.Status.dnd)
            await asyncio.sleep(15)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!'):
            await self.handle_command(message)

        blacklisted_users = load_blacklist()
        author_username = f"{message.author.name}#{message.author.discriminator}"
        if message.author.name in blacklisted_users or author_username in blacklisted_users:
            return
        
        print(f'({message.created_at.strftime("%Y-%m-%d %H:%M:%S")}) {message.author.name}: {message.content}')
        
        data_cache.save_user_message(message.author.name, message)

    async def handle_command(self, message):
        command = message.content.lower().split(' ')[0]
        if command == '!help':
            await send_help_embed(message.channel)
        elif command.startswith('!user'):
            username = message.content.split(' ', 1)[1]
            await get_user_info(message.channel, username)
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
            await remove_user(message.channel, username)

if __name__ == "__main__":
    client = MyClient(intents=intents)
    client.run(token)
