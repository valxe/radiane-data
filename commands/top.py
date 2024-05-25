import os
import json
import discord
from discord.ui import Button, View

top_path = os.path.join('data', 'top.json')

class TopUsersView(View):
    def __init__(self, top_users, current_page=0, items_per_page=10):
        super().__init__()
        self.top_users = top_users
        self.current_page = current_page
        self.items_per_page = items_per_page
        self.max_page = (len(top_users) - 1) // items_per_page

        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        first_button = Button(label='⏮️', style=discord.ButtonStyle.primary)
        previous_button = Button(label='◀️', style=discord.ButtonStyle.primary)
        next_button = Button(label='▶️', style=discord.ButtonStyle.primary)
        last_button = Button(label='⏭️', style=discord.ButtonStyle.primary)

        first_button.callback = self.first_page
        previous_button.callback = self.previous_page
        next_button.callback = self.next_page
        last_button.callback = self.last_page

        self.add_item(first_button)
        self.add_item(previous_button)
        self.add_item(next_button)
        self.add_item(last_button)

        first_button.disabled = self.current_page == 0
        previous_button.disabled = self.current_page == 0
        next_button.disabled = self.current_page == self.max_page
        last_button.disabled = self.current_page == self.max_page

    def get_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_users = self.top_users[start:end]

        embed = discord.Embed(title=f"Top Users (Page {self.current_page + 1}/{self.max_page + 1})", color=discord.Color.purple())
        for user, count in page_users:
            embed.add_field(name=user, value=str(count), inline=False)
        return embed

    async def update_message(self, interaction):
        embed = self.get_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def first_page(self, interaction):
        self.current_page = 0
        await self.update_message(interaction)

    async def previous_page(self, interaction):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_message(interaction)

    async def next_page(self, interaction):
        if self.current_page < self.max_page:
            self.current_page += 1
        await self.update_message(interaction)

    async def last_page(self, interaction):
        self.current_page = self.max_page
        await self.update_message(interaction)

async def send_top(channel):
    try:
        if os.path.exists(top_path):
            with open(top_path, 'r') as file:
                top_users = json.load(file)
            sorted_top_users = sorted(top_users.items(), key=lambda item: item[1], reverse=True)
            view = TopUsersView(sorted_top_users)
            embed = view.get_embed()
            await channel.send(embed=embed, view=view)
        else:
            embed = discord.Embed(title="Error", description="Top users data not available.", color=discord.Color.red())
            await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred: {e}", color=discord.Color.red())
        await channel.send(embed=embed)
