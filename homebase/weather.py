from datetime import datetime
import forecastio
import pygame
import math
import logging
import time

from .server import BaseServer
from .renderer import HomeBaseRenderer


class WeatherServer(BaseServer):

    def __init__(self, config, screen_size):
        self.logger = logging.getLogger('homebase.weather.WeatherServer')
        self.screen_size = screen_size

        self.config = config
        self.lat = config['lat']
        self.lon = config['lon']
        self.fio_key = config['forecastio']['api_key']
        self.fio_refresh_interval = config['forecastio']['refresh_interval']
        self.icon_map = config['icon_map']
        self.num_days = config['num_days']

        self.renderer = HomeBaseRenderer(config['layout'])
        self._forecast = None
        self.last_fio_refresh = datetime.fromtimestamp(0)

        super(WeatherServer, self).__init__()

    def run(self):
        while not self.stop_request.isSet():
            info = self.get_info()
            if info != self.last_info:
                self.logger.info('Putting new forecast surface')
                s = self.create_surface(info)
                with self.q.mutex:
                    self.q.queue.clear()
                self.q.put(s)
                self.new_info.set()
                self.last_info = info
                self.last_time = datetime.now()
            time.sleep(0.25)

    @property
    def forecast(self):
        dt = datetime.now() - self.last_fio_refresh
        if self._forecast is None or dt.total_seconds() > self.fio_refresh_interval:
            self.logger.info('Refreshing forecast')
            self._forecast = forecastio.load_forecast(self.fio_key, self.lat, self.lon)
            self.last_fio_refresh = datetime.now()
        return self._forecast

    def get_info(self):
        daily = self.forecast.daily()
        info = []
        for daily_data in daily.data:
            icon = self.icon_map[daily_data.icon]
            temp_max = round(daily_data.temperatureMax)
            temp_max = '{}°'.format(temp_max)
            temp_min = round(daily_data.temperatureMin)
            temp_min = '{}°'.format(temp_min)
            date = daily_data.time.strftime('%b %d')
            info.append({'temp_min': temp_min,
                         'temp_max': temp_max,
                         'date': date,
                         'icon': icon})
        return info

    def create_surface(self, info):
        n = self.num_days
        s_width, s_height = tuple(self.screen_size)
        i_width = math.floor(s_width / self.num_days)
        x_offset = round((s_width - i_width * self.num_days) / 2)

        output_surface = pygame.surface.Surface((s_width, s_height))
        output_surface.fill(pygame.Color('white'))

        weather_info = self.get_info()
        for idx, info in enumerate(weather_info):
            img = self.renderer.render_screen(info, (i_width, s_height))
            img_rect = img.get_rect(topleft=(x_offset + i_width * idx, 0))
            output_surface.blit(img, img_rect)

        return output_surface
