import os
import json
import discord

total_path = os.path.join('data', 'total.json')
user_data_path = os.path.join('data', 'users')

def count_users():
    if not os.path.exists(user_data_path):
        return 0
    file_count = sum([len(files) for _, _, files in os.walk(user_data_path)])
    return file_count

def read_total():
    if not os.path.exists(total_path):
        return 0
    with open(total_path, 'r') as file:
        total_messages = json.load(file)
    return total_messages['count']

async def send_total(channel):
    try:
        total_messages_logged = read_total()
        total_users = count_users()
        embed = discord.Embed(title="Total Messages and Users Logged", color=discord.Color.green())
        embed.add_field(name="Total Messages", value=str(total_messages_logged), inline=False)
        embed.add_field(name="Total Users", value=str(total_users), inline=False)
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await channel.send(embed=embed)
