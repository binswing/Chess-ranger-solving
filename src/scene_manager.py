import pygame
from src.scenes.scene import Scene
from src.scenes.menu import MenuScene
from src.scenes.puzzle import PuzzleScene
from src.scenes.map_creator import MapCreatorScene

SCENES: dict[str, type[Scene]]= {
    'menu': MenuScene,
    'puzzle': PuzzleScene,
    'creator': MapCreatorScene
}

class SceneManager:
    def __init__(self):
        # Start with the menu
        self.active_scene = MenuScene(self) 

    def switch_scene(self, scene_name, *args, **kwargs):
        """Logic to handle scene transitions"""
        if scene_name in SCENES:
            self.active_scene = SCENES[scene_name](self, *args, **kwargs)

    def run(self, event_list):
        """Delegates the loop to the active scene"""
        self.active_scene.update(event_list)
        self.active_scene.draw()