from PIL import Image
import pygame


def surface_to_image(s, fmt='RGBA', flipped=False):
    img_str = pygame.image.tostring(s, fmt, flipped)
    img = Image.fromstring(fmt, s.get_size(), img_str)
    return img
