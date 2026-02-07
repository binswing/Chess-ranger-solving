import pygame
class Scene:
    def __init__(self, manager):
        self.manager = manager
        self.display_surface = pygame.display.get_surface()

    def update(self, event_list):
        pass

    def draw(self):
        pass