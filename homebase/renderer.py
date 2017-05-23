import pygame
import copy
import logging

class HomeBaseRenderer(object):
    
    def __init__(self, layout):
        self.layout = layout
        self.logger = logging.getLogger('homebase.renderer.HomeBaseRenderer')

    def render_screen(self,info,size):
        s_width, s_height = size

        # Initialize a surface the size of our output
        s = pygame.surface.Surface(size)
        s.fill(pygame.Color('white'))
        # Loop over all of the layout items
        for name, fmt in self.layout.items():
            #print(name)
           
            # Make a deep copy so we can transform from normalized
            # space into pixel space
            pos = copy.deepcopy(fmt['pos'])
            
            k = pos.keys()
            
            # Normalize, multiplying width options by width, height options 
            # by height and size options by both
            w_opts = ('x','left','right','centerx')
            for o in w_opts:
                if o in k:
                    #print(o,pos[o])
                    v = round(pos[o]*s_width)
                    #print(o,v)
                    pos[o] = v
            
            h_opts = ('y','top','bottom','centery')
            for o in h_opts:
                if o in k:
                    #print(o,pos[o])
                    v = round(pos[o]*s_height)
                    #print(o,v)
                    pos[o] = v
            
            opts = ('topleft','bottomleft','topright','bottomright',
                    'midtop','midleft','midbottom','midright',
                    'center')
            for o in opts:
                if o in k:
                    #print(o,pos[o])
                    v = (round(pos[o][0]*s_width), round(pos[o][1]*s_height))
                    #print(o,v)
                    pos[o] = v
            
            # Normalize the image size too
            sz = copy.deepcopy(fmt['size'])
            sz = (sz[0]*s_width,sz[1]*s_height)
            
            # Now we can do the actual formatting
            # First, set the font
            fontface = fmt['font']
            if 'fontsize' in fmt.keys():
                self.logger.debug('Using font size from config for {}'.format(name))
                fontsize = round(fmt['fontsize']*sz[1])
                try:
                    font = pygame.font.Font(fontface, fontsize)
                except OSError:
                    font = pygame.font.Font(pygame.font.match_font(fontface), fontsize)
            else:
                # Now guess how big the font can be and fix if necessary
                self.logger.debug('Choosing a font size for {}'.format(name))
                if 'maxfontsize' in fmt.keys():
                    maxfontsize = round(fmt['maxfontsize']*sz[1])
                else:
                    maxfontsize = 10000
                fontsize = min(round(sz[1]), maxfontsize)
                max_w = 0.9
                while True:
                    # The font can be given as a system name or as a file. 
                    # Assume a file and fall back
                    try:
                        font = pygame.font.Font(fontface, fontsize)
                    except OSError:
                        font = pygame.font.Font(pygame.font.match_font(fontface), fontsize)
                    #print(fontface,fontsize,font)
                    textsize = font.size(info[name])
                    if textsize[0] > max_w*sz[0]:
                        oldfontsize = fontsize
                        fontsize = round(max_w*oldfontsize*sz[0]/textsize[0])
                        if fontsize == oldfontsize:
                            fontsize -= 1
                    else:
                        break
                self.logger.debug('Using font size {} for {}'.format(fontsize,name))
            #print(fontface,fontsize,font)
            # Set foreground and background colors
            bg = pygame.Color(fmt['bg'])
            fg = pygame.Color(fmt['fg'])
                        
            # Size up and fill the background surface, blit it onto the output
            ss = pygame.surface.Surface(sz)
            ss.fill(bg)
            r = ss.get_rect(**pos)
            s.blit(ss,r)
            
            # Render the font with a transparent bg, blit it
            f = font.render(info[name],True,fg)
            #print(pos)
            r = f.get_rect(**pos)
            #r.size = sz
            
            #print(r)
            #print(r.center)
            s.blit(f, r)
            #print('\n')
        return s        
