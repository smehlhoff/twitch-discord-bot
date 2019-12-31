from datetime import datetime, timedelta

import discord
from discord.ext import commands
from pytz import timezone

from bot import load_config
from core.models import Follows, session


class General:
    """
    General bot commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @staticmethod
    def get_bot_uptime(timestamp):
        now = datetime.utcnow()
        ts = now - timestamp
        ts = timedelta(seconds=ts.seconds)
        return ts

    @staticmethod
    def get_us_timezones():
        places = {
            'pst': 'US/Pacific',
            'cst': 'US/Central',
            'est': 'US/Eastern'
        }

        output = {}
        now = datetime.now(timezone('UTC'))

        for place in places:
            timestamp = now.astimezone(timezone(places[place]))
            format_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            output[place] = format_timestamp
        return output

    @commands.group()
    async def about(self, ctx):
        """
        Return general information about the bot
        """
        if ctx.invoked_subcommand is None:
            owner = await self.bot.get_user_info(self.config['bot']['owner'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = session.query(Follows)
            users = query.distinct(Follows.user_id).group_by(
                Follows.user_id).count()
            follows = query.count()

            embed = discord.Embed()
            embed.add_field(name='Host Local Time (UTC)', value=timestamp)
            embed.add_field(name='Bot Uptime', value=str(
                self.get_bot_uptime(self.bot.bot_uptime)))
            embed.add_field(name='Owner', value=owner)
            embed.add_field(name='Total Users', value=users)
            embed.add_field(name='Total Follows', value=follows)
            embed.set_footer(text=f'Requested by {ctx.message.author}')
            embed.colour = 0x738bd7
            await ctx.send(embed=embed)

    @about.command()
    async def discord(self, ctx):
        """
        Return discord server information
        """
        guild = ctx.message.guild
        region = str(guild.region)

        embed = discord.Embed()
        embed.add_field(name='Name', value=guild.name, inline=False)
        embed.add_field(name='ID', value=guild.id, inline=False)
        embed.add_field(name='Created', value=guild.created_at.strftime(
            '%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name='Region', value=region.upper(), inline=False)
        embed.add_field(name='Server Owner', value=guild.owner, inline=False)
        embed.add_field(name='Total Channels', value=str(
            len(guild.channels)), inline=False)
        embed.add_field(name='Total Users', value=str(
            len(guild.members)), inline=False)
        embed.set_footer(text=f'Requested by {ctx.message.author}')
        embed.colour = 0x738bd7
        await ctx.send(embed=embed)

    @commands.command()
    async def time(self, ctx):
        """
        List current U.S. times by region
        """
        timestamp = self.get_us_timezones()

        embed = discord.Embed()
        embed.add_field(name='U.S. Pacific', value=timestamp['pst'])
        embed.add_field(name='U.S. Central', value=timestamp['cst'])
        embed.add_field(name='U.S. Eastern', value=timestamp['est'])
        embed.set_footer(text=f'Requested by {ctx.message.author}')
        embed.colour = 0x738bd7
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
