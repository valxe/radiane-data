import discord
import logging
import asyncio
import threading
from commands.top import send_top
from commands.total import send_total
from commands.blacklist import send_blacklist, add_to_blacklist, remove_from_blacklist
from commands.user_info import get_user_info, get_random_user_info
from commands.help import send_help_embed
from data import DataCache, periodic_save, run_fastapi
from logic import load_token, load_blacklist, count_users, read_total

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

token = load_token()
blacklisted = load_blacklist()
intents = discord.Intents.all()

class MyClient(discord.Client):
    async def on_ready(self) -> None:
        total_messages_logged = read_total()
        total_users = count_users()
        logger.info(f'Logged in as {self.user}')
        logger.info(f'Total messages logged: {total_messages_logged}')
        logger.info(f'Total users: {total_users}')
        await self.change_presence(status=discord.Status.dnd)

        self.loop.create_task(periodic_save(data_cache))

    async def on_message(self, message: discord.Message) -> None:
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

    def process_message(self, message: discord.Message) -> None:
        user_name = message.author.name
        user_pfp = str(message.author.avatar.url) if message.author.avatar else None
        message_data = {
            'message_time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': message.content
        }
        data_cache.save_user_message(user_name, user_pfp, message_data)

    async def handle_command(self, message: discord.Message) -> None:
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
                await message.reply("This command has been removed since I want to keep as much data as possible.")
            elif command == '!random':
                await get_random_user_info(message)
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            await msg.edit(content=f"Error handling command {command}")
        else:
            await msg.delete()

if __name__ == "__main__":
    data_cache = DataCache()
    client = MyClient(intents=intents)
    
    # Start the FastAPI and Discord bot in separate threads
    fastapi_thread = threading.Thread(target=run_fastapi)
    discord_bot_thread = threading.Thread(target=client.run, args=(token,))
    
    fastapi_thread.start()
    discord_bot_thread.start()
    
    fastapi_thread.join()
    discord_bot_thread.join()