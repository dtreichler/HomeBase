import logging
import papirus

from .chromecast import ChromecastServer
from .weather import WeatherServer
from .renderer import HomeBaseRenderer
from .util import surface_to_image


class HomeBase(object):

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('homebase.homebase.HomeBase')
        self.screen_size = config['screen']['size']
        self.chromecast_server = ChromecastServer(config['chromecast'], self.screen_size)
        self.weather_server = WeatherServer(config['weather'], self.screen_size)
        self.text_renderer = HomeBaseRenderer(config['text']['layout'])
        self._p = papirus.Papirus()

        self.weather_surface = None
        self.new_weather = False
        self.chromecast_surface = None
        self.new_chromecast = False

        self._p.clear()
        self.chromecast_server.start()
        self.weather_server.start()

    @property
    def screen_width(self):
        return self.screen_size[0]

    @property
    def screen_height(self):
        return self.screen_size[1]

    def is_idle(self):
        return True

    def display(self, s, partial=False):
        self._p.display(surface_to_image(s))
        if partial:
            self._p.partial_update()
        else:
            self._p.update()

    def display_text(self, message):
        s = self.text_renderer.render_screen({'message': message}, self.screen_size)
        self.display(s)

    def run(self):
        self.display_text('Starting...')
        last_displayed = None
        while True:
            try:
                if self.weather_server.new_info.isSet():
                    self.weather_surface = self.weather_server.q.get()
                    self.weather_server.new_info.clear()
                    self.new_weather = True
                else:
                    self.new_weather = False

                if self.chromecast_server.new_info.isSet():
                    self.chromecast_surface = self.chromecast_server.q.get()
                    self.chromecast_server.new_info.clear()
                    self.new_chromecast = True
                else:
                    self.new_chromecast = False

                if self.is_idle():
                    if self.chromecast_server.any_playing() and self.chromecast_surface is not None:
                        if last_displayed is 'chromecast' and self.new_chromecast:
                            self.display(self.chromecast_surface, True)
                            last_displayed = 'chromecast'
                        elif last_displayed is 'weather':
                            self.display(self.chromecast_surface)
                            last_displayed = 'chromecast'
                    else:
                        if last_displayed is not 'weather' or self.new_weather:
                            self.display(self.weather_surface)
                            last_displayed = 'weather'
            except:
                self.display_text('Stopped')
                break
