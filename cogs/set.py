import discord
from discord.ext import commands, tasks
import requests
import asyncio
import random
import configparser
import re
from discord.ui import View, Button

class NekoCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = configparser.ConfigParser()
        self.config.read("./data/config.ini")

        self.nekobot_api_key = self.config["Nekobot"]["api_key"]
        self.auth_url = self.config["Auth"]["URL"]

        self.image_types_config = self.config["ImageTypes"]
        self.image_types = [self.image_types_config[key] for key in self.image_types_config]

        self.send_interval_task.start()

    @tasks.loop(seconds=10)  # Default interval is 10 seconds
    async def send_interval_task(self):
        image_type = random.choice(self.image_types)
        response = requests.get(
            f"https://nekobot.xyz/api/image?type={image_type}",
            headers={"Authorization": "Bearer " + self.nekobot_api_key},
        )

        channel_id = int(self.config["Discord"]["channel"])
        channel = self.client.get_channel(channel_id)

        if response.status_code == 200:
            image_url = response.json()["message"]
            view = discord.ui.View()
            button = discord.ui.Button(
                label="Verify to see more", url=self.auth_url, style=discord.ButtonStyle.link
            )
            view.add_item(button)
            embed = discord.Embed(
                description=f"[Want more? Verify to see more]({self.auth_url}).", color=0x2f3136
            )
            embed.set_image(url=image_url)

            await channel.send(embed=embed, view=view)
        else:
            print(f"Error sending Nekobot image ({image_type}):", response.status_code)
            await channel.send(embed=self.error_embed(f"Error sending Nekobot image ({image_type})."))

    @send_interval_task.before_loop
    async def before_send_interval_task(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Set cog is ready!")

    @commands.command()
    async def setinterval(self, ctx, interval: str):
        if ctx.author.guild_permissions.administrator:
            if self.is_valid_interval(interval):
                interval_seconds = self.parse_interval(interval)
                self.send_interval_task.change_interval(seconds=interval_seconds)
                self.config["SendInterval"]["interval"] = interval
                with open("./data/config.ini", "w") as config_file:
                    self.config.write(config_file)
                embed = discord.Embed(
                    title="Send Interval Updated",
                    description=f"Send interval updated to {interval}.",
                    color=0x2f3136
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Invalid Interval",
                    description="Invalid interval format. Please use '1h', '10m', '1s', etc.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Insufficient Permissions",
                description="You do not have the required permissions to use this command.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    def is_valid_interval(self, interval):
        return re.match(r'^(\d+[hms])+$', interval)

    def parse_interval(self, interval):
        # Convert interval string to seconds
        total_seconds = 0
        matches = re.finditer(r'(\d+)([hms])', interval)
        for match in matches:
            value, unit = int(match.group(1)), match.group(2)
            if unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 's':
                total_seconds += value
        return total_seconds

    def error_embed(self, message):
        return discord.Embed(
            title="Error",
            description=message,
            color=0xFF0000
        )

async def setup(client):
    await client.add_cog(NekoCog(client))
