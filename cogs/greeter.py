# greeter.py
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
import time
import os
from typing import Union
from colorama import Fore
import configparser

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
database_path = os.path.join(data_folder, 'database.ini')


class Greeter(commands.Cog):
    def __init__(self, client, database_path):
        self.client = client
        self.join_data = {}
        self.database_path = database_path

        # Create an instance of ConfigParser
        self.config = configparser.ConfigParser()
        self.config.read(database_path)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.client.user.name} (ID: {self.client.user.id})')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        welcome_channel_id, threshold = self.get_guild_settings(guild_id)

        if welcome_channel_id:
            welcome_channel = member.guild.get_channel(welcome_channel_id)
            if welcome_channel:
                self.join_data.setdefault(guild_id, {'counter': 0, 'members': []})
                self.join_data[guild_id]['counter'] += 1
                self.join_data[guild_id]['members'].append(member.mention)

                if self.join_data[guild_id]['counter'] >= threshold:
                    welcome_message = f"Welcome {' '.join(self.join_data[guild_id]['members'])}!"
                    greeting_message = await welcome_channel.send(welcome_message)

                    self.join_data[guild_id]['counter'] = 0
                    self.join_data[guild_id]['members'] = []

                    time.sleep(1)

                    await self.schedule_deletion(greeting_message, 1)

    @commands.group(name='greeter')
    @has_permissions(manage_messages=True)
    async def greeter(self, ctx):
        if ctx.invoked_subcommand is None:
            message = await ctx.send('Invalid greeter command.')
            await asyncio.sleep(5)
            await message.delete()

    @greeter.command(name='set')
    @has_permissions(manage_messages=True)
    async def set_greeter_channel(self, ctx, threshold: int = 1, channel_id_or_threshold: Union[discord.TextChannel, int] = None):
        if isinstance(channel_id_or_threshold, discord.TextChannel):
            channel_id = channel_id_or_threshold.id
        else:
            channel_id = ctx.channel.id if channel_id_or_threshold is None else channel_id_or_threshold

        self.set_guild_settings(ctx.guild.id, channel_id, threshold)
        message = await ctx.send(f'Greeter channel set to #{ctx.guild.get_channel(channel_id).name} with a threshold of {threshold}.')
        await asyncio.sleep(3)
        await message.delete()

    @greeter.command(name='delete')
    @has_permissions(manage_messages=True)
    async def delete_greeter_message(self, ctx, delay_seconds: int = 1):
        guild_id = ctx.guild.id
        welcome_channel_id, _ = self.get_guild_settings(guild_id)

        if welcome_channel_id:
            welcome_channel = ctx.guild.get_channel(welcome_channel_id)
            if welcome_channel:
                async for message in welcome_channel.history(limit=1):
                    await message.delete(delay=delay_seconds)

                self.config[f'GUILD:{guild_id}']['DELETER'] = str(delay_seconds)
                with open(database_path, 'w') as configfile:
                    self.config.write(configfile)

                update_message = await ctx.send(f"Greeter message will be deleted after {delay_seconds} seconds.")
                await asyncio.sleep(5)
                await update_message.delete()

    @greeter.command(name='stop')
    @has_permissions(manage_messages=True)
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        self.set_guild_settings(guild_id, None, 1)  # Set channel_id to None
        message = await ctx.send('Greeter functionality has been stopped.')
        await asyncio.sleep(3)
        await message.delete()

    async def schedule_deletion(self, message, delay_seconds):
        await asyncio.sleep(delay_seconds)
        await message.delete()

    def get_guild_settings(self, guild_id):
        if f'GUILD:{guild_id}' in self.config:
            channel_id = self.config[f'GUILD:{guild_id}'].get('channel', fallback=None)
            threshold = self.config[f'GUILD:{guild_id}'].getint('threshold', fallback=1)
            channel_id = int(channel_id) if channel_id and channel_id.lower() != 'none' else None

            return channel_id, threshold

        return None, None

    def set_guild_settings(self, guild_id, channel_id, threshold):
        self.config[f'GUILD:{guild_id}'] = {'channel': str(channel_id), 'threshold': str(threshold)}
        with open(database_path, 'w') as configfile:
            self.config.write(configfile)


async def setup(client):
    await client.add_cog(Greeter(client, database_path))
