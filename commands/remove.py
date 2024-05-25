import os
import json
import discord

users_dir = os.path.join('data', 'users')
top_path = os.path.join('data', 'top.json')

async def remove_user(ctx, username):
    user_file_path = os.path.join(users_dir, f'{username}.json')

    try:
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
        else:
            await ctx.send(f"User {username} does not exist.")
            return

        if os.path.exists(top_path):
            with open(top_path, 'r+') as file:
                data = json.load(file)
                if 'users' in data and username in data['users']:
                    del data['users'][username]
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
                else:
                    await ctx.send(f"User {username} not found in top data.")
                    return

        await ctx.send(f"User {username} has been removed.")
    except Exception as e:
        await ctx.send(f"An error occurred while removing user {username}: {e}")
