import threading
import queue
from datetime import datetime
import logging
import pychromecast
import forecastio
import pygame
import math
import time

from .config import config
from .renderer import HomeBaseRenderer


class BaseServer(threading.Thread):

    def __init__(self):
        super(BaseServer, self).__init__()
        self.q = queue.Queue()

        self.stop_request = threading.Event()
        self.new_info = threading.Event()

        self.last_info = None
        self.last_time = datetime.fromtimestamp(0)

    def join(self, timeout=None):
        self.stop_request.set()
        super(BaseServer, self).join(timeout)


class ChromecastServer(BaseServer):

    def __init__(self, config, screen_size):
        self._chromecasts = None
        self.logger = logging.getLogger('homebase.threads.ChromecastServer')
        self.renderer = HomeBaseRenderer(config['layout'])
        self.screen_size = screen_size
        super(ChromecastServer, self).__init__()

    def run(self):
        while not self.stop_request.isSet():
            if self.any_playing():
                info = self.get_info()
                if info != self.last_info:
                    self.logger.info('Putting new Chromecast surface')
                    with self.q.mutex:
                        self.q.queue.clear()
                    s = self.create_surface(info)
                    self.q.put(s)
                    self.new_info.set()
                    self.last_info = info
                    self.last_time = datetime.now()
            time.sleep(0.25)

    @property
    def chromecasts(self):
        if self._chromecasts is None:
            self.logger.info('Initializing Chromecasts')
            self._chromecasts = pychromecast.get_chromecasts()
        return self._chromecasts

    def any_playing(self):
        for cc in self.chromecasts:
            mc = cc.media_controller
            if mc.is_playing:
                return True
        return False

    def get_info(self):
        for cc in self.chromecasts:
            mc = cc.media_controller
            if mc.is_playing:
                try:
                    artist = mc.status.artist
                    title = mc.status.title
                    album = mc.status.album_name
                    source = cc.status.display_name
                    info = {'artist': ' ' if artist is None else ' ' + artist,
                            'title': ' ' if title is None else ' ' + title,
                            'album': ' ' if album is None else ' ' + album,
                            'chromecast': cc.name,
                            'source': ' ' if source is None else ' ' + source}
                    return info
                except:
                    self.logger.warning('Caught an error with source %s'.format(source))
                    info = {'artist': 'Check logs',
                            'title': 'Encountered an Error',
                            'album': '',
                            'chromecast': cc.name,
                            'source': source}
                    return info
        info = {'artist': '',
                'title': 'Nothing is Playing',
                'album': '',
                'chromecast': '',
                'source': ''}
        return info

    def create_surface(self, info):
        img = self.renderer.render_screen(info, self.screen_size)
        return img


class WeatherServer(BaseServer):

    def __init__(self, config, screen_size):
        self.logger = logging.getLogger('homebase.threads.WeatherServer')
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
