import pychromecast
import logging

from .renderer import HomeBaseRenderer

class ChromecastScreen(object):
       
    def __init__(self, config):
        self.config = config
        self.renderer = HomeBaseRenderer(config['layout'])
        self._chromecasts = None
        self.logger = logging.getLogger('homebase.chromecast.ChromecastScreen')
        
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
    
    def get_media_info(self):
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

    def create_surface(self, size):        
        media_info = self.get_media_info()
        #print(media_info)
        img = self.renderer.render_screen(media_info,size)
        return img