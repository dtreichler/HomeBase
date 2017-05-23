from .homebase import HomeBase

if __name__ == "__main__":
    import pygame
    import time
    import logging
    
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
    screen = pygame.display.set_mode(config['screen']['size'])
    logger.info('Initializing HomeBase')
    s = hb.render_text('Loading...')
    screen.blit(s,(0,0))
    pygame.display.flip()

    running = True
    last_rendered = None
    try:
        while running:                
            if hb.any_playing():
                s = hb.render_chromecast()
                screen.blit(s,(0,0))
                pygame.display.flip()
                last_rendered = 'chromecast'
                time.sleep(1)
            else:
                s = hb.render_weather()
                screen.blit(s,(0,0))
                pygame.display.flip()
                last_rendered = 'weather'
                time.sleep(2)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    s = hb.render_text('Sucka!')
                    screen.blit(s,(0,0))
                    pygame.display.flip()
                    pygame.quit()
                    running = False
    except KeyboardInterrupt:
        pygame.quit()