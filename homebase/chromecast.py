import pychromecast
import logging
import time
from datetime import datetime

from .renderer import HomeBaseRenderer
from .server import BaseServer


class ChromecastServer(BaseServer):

    def __init__(self, config, screen_size):
        self._chromecasts = None
        self.logger = logging.getLogger('homebase.chromecast.ChromecastServer')
        self.renderer = HomeBaseRenderer(config['layout'])
        self.screen_size = screen_size
        super(ChromecastServer, self).__init__()

    def run(self):
        while not self.stop_request.isSet():
            if self.any_playing():
                info = self.get_info()
                if info != self.last_info:
                    self.logger.info('New media info: {title} - {artist} - '
                                     '{album} - {source} - {chromecast}'.format(**info))
                    with self.q.mutex:
                        self.q.queue.clear()
                    s = self.create_surface(info)
                    self.logger.debug('New Chromecast surface {}'.format(s.__repr__()))
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
            self.logger.debug('Chromecasts: {}'.format(self._chromecasts.__repr__()))
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
                source = cc.status.display_name
                try:
                    artist = mc.status.artist
                    if artist is None and hasattr(mc.status, 'subtitle'):
                        artist = mc.status.subtitle
                    title = mc.status.title
                    album = mc.status.album_name
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
