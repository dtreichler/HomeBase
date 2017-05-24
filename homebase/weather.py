import datetime
import forecastio
import pygame
import math
import logging

from .renderer import HomeBaseRenderer


class WeatherScreen(object):

    def __init__(self, config):
        self.config = config
        self.lat = config['lat']
        self.lon = config['lon']
        self.fio_key = config['forecastio']['api_key']
        self.fio_refresh_interval = config['forecastio']['refresh_interval']
        self.icon_map = config['icon_map']

        self.renderer = HomeBaseRenderer(config['layout'])

        self._forecast = None
        self.last_fio_refresh = datetime.datetime.now()

        self.last_screen_refresh = datetime.datetime(2000, 1, 1)

        self.logger = logging.getLogger('homebase.weather.WeatherScreen')

    @property
    def forecast(self):
        dt = datetime.datetime.now() - self.last_fio_refresh
        if self._forecast is None or dt.total_seconds() > self.fio_refresh_interval:
            self.logger.info('Refreshing forecast')
            self._forecast = forecastio.load_forecast(self.fio_key, self.lat, self.lon)
            self.last_fio_refresh = datetime.datetime.now()
        return self._forecast

    def get_forecast_info(self):
        daily = self.forecast.daily()
        for daily_data in daily.data:
            icon = self.icon_map[daily_data.icon]
            temp_max = round(daily_data.temperatureMax)
            temp_max = '{}°'.format(temp_max)
            temp_min = round(daily_data.temperatureMin)
            temp_min = '{}°'.format(temp_min)
            date = daily_data.time.strftime('%b %d')
            info = {'temp_min': temp_min,
                    'temp_max': temp_max,
                    'date': date,
                    'icon': icon}
            yield info

    def create_surface(self, size, n=4):
        s_width, s_height = size
        i_width = math.floor(s_width / n)
        x_offset = round((s_width - i_width * n) / 2)

        output_surface = pygame.surface.Surface((s_width, s_height))
        output_surface.fill(pygame.Color('white'))

        weather_info = self.get_forecast_info()
        for idx, info in enumerate(weather_info):
            img = self.renderer.render_screen(info, (i_width, s_height))
            img_rect = img.get_rect(topleft=(x_offset + i_width * idx, 0))
            output_surface.blit(img, img_rect)

        return output_surface
