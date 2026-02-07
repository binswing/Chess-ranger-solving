from src.scenes.scene import Scene
import pygame

class MenuScene(Scene):
    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    print("Switching to Puzzle...")
                    self.manager.switch_scene('puzzle')

    def draw(self):
        self.display_surface.fill('black')