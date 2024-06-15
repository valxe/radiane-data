import os
import json
import discord

blacklist_path = os.path.join('data', 'blacklist.json')
admin_path = os.path.join('data', 'admin.json')
top_path = os.path.join('data', 'top.json')
users_dir = os.path.join('data', 'users')

def load_blacklist():
    if not os.path.exists(blacklist_path):
        return []
    with open(blacklist_path, 'r') as file:
        return json.load(file)

def load_admins():
    if not os.path.exists(admin_path):
        return []
    with open(admin_path, 'r') as file:
        return json.load(file)

async def send_blacklist(channel):
    try:
        blacklisted_users = load_blacklist()
        if blacklisted_users:
            embed = discord.Embed(title="Blacklisted Users", description=', '.join(blacklisted_users), color=discord.Color.red())
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Blacklisted Users", description="No users in the blacklist.", color=discord.Color.green())
            await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await channel.send(embed=embed)

async def add_to_blacklist(message):
    try:
        if await check_admin(message.author.id):
            username_to_add = message.content.split(' ', 1)[1]
            blacklisted_users = load_blacklist()
            if username_to_add not in blacklisted_users:
                blacklisted_users.append(username_to_add)
                with open(blacklist_path, 'w') as file:
                    json.dump(blacklisted_users, file)
                embed = discord.Embed(title="Success", description=f"User {username_to_add} added to the blacklist.", color=discord.Color.green())
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Info", description=f"User {username_to_add} is already in the blacklist.", color=discord.Color.red())
                await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Error", description="You don't have permission to perform this action.", color=discord.Color.red())
            await message.channel.send(embed=embed)
    except IndexError:
        embed = discord.Embed(title="Error", description="Please specify a username to add to the blacklist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def remove_from_blacklist(message):
    try:
        if await check_admin(message.author.id):
            username_to_remove = message.content.split(' ', 1)[1]
            blacklisted_users = load_blacklist()
            if username_to_remove in blacklisted_users:
                blacklisted_users.remove(username_to_remove)
                with open(blacklist_path, 'w') as file:
                    json.dump(blacklisted_users, file)
                embed = discord.Embed(title="Success", description=f"User {username_to_remove} removed from the blacklist.", color=discord.Color.green())
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Info", description=f"User {username_to_remove} not found in the blacklist.", color=discord.Color.red())
                await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Error", description="You don't have permission to perform this action.", color=discord.Color.red())
            await message.channel.send(embed=embed)
    except IndexError:
        embed = discord.Embed(title="Error", description="Please specify a username to remove from the blacklist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def check_admin(command_author_id):
    admins = load_admins()
    if str(command_author_id) in admins:
        return True
    else:
        return False