import discord
import asyncio
import json
import os
from colorama import Fore, Style, init
from threading import Thread

from commands.blacklist import send_blacklist, add_to_blacklist, remove_from_blacklist
from commands.help import send_help_embed
from flask_app import start_flask_server

init(autoreset=True)

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
    if not os.path.exists(blacklist_path):
        return []
    with open(blacklist_path, 'r') as file:
        return json.load(file)

def count_users():
    if not os.path.exists(users_dir):
        return 0
    file_count = sum([len(files) for _, _, files in os.walk(users_dir)])
    return file_count

def save_user_message(user_name, message):
    user_file = os.path.join(users_dir, f'{user_name}.json')
    if os.path.exists(user_file):
        with open(user_file, 'r') as file:
            user_data = json.load(file)
    else:
        user_data = []

    message_info = {
        'message_time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'content': message.content
    }
    user_data.append(message_info)

    with open(user_file, 'w') as file:
        json.dump(user_data, file, indent=4)

    update_top(user_name)
    update_total()

def update_top(user_name):
    if not os.path.exists(top_path):
        top_users = {}
    else:
        with open(top_path, 'r') as file:
            top_users = json.load(file)

    if user_name in top_users:
        top_users[user_name] += 1
    else:
        top_users[user_name] = 1

    sorted_top_users = dict(sorted(top_users.items(), key=lambda item: item[1], reverse=True))

    with open(top_path, 'w') as file:
        json.dump(sorted_top_users, file, indent=4)

def update_total():
    if not os.path.exists(total_path):
        total_messages = {'count': 0}
    else:
        with open(total_path, 'r') as file:
            total_messages = json.load(file)

    total_messages['count'] += 1

    with open(total_path, 'w') as file:
        json.dump(total_messages, file, indent=4)

def read_total():
    if not os.path.exists(total_path):
        return 0
    with open(total_path, 'r') as file:
        total_messages = json.load(file)
    return total_messages['count']

token = load_token()
blacklisted = load_blacklist()
intents = discord.Intents.all()

class MyClient(discord.Client):
    async def on_ready(self):
        total_messages_logged = read_total()
        total_users = count_users()
        print(f'{Fore.GREEN}Logged in as {self.user}')
        print(f'{Fore.YELLOW}Total messages logged: {total_messages_logged}')
        print(f'{Fore.YELLOW}Total users: {total_users}')
        await self.change_presence(status=discord.Status.dnd)

        while True:
            await self.update_presence_message()
            await asyncio.sleep(120)

    async def update_presence_message(self):
        new_status_message = f"{read_total()} messages saved!"
        await self.change_presence(activity=discord.Game(new_status_message), status=discord.Status.dnd)

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
        save_user_message(message.author.name, message)

    async def handle_command(self, message):
        command = message.content.lower().split(' ')[0]
        if command == '!help':
            await send_help_embed(message.channel)
        elif command == '!bl':
            await send_blacklist(message.channel)
        elif command.startswith('!bladd'):
            await add_to_blacklist(message)
        elif command.startswith('!blremove'):
            await remove_from_blacklist(message)

def start_discord_client():
    client = MyClient(intents=intents)
    client.run(token)

flask_thread = Thread(target=start_flask_server)
discord_thread = Thread(target=start_discord_client)

flask_thread.start()
discord_thread.start()

flask_thread.join()
discord_thread.join()
