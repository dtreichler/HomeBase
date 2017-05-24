from .homebase import HomeBase

if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((200, 96))
    hb = HomeBase(screen.get_size(), cc_layout, ws_layout, (lat, lon), 4)
    n = 0
    try:
        while True:
            if hb.any_playing():
                s = hb.render_chromecast()
                screen.blit(s, (0, 0))
                pygame.display.flip()
                time.sleep(1)
            else:
                s = hb.render_weather()
                screen.blit(s, (0, 0))
                pygame.display.flip()
                time.sleep(2)
    except KeyboardInterrupt:
        pygame.quit()
