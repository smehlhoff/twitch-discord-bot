import os

import aiohttp
import discord
from discord.ext import commands

from bot import load_config
from core.utils import embed_message


class Weather:
    """
    Bot commands to retrieve weather API data
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    async def weather_api_call(self, ctx, endpoint, zip_code):
        async with aiohttp.ClientSession() as session:
            api_key = self.config['wunderground']['key']
            url = f'http://api.wunderground.com/api/{api_key}/{endpoint}/q/{zip_code}.json'
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

                if resp.status == 200:
                    return data
                elif aiohttp.ServerTimeoutError:
                    await embed_message(ctx, message_type='Error', message='Connection Timeout')
                else:
                    await embed_message(ctx, message_type='Error', message='Unexpected Error')
                return None

    @commands.command()
    async def wx(self, ctx, zip_code: int):
        """
        Return current weather conditions
        """
        data = await self.weather_api_call(ctx, endpoint='conditions', zip_code=zip_code)

        try:
            embed = discord.Embed()
            embed.add_field(
                name='City', value=data['current_observation']['display_location']['full'], inline=False)
            embed.add_field(
                name='Weather', value=data['current_observation']['weather'], inline=False)
            embed.add_field(
                name='Temp', value=data['current_observation']['temperature_string'], inline=False)
            embed.add_field(
                name='Wind', value=data['current_observation']['wind_string'], inline=False)
            embed.add_field(
                name='Humidity', value=data['current_observation']['relative_humidity'], inline=False)
            embed.add_field(
                name='Rain', value=data['current_observation']['precip_today_string'], inline=False)
            embed.set_footer(text=f'Requested by {ctx.message.author}')
            embed.colour = 0x738bd7
            await ctx.send(embed=embed)
        except KeyError:
            await embed_message(ctx, message_type='Error', message='Zip code is invalid')

    @commands.command()
    async def forecast(self, ctx, zip_code: int):
        """
        Return three day weather forecast
        """
        data = await self.weather_api_call(ctx, endpoint='forecast', zip_code=zip_code)

        try:
            embed = discord.Embed()
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][0]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][0]['fcttext'],
                inline=False
            )
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][1]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][1]['fcttext'],
                inline=False
            )
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][2]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][2]['fcttext'],
                inline=False
            )
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][3]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][3]['fcttext'],
                inline=False
            )
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][4]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][4]['fcttext'],
                inline=False
            )
            embed.add_field(
                name=data['forecast']['txt_forecast']['forecastday'][5]['title'],
                value=data['forecast']['txt_forecast']['forecastday'][5]['fcttext'],
                inline=False
            )
            embed.set_footer(text=f'Requested by {ctx.message.author}')
            embed.colour = 0x738bd7
            await ctx.send(embed=embed)
        except KeyError:
            await embed_message(ctx, message_type='Error', message='Zip code is invalid')

    @commands.command()
    async def radar(self, ctx, zip_code: int):
        """
        Display static radar image
        """
        try:
            data = await self.weather_api_call(ctx, endpoint='conditions', zip_code=zip_code)
            if data['current_observation']['display_location']['zip'] == str(zip_code):
                async with aiohttp.ClientSession() as session:
                    api_key = self.config['wunderground']['key']
                    url = f'http://api.wunderground.com/api/' \
                          f'{api_key}/radar/q/{zip_code}.png?newmaps=1&smooth=1&noclutter=1'
                    async with session.get(url, timeout=60) as resp:
                        if resp.status == 200:
                            radar_image = f'{zip_code}_radar.png'
                            with open(radar_image, 'wb') as f:
                                while True:
                                    chunk = await resp.content.read()
                                    if not chunk:
                                        break
                                    f.write(chunk)
                                    await ctx.send(file=discord.File(radar_image))
                            os.remove(radar_image)
                        elif aiohttp.ServerTimeoutError:
                            await embed_message(ctx, message_type='Error', message='Connection Timeout')
                        else:
                            await embed_message(ctx, message_type='Error', message='Unexpected Error')
                        return None
        except KeyError:
            await embed_message(ctx, message_type='Error', message='Zip code is invalid')

    @commands.command()
    async def alerts(self, ctx, zip_code: int):
        """
        Return current weather alerts
        """
        data = await self.weather_api_call(ctx, endpoint='alerts', zip_code=zip_code)

        try:
            alerts = []
            count = 0
            for alert in data['alerts']:
                count += 1
                alert_description = alert['description']
                alerts.append(f'{count}. {alert_description}')
            if count == 0:
                await embed_message(ctx, message_type='Info', message='No active weather alerts')
            else:
                embed = discord.Embed()
                embed.add_field(name='Active Weather Alerts',
                                value=' \n'.join(alerts))
                embed.set_footer(text=f'Requested by {ctx.message.author}')
                embed.colour = 0x738bd7
                await ctx.send(embed=embed)
        except KeyError:
            await embed_message(ctx, message_type='Error', message='Zip code is invalid')


def setup(bot):
    bot.add_cog(Weather(bot))
