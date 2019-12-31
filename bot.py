import asyncio
import json
import locale
import logging
from datetime import datetime
from sys import platform

from discord.ext import commands

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def load_config():
    return json.loads(open('config.json').read())


def load_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename='bot.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


cogs = [
    'cogs.admin',
    'cogs.follow',
    'cogs.general',
    'cogs.twitch',
    'cogs.weather'
]


def main():
    config = load_config()
    load_logging()

    if platform == 'win32':
        locale.setlocale(locale.LC_ALL, 'US')
    else:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    if config['bot']['debug'] is True:
        command_prefix = '?'
    else:
        command_prefix = '!'

    description = 'A discord bot to retrieve twitch.tv API data'
    bot = commands.Bot(command_prefix=command_prefix, description=description)

    @bot.event
    async def on_ready():
        print('Connected to server...')
        print(f'Username: {bot.user.name}')
        print(f'ID: {bot.user.id}')
        print('----------------------')

        if not hasattr(bot, 'bot_uptime'):
            bot.bot_uptime = datetime.utcnow()

        for cog in cogs:
            try:
                bot.load_extension(cog)
            except Exception as e:
                print(f'Failed to load {cog}\n{type(type(e).__name__)}: {e}')

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        await bot.process_commands(message)

    bot.loop.set_debug(config['bot']['debug'])
    bot.run(config['discord']['key'])


if __name__ == '__main__':
    main()
