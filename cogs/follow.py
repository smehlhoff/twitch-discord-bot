import locale
import textwrap

import discord
from discord.ext import commands
from sqlalchemy import exc

from core.models import session, Follows
from core.utils import check_follows_exist, twitch_api_call, twitch_convert_timestamp, twitch_channel_uptime, \
    retrieve_twitch_channel_id, retrieve_twitch_game, retrieve_twitch_channel_name, embed_message


class Follow:
    """
    Bot commands to handle channel follows for twitch.tv
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def follows(self, ctx):
        """
        List followed channels
        """
        user_id = ctx.message.author.id

        if ctx.invoked_subcommand is None:
            follows = check_follows_exist(user_id, channel=None)
            if follows:
                channels = []
                for count, follow in enumerate(follows, start=1):
                    channels.append(f'{count}. {follow.channel}')
                embed = discord.Embed()
                embed.add_field(name='Channel Follows',
                                value=' \n'.join(channels))
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x738bd7
                await ctx.send(embed=embed)
            else:
                await embed_message(ctx, message_type='Error', message='No channels saved in database')

    @follows.command(aliases=['import'])
    async def _import(self, ctx, twitch_username: str):
        """
        Import channel follows from twitch username
        """
        user_id = ctx.message.author.id
        username = ctx.message.author.name
        twitch_user_id = await retrieve_twitch_channel_id(ctx, twitch_username)

        if twitch_user_id:
            data = await twitch_api_call(ctx, endpoint='users/follows?from_id=', channel=twitch_user_id, params='')
            if data:
                objects = []
                for follow in data['data']:
                    channel_id = follow['to_id']
                    channel_name = await retrieve_twitch_channel_name(ctx, channel_id)
                    follows = check_follows_exist(user_id, channel_name)
                    if follows:
                        pass
                    else:
                        objects.append(
                            Follows(
                                user_id=user_id,
                                username=username,
                                channel=channel_name,
                                channel_id=channel_id
                            )
                        )
                if len(objects) == 0:
                    await embed_message(
                        ctx,
                        message_type='Error',
                        message='Channel follows already saved in database'
                    )
                else:
                    try:
                        session.add_all(objects)
                        session.commit()
                        await embed_message(
                            ctx,
                            message_type='Success',
                            message=f'Imported {len(objects)} channel follows to database'
                        )
                    except exc.OperationalError:
                        session.rollback()
                        await embed_message(
                            ctx,
                            message_type='Error',
                            message='Cannot save channel follows to database'
                        )

    @follows.command()
    async def add(self, ctx, *channels: str):
        """
        Add channel follow
        """
        user_id = ctx.message.author.id
        username = ctx.message.author.name

        for channel in channels:
            follows = check_follows_exist(user_id, channel)
            if follows:
                await embed_message(
                    ctx,
                    message_type='Error',
                    message=f'Channel {channel} is already saved in database'
                )
            else:
                channel_id = await retrieve_twitch_channel_id(ctx, channel)
                if channel_id:
                    try:
                        new_follow = Follows(
                            user_id=user_id, username=username, channel=channel, channel_id=channel_id)
                        session.add(new_follow)
                        session.commit()
                        await embed_message(
                            ctx,
                            message_type='Success',
                            message=f'Channel {channel} has been saved to database'
                        )
                    except exc.OperationalError:
                        session.rollback()
                        await embed_message(
                            ctx,
                            message_type='Error',
                            message=f'Cannot save channel {channel} to database'
                        )

    @follows.command()
    async def live(self, ctx):
        """
        List viewer count for live followed channels
        """
        user_id = ctx.message.author.id
        follows = check_follows_exist(user_id, channel=None)

        if follows:
            channels = []
            count = 0
            for follow in follows:
                data = await twitch_api_call(
                    ctx,
                    endpoint='streams?user_id=',
                    channel=follow.channel_id,
                    params='&type=live'
                )
                try:
                    viewers = locale.format(
                        '%d', data['data'][0]['viewer_count'], grouping=True)
                    count += 1
                    channels.append(f'{count}. {follow.channel}')
                    channels.append(viewers)
                except IndexError:
                    pass
            if count == 0:
                await embed_message(ctx, message_type='Error', message='No channels are currently live')
            else:
                embed = discord.Embed()
                embed.add_field(name='Live Channels',
                                value=' \n'.join(channels[0::2]))
                embed.add_field(
                    name='Viewers', value=' \n'.join(channels[1::2]))
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x738bd7
                await ctx.send(embed=embed)
        else:
            await embed_message(ctx, message_type='Error', message='No channels saved in database')

    @follows.command()
    async def uptime(self, ctx):
        """
        List uptime for live followed channels
        """
        user_id = ctx.message.author.id
        follows = check_follows_exist(user_id, channel=None)

        if follows:
            channels = []
            count = 0
            for follow in follows:
                data = await twitch_api_call(
                    ctx,
                    endpoint='streams?user_id=',
                    channel=follow.channel_id,
                    params='&type=live'
                )
                try:
                    uptime = twitch_convert_timestamp(
                        data['data'][0]['started_at'])
                    uptime = twitch_channel_uptime(uptime)
                    count += 1
                    channels.append(f'{count}. {follow.channel}')
                    channels.append(str(uptime))
                except IndexError:
                    pass
            if count == 0:
                await embed_message(ctx, message_type='Error', message='No channels are currently live')
            else:
                embed = discord.Embed()
                embed.add_field(name='Live Channels',
                                value=' \n'.join(channels[0::2]))
                embed.add_field(
                    name='Uptime', value=' \n'.join(channels[1::2]))
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x738bd7
                await ctx.send(embed=embed)
        else:
            await embed_message(ctx, message_type='Error', message='No channels saved in database')

    @follows.command()
    async def game(self, ctx):
        """
        List game title for live followed channels
        """
        user_id = ctx.message.author.id
        follows = check_follows_exist(user_id, channel=None)

        if follows:
            channels = []
            count = 0
            for follow in follows:
                data = await twitch_api_call(
                    ctx,
                    endpoint='streams?user_id=',
                    channel=follow.channel_id,
                    params='&type=live'
                )
                try:
                    game = data['data'][0]['game_id']
                    game = await retrieve_twitch_game(ctx, game)
                    game = textwrap.shorten(game, width=60, placeholder="...")
                    count += 1
                    channels.append(f'{count}. {follow.channel}')
                    channels.append(game)
                except IndexError:
                    pass
            if count == 0:
                await embed_message(ctx, message_type='Error', message='No channels are currently live')
            else:
                embed = discord.Embed()
                embed.add_field(name='Live Channels',
                                value=' \n'.join(channels[0::2]))
                embed.add_field(name='Game', value=' \n'.join(channels[1::2]))
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x738bd7
                await ctx.send(embed=embed)
        else:
            await embed_message(ctx, message_type='Error', message='No channels saved in database')

    @follows.command(aliases=['delete'])
    async def remove(self, ctx, *channels: str):
        """
        Remove channel follows
        """
        user_id = ctx.message.author.id

        for channel in channels:
            follows = check_follows_exist(user_id, channel)
            if follows:
                try:
                    for follow in follows:
                        session.delete(follow)
                        session.commit()
                        await embed_message(
                            ctx,
                            message_type='Success',
                            message=f'Channel {channel} has been removed from database'
                        )
                except exc.OperationalError:
                    session.rollback()
                    await embed_message(
                        ctx,
                        message_type='Error',
                        message=f'Cannot remove channel {channel} in database'
                    )
            else:
                await embed_message(
                    ctx,
                    message_type='Error',
                    message=f'Channel {channel} is not saved in database'
                )

    @follows.command(aliases=['removeall', 'deleteall'])
    async def remove_all(self, ctx):
        """
        Remove all channel follows
        """
        user_id = ctx.message.author.id

        follows = check_follows_exist(user_id, channel=None)

        if follows:
            try:
                for follow in follows:
                    session.delete(follow)
                    session.commit()
                await embed_message(
                    ctx,
                    message_type='Success',
                    message=f'Removed {len(follows)} channel follows from database'
                )
            except exc.OperationalError:
                session.rollback()
                await embed_message(
                    ctx,
                    message_type='Error',
                    message='Cannot remove channel follows in database'
                )
        else:
            return await embed_message(
                ctx,
                message_type='Error',
                message='No channels saved in database'
            )


def setup(bot):
    bot.add_cog(Follow(bot))
