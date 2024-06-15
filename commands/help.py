import discord

async def send_help_embed(channel):
    help_commands = {
        'General': {
            '!user {username}': "Retrieves information about the user's message activity.",
            '!top': "Displays the top 10 users by number of messages.",
            '!total': "Displays the total number of messages logged by the bot.",
            '!random': "Retrieves random user information."
        },
        'Moderation': {
            '!remove {username}': "Removes a user from the database. - Discontinued",
            '!bl': "Lists all blacklisted users.",
            '!bladd {username}': "Adds a user to the blacklist. - Admin Only",
            '!blremove {username}': "Removes a user from the blacklist. - Admin Only"
        }
    }

    embed = discord.Embed(
        title="📚 Command Help",
        description="Here are the available commands for the bot. Use them to interact with the bot.",
        color=discord.Color.blue()
    )

    for category, commands in help_commands.items():
        command_list = '\n'.join([f"**{cmd}**: {desc}" for cmd, desc in commands.items()])
        embed.add_field(name=f"__{category} Commands__", value=command_list, inline=False)

    embed.set_footer(text="For more information or assistance, contact the server admin.")

    await channel.send(embed=embed)