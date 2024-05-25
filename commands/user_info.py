import os
import json
import discord
from datetime import datetime, date

users_dir = os.path.join('data', 'users')
top_path = os.path.join('data', 'top.json')

async def get_user_info(ctx, username: str):
    try:
        user_file_path = os.path.join(users_dir, f'{username}.json')
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r', encoding='utf-8') as file:
                user_data = json.load(file)

            user_pfp = user_data[0].get('user_pfp')

            all_user_data = [msg for msg in user_data if 'message_time' in msg and msg['message_time']]
            all_user_data.sort(key=lambda x: datetime.strptime(x['message_time'], '%Y-%m-%d %H:%M:%S'))

            today = date.today()
            today_user_data = [msg for msg in all_user_data if datetime.strptime(msg['message_time'], '%Y-%m-%d %H:%M:%S').date() == today]

            total_messages = len(all_user_data)
            recent_messages = all_user_data[-5:][::-1]
            recent_str = '\n'.join([f"{msg['message_time']}: {msg.get('content', '')}" for msg in recent_messages])

            embed = discord.Embed(title=f"User: {username}", description=f"Total Messages: {total_messages}", color=discord.Color.blue())
            embed.add_field(name="Recent Messages", value=f"{recent_str}")

            if user_pfp:
                embed.set_thumbnail(url=user_pfp)

            with open(top_path, 'r', encoding='utf-8') as top_file:
                top_data = json.load(top_file)
            sorted_users = sorted(top_data.items(), key=lambda item: item[1], reverse=True)
            placement = next((rank + 1 for rank, (user, _) in enumerate(sorted_users) if user == username), "Not ranked")

            embed.add_field(name="Leaderboard Placement", value=f"{placement}", inline=False)

            file_name = f"{username}_messages.txt"
            with open(file_name, 'w', encoding='utf-8') as file:
                all_messages = '\n'.join([f"{msg['message_time']}: {msg.get('content', '')}" for msg in reversed(all_user_data)])
                file.write(all_messages)

            file = discord.File(file_name, filename=file_name)
            await ctx.send(file=file, embed=embed)
            os.remove(file_name)
        else:
            embed = discord.Embed(title="Error", description="User not found or has not sent any messages yet.", color=discord.Color.red())
            await ctx.send(embed=embed)
    except Exception as error:
        embed = discord.Embed(title="Error", description=f"An error occurred: {error}", color=discord.Color.red())
        await ctx.send(embed=embed)
