from .homebase import HomeBase
from .util import surface_to_image

if __name__ == "__main__":
    import pygame
    import time
    import logging
    from PIL import Image
    import papirus

    from .config import config
    from .renderer import HomeBaseRenderer

    logger = logging.getLogger('homebase')
    logger.setLevel(config['loglevel'])
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    pygame.init()

    hb = HomeBase(config)
    papirus = papirus.Papirus()
    logger.info('Initializing HomeBase')
    s = hb.render_text('Loading...')
    s = surface_to_image(s)
    papirus.display(s)
    papirus.update()

    running = True
    last_rendered = None
    last_chromecast_screen = None

    try:
        while running:
            if hb.any_playing():
                s = hb.render_chromecast()
                s = surface_to_image(s)
                papirus.display(s)
                if last_rendered is 'chromecast':
                    papirus.partial_update()
                else:
                    papirus.update()
                last_rendered = 'chromecast'
                time.sleep(1)
            else:
                s = hb.render_weather()
                s = surface_to_image(s)
                papirus.display(s)
                if last_rendered is 'weather':
                    papirus.partial_update()
                else:
                    papirus.update()
                last_rendered = 'weather'
                time.sleep(2)
    except KeyboardInterrupt:
        papirus.clear()
