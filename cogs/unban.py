import discord
from discord.ext import commands
import asyncio

class UnbanCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bans_before_unban = []
        self.progress_message = None

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.ban_members

    @commands.group(name='unban', aliases=['ub'])
    async def unban(self, ctx):
        """Unban command."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand. Use ,help unban for more information.")

    @unban.command(name='all', aliases=['a'])
    async def unban_all(self, ctx):
        """Unban all users from the ban list."""
        self.bans_before_unban = []
        removed_count = 0

        embed = discord.Embed(title="Unban Progress", color=0x2f3136)
        embed.description = "Unban process in progress..."
        self.progress_message = await ctx.send(embed=embed)

        async for ban_entry in ctx.guild.bans():
            user = ban_entry.user
            try:
                await ctx.guild.unban(user)
                self.bans_before_unban.append(ban_entry)
                removed_count += 1
                remaining_count = len(self.bans_before_unban) - removed_count

                embed.description = (
                    f"-------------------------------------------\n"
                    f"- Currently removed: **` {removed_count} bans `**\n"
                    f"-------------------------------------------"
                )
                await self.progress_message.edit(embed=embed)

            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to unban members.")
                break

        await asyncio.sleep(2)
        if self.progress_message:
            embed.description = (
                f"-------------------------------------------\n"
                f"- Currently removed: **` {removed_count} bans `**\n"
                f"-------------------------------------------"
            )
            await self.progress_message.edit(embed=embed)
            self.progress_message = None

    @unban.command(name='user', aliases=['u']) # didnt tested but ig it works if not open issues/pull request
    async def unban_user(self, ctx, *, user):
        """Unban a specific user by ID or mention."""
        try:
            banned_user = await commands.converter.UserConverter().convert(ctx, user)
            await ctx.guild.unban(banned_user)
            await ctx.send(f"Successfully unbanned {banned_user.mention}.")
        except (commands.BadArgument, discord.NotFound):
            await ctx.send("User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to unban members.")

    @commands.command(name='progress', aliases=['p'])
    async def unban_progress(self, ctx):
        """Show progress of the unban process."""
        if self.progress_message:
            removed_count = len(self.bans_before_unban)

            embed = discord.Embed(title="Unban Progress", color=0x2f3136)
            embed.description = (
                f"-------------------------------------------\n"
                f"- Currently removed: **` {removed_count} bans `**\n"
                f"-------------------------------------------"
            )
            await self.progress_message.edit(embed=embed)
        else:
            await ctx.send("No unban process has been initiated.")

async def setup(client):
    await client.add_cog(UnbanCog(client))
