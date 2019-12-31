from datetime import datetime, timedelta

import aiohttp
import discord
from dateutil import parser
from pytz import timezone
from sqlalchemy import asc

from bot import load_config
from .models import session, Follows

config = load_config()


async def twitch_api_call(ctx, endpoint, channel, params):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.twitch.tv/helix/{endpoint}{channel}{params}'
        headers = {
            'Authorization': 'Bearer ' + config['twitch']['token']
        }
        async with session.get(url, headers=headers, timeout=60) as resp:
            data = await resp.json()
            error_codes = [400, 401, 403, 404, 422, 429, 500, 503]

            if resp.status == 200:
                return data
            elif resp.status in error_codes:
                await embed_message(ctx, message_type='Error', message=data['error'])
            elif aiohttp.ServerTimeoutError:
                await embed_message(ctx, message_type='Error', message='Connection Timeout')
            else:
                await embed_message(ctx, message_type='Error', message='Unexpected Error')
            return None


# async def generate_new_twitch_token():
#     async with aiohttp.ClientSession as session:
#         client_id = config['twitch']['client_id']
#         client_secret = config['twitch']['client_secret']
#         url = f'https://id.twitch.tv/oauth2/' \
#               f'token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
#         async with session.post(url, timeout=60) as resp:
#             data = await resp.json()
#             return data['access_token']


async def retrieve_twitch_channel_id(ctx, channel_name):
    data = await twitch_api_call(ctx, endpoint='users?login=', channel=channel_name, params='')

    if len(data['data']) == 1:
        channel = data['data'][0]['id']
        return channel
    else:
        await embed_message(ctx, message_type='Error', message=f'Channel {channel_name} does not exist')


async def retrieve_twitch_channel_name(ctx, channel_id):
    data = await twitch_api_call(ctx, endpoint='users?id=', channel=channel_id, params='')
    return data['data'][0]['login']


async def retrieve_twitch_game(ctx, game_id):
    data = await twitch_api_call(ctx, endpoint='games?id=', channel='', params=game_id)

    if len(data['data']) == 1:
        game = data['data'][0]['name']
        return game
    else:
        await embed_message(ctx, message_type='Error', message=f'Game title does not exist')


async def embed_message(ctx, message_type, message):
    embed = discord.Embed(title=message_type, description=message)
    if message_type == 'Success':
        embed.colour = 0x2ecc71
    elif message_type == 'Error':
        embed.colour = 0xe74c3c
    elif message_type == 'Info':
        embed.colour = 0x738bd7
    embed.set_footer(text=f'Requested by {ctx.message.author}')
    return await ctx.send(embed=embed)


def check_follows_exist(user_id, channel):
    if channel is None:
        follows = session.query(Follows).filter(
            Follows.user_id == user_id).order_by(asc(Follows.channel)).all()
    else:
        follows = session.query(Follows).filter(
            Follows.user_id == user_id, Follows.channel == channel).all()
    return follows


def twitch_convert_timestamp(timestamp):
    ts = parser.parse(timestamp)
    ts = ts.astimezone(timezone('UTC'))
    return ts


def twitch_channel_uptime(timestamp):
    now = datetime.now(timezone('UTC'))
    ts = now - timestamp
    ts = timedelta(seconds=ts.seconds)
    return ts
