import asyncio
import math
import platform
import socket
from datetime import timedelta

import discord
import psutil
import uptime
from discord.ext import commands


class Admin:
    """
    Bot owner and admin commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def host(self, ctx):
        """
        Return host server information
        """
        server_uptime_seconds = uptime.uptime()
        server_uptime = timedelta(seconds=math.floor(server_uptime_seconds))

        processor = psutil.cpu_times_percent(interval=1)
        processor_system_load = processor.system
        processor_user_load = processor.user

        memory = psutil.virtual_memory()
        memory_load = memory.percent

        embed = discord.Embed()
        embed.add_field(name='Platform',
                        value=platform.platform().lower(), inline=False)
        embed.add_field(name='Hostname',
                        value=socket.gethostname().lower(), inline=False)
        embed.add_field(name='Host Uptime', value=str(
            server_uptime), inline=False)
        embed.add_field(name='CPU System Load', value=str(
            processor_system_load) + '%', inline=False)
        embed.add_field(name='CPU User Load', value=str(
            processor_user_load) + '%', inline=False)
        embed.add_field(name='Memory Load', value=str(
            memory_load) + '%', inline=False)
        embed.colour = 0x738bd7
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        """
        Load a cog
        """
        embed = discord.Embed()
        embed.colour = 0x738bd7
        embed.set_footer(text=f'Requested by {ctx.message.author}')

        try:
            self.bot.load_extension(cog)
        except:
            embed.add_field(name='Info', value=f'Failed to load {cog}')
        else:
            embed.add_field(name='Info', value=f'Successfully loaded {cog}')
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        """
        Unload a cog
        """
        embed = discord.Embed()
        embed.colour = 0x738bd7
        embed.set_footer(text=f'Requested by {ctx.message.author}')

        try:
            self.bot.unload_extension(cog)
        except:
            embed.add_field(name='Info', value=f'Failed to unload {cog}')
        else:
            embed.add_field(name='Info', value=f'Successfully unloaded {cog}')
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        """
        Reload a cog
        """
        embed = discord.Embed()
        embed.colour = 0x738bd7
        embed.set_footer(text=f'Requested by {ctx.message.author}')

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except:
            embed.add_field(name='Info', value=f'Failed to reload {cog}')
        else:
            embed.add_field(name='Info', value=f'Successfully reloaded {cog}')
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx, count: int = 10):
        """
        Shutdown the bot
        """
        embed = discord.Embed(
            title='Warning', description=f'This bot will now shutdown in {count} seconds')
        embed.set_footer(text=f'Requested by {ctx.message.author}')
        embed.colour = 0xe74c3c
        await ctx.send(embed=embed)

        await asyncio.sleep(count)
        quit()


def setup(bot):
    bot.add_cog(Admin(bot))
