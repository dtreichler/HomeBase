from .chromecast import ChromecastScreen
from .weather import WeatherScreen
from .renderer import HomeBaseRenderer


class HomeBase(object):

    def __init__(self, config):
        self.config = config
        self.screen_size = config['screen']['size']
        self.chromecast_screen = ChromecastScreen(config['chromecast'])
        self.weather_screen = WeatherScreen(config['weather'])
        self.weather_num_days = config['weather']['num_days']
        self.text_renderer = HomeBaseRenderer(config['text']['layout'])

    @property
    def screen_width(self):
        return self.screen_size[0]

    @property
    def screen_height(self):
        return self.screen_size[1]

    def render_text(self, message):
        s = self.text_renderer.render_screen({'message': message}, self.screen_size)
        return s

    def render_chromecast(self):
        s = self.chromecast_screen.create_surface(self.screen_size)
        return s

    def render_weather(self):
        s = self.weather_screen.create_surface(self.screen_size, self.weather_num_days)
        return s

    def any_playing(self):
        return self.chromecast_screen.any_playing()

    def render(self):
        if self.chromecast_screen.any_playing():
            return self.render_chromecast()
        else:
            return self.render_weather()
