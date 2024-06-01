import discord

async def send_help_embed(channel):
    help_commands = {
        'user': "Usage: `!user {username}` - Retrieves information about the user's message activity.",
        'random': "Usage: `!random` - Retrieves information about a random user.",
        'top': "Usage: `!top` - Displays the top 10 users by number of messages.",
        'total': "Usage: `!total` - Displays the total number of messages logged by the bot.",
        'remove': "Usage: `!remove {username}` - Removes a user from the database.",
        'bl': "Usage: `!bl` - Lists all blacklisted users.",
        'bladd': "Usage: `!bladd {username}` - Adds a user to the blacklist. - Admin Only",
        'blremove': "Usage: `!blremove {username}` - Removes a user from the blacklist. - Admin Only",
    }

    embed = discord.Embed(title="Command Help", color=discord.Color.blue())

    for command, description in help_commands.items():
        embed.add_field(name=f"!{command}", value=description, inline=False)

    await channel.send(embed=embed)
