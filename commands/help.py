import discord

async def send_help_embed(channel):
    help_commands = {
        'bl': "Usage: `!bl` - Lists all blacklisted users. - Admin Only",
        'bladd': "Usage: `!bladd {username}` - Adds a user to the blacklist. - Admin Only",
        'blremove': "Usage: `!blremove {username}` - Removes a user from the blacklist. - Admin Only"
        }

    embed = discord.Embed(title="Command Help", color=discord.Color.blue())

    for command, description in help_commands.items():
        embed.add_field(name=f"!{command}", value=description, inline=False)

    await channel.send(embed=embed)
