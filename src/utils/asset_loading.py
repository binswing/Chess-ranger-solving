import pygame
import os

from settings import *

# --- Asset Loading ---

def load_images(square_size):
    pieces = ['bb', 'bk', 'bn', 'bp', 'bq', 'br', 
              'wb', 'wk', 'wn', 'wp', 'wq', 'wr']
    images = {}
    for piece in pieces:
        path = os.path.join(PIECES_IMG_URL, piece + ".png")
        try:
            image = pygame.image.load(path).convert_alpha()
            # Smoothscale prevents pixelation when resizing
            images[piece] = pygame.transform.smoothscale(image, (square_size, square_size))
        except FileNotFoundError:
            print(f"Error: Could not find image at {path}")
    return images