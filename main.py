import pygame
import os
import ctypes
import sys

from settings import *
from src.scene_manager import SceneManager
# --- PREVENT STRETCHING/BLURRING (Windows Fix) ---
# This tells the OS to disable auto-scaling so the game runs at true 1:1 resolution.
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass # Ignore if on Mac/Linux

class ChessPuzzleEnv:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Chess Puzzle")
        self.clock = pygame.time.Clock()
        self.scene_manager = SceneManager() # The brain

    def run(self):
        while True:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.scene_manager.run(event_list)
            
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = ChessPuzzleEnv()
    game.run()