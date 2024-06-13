import os
import random
import discord
from commands.user_info import get_user_info

users_dir = os.path.join('data', 'users')

async def send_random_user_info(channel):
    try:
        users = [f[:-5] for f in os.listdir(users_dir) if f.endswith('.json')]
        if not users:
            embed = discord.Embed(title="Error", description="No users found.", color=discord.Color.red())
            await channel.send(embed=embed)
            return

        random_user = random.choice(users)
        await get_user_info(channel, random_user)
    except Exception as error:
        embed = discord.Embed(title="Error", description=f"An error occurred: {error}", color=discord.Color.red())
        await channel.send(embed=embed)