import discord
from discord.ext import commands, tasks
import configparser
import re
import asyncio

config = configparser.ConfigParser()
config.read("./data/config.ini")

class DeleteCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.delete_task.start()  # Start the looping task

    def cog_unload(self):
        self.delete_task.cancel()  # Cancel the looping task when unloading the cog

    def is_valid_timeout(self, timeout):
        return re.match(r'^(\d+[hms])+$', timeout)

    @tasks.loop(seconds=10)  # Initial interval is set to 10 seconds
    async def delete_task(self):
        config = configparser.ConfigParser()
        config.read("./data/config.ini")
        timeout_str = config.get("DeleteTimeout", "timeout")

        if timeout_str:
            timeout = self.parse_timeout(timeout_str)
            channel_id = config.get("Discord", "channel", fallback="0")
            if channel_id.isdigit():
                channel = self.client.get_channel(int(channel_id))
                if channel:
                    deleted_messages = await channel.purge(limit=None)
                    if deleted_messages:
                        embed = discord.Embed(
                            title="Messages Deleted",
                            description=f"Posting new images within seconds!",
                            color=0x2f3136
                        )
                        await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="No Messages Found",
                            description=f"No messages found to delete in the specified channel ({channel.mention}).",
                            color=0xFF0000
                        )
                        await channel.send(embed=embed)
                else:
                    print("Channel not found.")
            else:
                print("Invalid channel ID in the config file.")

    def parse_timeout(self, timeout_str):
        # Convert timeout string to seconds
        total_seconds = 0
        matches = re.finditer(r'(\d+)([hms])', timeout_str)
        for match in matches:
            value, unit = int(match.group(1)), match.group(2)
            if unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 's':
                total_seconds += value
        return total_seconds

    @commands.command()
    async def setdeletetimeout(self, ctx, timeout: str):
        if not self.is_valid_timeout(timeout):
            embed = discord.Embed(
                title="Invalid Timeout Format",
                description="Invalid timeout format. Please use '1h', '10m', '1s', etc.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        config = configparser.ConfigParser()
        config.read("./data/config.ini")
        if "DeleteTimeout" not in config:
            config["DeleteTimeout"] = {}

        config["DeleteTimeout"]["timeout"] = timeout
        self.delete_task.change_interval(seconds=self.parse_timeout(timeout))  # Change the loop interval dynamically

        with open("./data/config.ini", "w") as config_file:
            config.write(config_file)

        embed = discord.Embed(
            title="Delete Timeout Updated",
            description=f"Delete timeout set to {timeout}. The automatic delete interval has been updated.",
            color=0x2f3136
        )
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(DeleteCog(client))
