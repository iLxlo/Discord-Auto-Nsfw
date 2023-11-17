import discord
from discord.ext import commands
import asyncio

class SendCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def send(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand. Use `,send embed {link}` or `,send custom`.")

    @send.command(name='embed')
    async def send_embed(self, ctx, link):
        content = fetch_content(link)

        initial_message = await ctx.send(content)

        title = await self.get_user_input_and_delete(ctx, "Enter embed title (type 'none' to skip):")
        description = await self.get_user_input_and_delete(ctx, "Enter embed description:")
        button_label = await self.get_user_input_and_delete(ctx, "Enter button label (type 'none' to skip):")
        image_link = await self.get_user_input_and_delete(ctx, "Enter embed image link (type 'none' to skip):")
        add_emoji = await self.get_user_input_and_delete(ctx, "Do you want to add an emoji to the button label? Type 'yes' or 'no':")

        emoji = None
        if add_emoji.lower() == 'yes':
            emoji = await self.get_user_input_and_delete(ctx, "Select an emoji:")

        extra_button = await self.get_user_input_and_delete(ctx, "Do you want to add an extra button? Type 'yes' or 'no':")

        extra_button_label = extra_button_link = extra_button_emoji = None
        if extra_button.lower() == 'yes':
            extra_button_label = await self.get_user_input_and_delete(ctx, "Enter the label for the extra button:")
            extra_button_link = await self.get_user_input_and_delete(ctx, "Enter the link for the extra button:")
            extra_button_emoji = await self.get_user_input_and_delete(ctx, "Enter the emoji for the extra button:")

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x00ff00 
        )

        if image_link:
            embed.set_image(url=image_link)

        view = discord.ui.View()
        if button_label:
            button = discord.ui.Button(
                label=button_label,
                emoji=emoji,
                url=link,
                style=discord.ButtonStyle.link
            )
            view.add_item(button)

        if extra_button_label and extra_button_link:
            extra_button = discord.ui.Button(
                label=extra_button_label,
                emoji=extra_button_emoji,
                url=extra_button_link,
                style=discord.ButtonStyle.link
            )
            view.add_item(extra_button)

        await initial_message.edit(content=content, embed=embed, view=view)

    async def get_user_input_and_delete(self, ctx, question):
        initial_message = await ctx.send(question)
        try:
            user_input = await self.client.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
            await user_input.delete()
            return str(user_input.content) if user_input.content.lower() != 'none' else None
        except asyncio.TimeoutError:
            await ctx.send("Timeout. Command canceled.")
            raise
        finally:
            await initial_message.delete()

def fetch_content(link):
    return f"Content fetched from {link}"

async def setup(client):
    await client.add_cog(SendCog(client))
