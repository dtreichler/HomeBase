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
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    pygame.init()    
    
    hb = HomeBase(config)
    #screen = pygame.display.set_mode(config['screen']['size'])
    papirus = papirus.Papirus()
    logger.info('Initializing HomeBase')
    s = hb.render_text('Loading...')
    s = surface_to_image(s)
    papirus.display(s)
    papirus.update()
    
    #screen.blit(s,(0,0))
    #pygame.display.flip()

    running = True
    last_rendered = None
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
            
#            for event in pygame.event.get():
#                if event.type == pygame.QUIT:
#                    s = hb.render_text('Sucka!')
#                    screen.blit(s,(0,0))
#                    pygame.display.flip()
#                    pygame.quit()
#                    running = False
    except KeyboardInterrupt:
        papirus.clear()
