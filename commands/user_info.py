import os
import sqlite3
import discord
from datetime import datetime, date
import random
import json

db_path = os.path.join('data', 'database.db')
blacklist_path = os.path.join('data', 'blacklist.json')

def format_number(number):
    return "{:,}".format(number)

async def get_user_info(message, username: str):
    try:
        if not username:
            username = message.author.name

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            with open(blacklist_path, 'r') as f:
                blacklist = json.load(f)

            if username in blacklist:
                embed = discord.Embed(title="Blacklisted User", description=f"The user `{username}` is blacklisted and cannot be displayed.", color=discord.Color.red())
                await message.channel.send(embed=embed)
                return

            cursor.execute("SELECT user_pfp, messages FROM users WHERE user_name = ?", (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_pfp, messages = user_data
                all_user_data = json.loads(messages)

                all_user_data.sort(key=lambda x: datetime.strptime(x['message_time'], '%Y-%m-%d %H:%M:%S'))

                today = date.today()
                today_user_data = [msg for msg in all_user_data if datetime.strptime(msg['message_time'], '%Y-%m-%d %H:%M:%S').date() == today]

                total_messages = len(all_user_data)
                recent_messages = all_user_data[-5:][::-1]
                recent_str = '\n'.join([f"{msg['message_time']}: {msg.get('content', '')}" for msg in recent_messages])

                embed = discord.Embed(title=f"User: {username}", description=f"Total Messages: {format_number(total_messages)}", color=discord.Color.blue())
                embed.add_field(name="Recent Messages", value=f"{recent_str}")

                if user_pfp:
                    embed.set_thumbnail(url=user_pfp)

                cursor.execute("SELECT user_name, message_count FROM top_users")
                top_data = cursor.fetchall()
                sorted_users = sorted(top_data, key=lambda item: item[1], reverse=True)
                placement = next((rank + 1 for rank, (user, _) in enumerate(sorted_users) if user == username), "Not ranked")

                embed.add_field(name="Leaderboard Placement", value=f"{format_number(placement)}", inline=False)

                file_name = f"{username}_messages.txt"
                with open(file_name, 'w', encoding='utf-8') as file:
                    all_messages = '\n'.join([f"{msg['message_time']}: {msg.get('content', '')}" for msg in reversed(all_user_data)])
                    file.write(all_messages)

                file = discord.File(file_name, filename=file_name)
                
                await message.channel.send(file=file, embed=embed)
                
                os.remove(file_name)
            else:
                embed = discord.Embed(title="Error", description="User not found or has not sent any messages yet.", color=discord.Color.red())
                await message.channel.send(embed=embed)
    except Exception as error:
        embed = discord.Embed(title="Error", description=f"An error occurred: {error}", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def get_random_user_info(message):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_name FROM users")
            users = cursor.fetchall()

            if not users:
                embed = discord.Embed(title="Error", description="No user data available.", color=discord.Color.red())
                await message.channel.send(embed=embed)
                return

            random_user = random.choice(users)[0]
            await get_user_info(message, random_user)
    except Exception as error:
        embed = discord.Embed(title="Error", description=f"An error occurred: {error}", color=discord.Color.red())
        await message.channel.send(embed=embed)