import pygame
import os
import json

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

def get_puzzle_limits(mode):
    """
    Reads the puzzle_map.json for the given mode to find min/max pieces.
    Returns (min_pieces, max_pieces).
    """
    try:
        path = DATA_URL + f'chess_{mode}/puzzle_map.json'
        if not os.path.exists(path):
            return 1, 1
            
        with open(path) as json_data:
            data = json.load(json_data)
            keys = list(map(lambda x: int(x), data.keys()))
            
            if not keys:
                return 1, 1
                
            return min(keys), max(keys)
    except Exception as e:
        print(f"Error loading limits for {mode}: {e}")
        return 1, 1