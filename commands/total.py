import os
import sqlite3
import discord

db_path = os.path.join('data', 'database.db')

def count_users():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def read_total():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM total_messages WHERE id = 1")
        return cursor.fetchone()[0]

def format_number(number):
    return "{:,}".format(number)

async def send_total(channel):
    try:
        total_messages_logged = read_total()
        total_users = count_users()
        embed = discord.Embed(title="Total Messages and Users Logged", color=discord.Color.green())
        embed.add_field(name="Total Messages", value=format_number(total_messages_logged), inline=False)
        embed.add_field(name="Total Users", value=format_number(total_users), inline=False)
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await channel.send(embed=embed)