from src.scenes.scene import Scene
from src.ui.element import *
from settings import *

import pygame
import sys

class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        screen = pygame.display.get_surface()
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        image_url = APP_IMG_URL + "logo.jpg"
        logo_image = pygame.image.load(image_url).convert()
        logo_width, logo_height = logo_image.get_size()

        self.logo_image = Image(APP_IMG_URL + "logo.png", SCREEN_WIDTH // 20, SCREEN_HEIGHT // 12, (logo_width * 3 // 4, logo_height * 3 // 4))
        self.chess_ranger_scene_button = ThemedButton("Chess Ranger Mode", SCREEN_WIDTH // 20 + logo_width * 3 // 8 - 200 , SCREEN_HEIGHT // 12 + logo_height * 3 // 4 - 20 + 100 * 1, 400, 60, font_size = 40, action = lambda: self.manager.switch_scene('puzzle', "ranger"))
        self.chess_melee_scene_button = ThemedButton("Chess Melee Mode", SCREEN_WIDTH // 20 + logo_width * 3 // 8 - 200 , SCREEN_HEIGHT // 12 + logo_height * 3 // 4 - 20 + 100 * 2, 400, 60, font_size = 40, action = lambda: self.manager.switch_scene('puzzle', "melee"))
        self.credit_scene_button = ThemedButton("Credits", SCREEN_WIDTH // 20 + logo_width * 3 // 8 - 200 , SCREEN_HEIGHT // 12 + logo_height * 3 // 4 - 20 + 100 * 3, 400, 60, font_size = 40)
        self.quit_button = ThemedButton("Quit", SCREEN_WIDTH // 20 + logo_width * 3 // 8 - 200 , SCREEN_HEIGHT // 12 + logo_height * 3 // 4 - 20 + 100 * 4, 400, 60, font_size = 40, action = self.quit)

    def update(self, event_list):
        for event in event_list:
            if self.chess_ranger_scene_button.check_click(event):
                print("Switch to Chess Ranger Mode button clicked!")
            elif self.chess_melee_scene_button.check_click(event):
                print("Switch to Chess Melee Mode button clicked!")
            elif self.credit_scene_button.check_click(event):
                print("Switch to Credits button clicked!")
            elif self.quit_button.check_click(event):
                print("Quit button clicked!")
                
    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        self.logo_image.draw(screen)
        self.chess_ranger_scene_button.draw(screen)
        self.chess_melee_scene_button.draw(screen)
        self.credit_scene_button.draw(screen)
        self.quit_button.draw(screen)

    def quit(self):
        pygame.quit()
        sys.exit()