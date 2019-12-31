import locale
import textwrap

import discord
from discord.ext import commands

from bot import load_config
from core.utils import twitch_api_call, twitch_convert_timestamp, twitch_channel_uptime, retrieve_twitch_channel_id, \
    retrieve_twitch_game, retrieve_twitch_channel_name, embed_message


class Twitch:
    """
    Bot commands to retrieve twitch.tv API data
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @staticmethod
    async def embed_twitch_message(ctx, description):
        embed = discord.Embed(description=description)
        embed.set_footer(text=f'Requested by {ctx.message.author}')
        embed.colour = 0x9b59b6
        return await ctx.send(embed=embed)

    @commands.command(aliases=['live', 'uptime', 'game'])
    async def stream(self, ctx, *channels: str):
        """
        Return stream information for live channel
        """
        for channel in channels:
            channel_id = await retrieve_twitch_channel_id(ctx, channel)
            if channel_id:
                data = await twitch_api_call(
                    ctx,
                    endpoint='streams?user_id=',
                    channel=channel_id,
                    params='&type=live'
                )
                try:
                    game = data['data'][0]['game_id']
                    game = await retrieve_twitch_game(ctx, game)
                    game = textwrap.shorten(game, width=60, placeholder="...")
                    viewers = locale.format(
                        '%d', data['data'][0]['viewer_count'], grouping=True)
                    uptime = twitch_convert_timestamp(
                        data['data'][0]['started_at'])
                    uptime = twitch_channel_uptime(uptime)
                    embed = discord.Embed()
                    embed.add_field(
                        name='Channel', value=channel.lower(), inline=False)
                    embed.add_field(
                        name='Title', value=data['data'][0]['title'], inline=False)
                    embed.add_field(name='Game', value=game, inline=False)
                    embed.add_field(
                        name='Viewers', value=viewers, inline=False)
                    embed.add_field(name='Uptime', value=uptime, inline=False)
                    embed.add_field(
                        name='URL', value=f'https://www.twitch.tv/{channel.lower()}', inline=False)
                    embed.set_footer(text=f'Requested by {ctx.message.author}')
                    embed.colour = 0x9b59b6
                    await ctx.send(embed=embed)
                except IndexError:
                    await embed_message(ctx, message_type='Info', message=f'Channel {channel} is offline')

    @commands.command()
    async def info(self, ctx, *channels: str):
        """
        Return basic channel information
        """
        for channel in channels:
            channel_id = await retrieve_twitch_channel_id(ctx, channel)
            if channel_id:
                data = await twitch_api_call(ctx, endpoint='users?id=', channel=channel_id, params='')
                views = locale.format(
                    '%d', data['data'][0]['view_count'], grouping=True)
                follows = await twitch_api_call(ctx, endpoint='users/follows?to_id=', channel=channel_id, params='')
                follows = locale.format('%d', follows['total'], grouping=True)
                embed = discord.Embed()
                embed.add_field(
                    name='Channel', value=channel.lower(), inline=False)
                embed.add_field(
                    name='Broadcaster', value=data['data'][0]['broadcaster_type'], inline=False)
                embed.add_field(name='Views', value=views, inline=False)
                embed.add_field(name='Follows', value=follows, inline=False)
                embed.add_field(
                    name='Description', value=data['data'][0]['description'], inline=False)
                embed.add_field(
                    name='URL', value=f'https://www.twitch.tv/{channel.lower()}', inline=False)
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x9b59b6
                await ctx.send(embed=embed)

    @commands.group()
    async def top(self, ctx):
        """
        List top game titles by viewer count
        """
        if ctx.invoked_subcommand is None:
            data = await twitch_api_call(ctx, endpoint='games/top', channel='', params='?first=10')
            games = []

            for count, game in enumerate(data['data'], start=1):
                game = game['name']
                game = textwrap.shorten(game, width=60, placeholder="...")
                games.append(f'{count}. {game}')
            embed = discord.Embed()
            embed.add_field(name='Game', value=' \n'.join(games[0::1]))
            embed.set_footer(text=f'Requested by {ctx.message.author}')
            embed.colour = 0x9b59b6
            await ctx.send(embed=embed)

    @top.command()
    async def channels(self, ctx):
        """
        List top channels by viewer count
        """
        data = await twitch_api_call(ctx, endpoint='streams', channel='', params='?first=10&type=live')
        channels = []

        for count, channel in enumerate(data['data'], start=1):
            channel_id = channel['user_id']
            channel_id = await retrieve_twitch_channel_name(ctx, channel_id)
            viewers = locale.format(
                '%d', channel['viewer_count'], grouping=True)
            channels.append(f'{count}. {channel_id}')
            channels.append(viewers)
        embed = discord.Embed()
        embed.add_field(name='Channel', value=' \n'.join(channels[0::2]))
        embed.add_field(name='Viewers', value=' \n'.join(channels[1::2]))
        embed.set_footer(text=f'Requested by {ctx.message.author}')
        embed.colour = 0x9b59b6
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Twitch(bot))
