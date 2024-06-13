import os
import discord
import json

users_dir = os.path.join('data', 'users')
top_path = os.path.join('data', 'top.json')
admin_path = os.path.join('data', 'admin.json')

def load_admins():
    if not os.path.exists(admin_path):
        return []
    with open(admin_path, 'r') as file:
        return json.load(file)

async def check_admin(user_id):
    admins = load_admins()
    return str(user_id) in admins

async def remove_user(message, username):
    try:
        if not await check_admin(message.author.id):
            embed = discord.Embed(title="Error", description="You don't have permission to perform this action.", color=discord.Color.red())
            await message.channel.send(embed=embed)
            return

        user_file_path = os.path.join(users_dir, f'{username}.json')
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
            
        if os.path.exists(top_path):
            with open(top_path, 'r+') as file:
                data = json.load(file)
                if username in data:
                    del data[username]
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
                else:
                    embed = discord.Embed(title="Error", description=f"User {username} not found in top data.", color=discord.Color.red())
                    await message.channel.send(embed=embed)
                    return
        else:
            embed = discord.Embed(title="Error", description="Top data file does not exist.", color=discord.Color.red())
            await message.channel.send(embed=embed)
            return

        embed = discord.Embed(title="Remove User", description=f"User {username} has been removed.", color=discord.Color.red())
        await message.channel.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred while removing user {username}: {e}", color=discord.Color.red())
        await message.channel.send(embed=embed)