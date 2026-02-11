import pygame
import copy

from src.entities.chess import ChessPuzzle
from src.algorithms.algorithm import ChessSolver
from src.algorithms.Astar import AStarSolver
from src.algorithms.BFS import BFSSolver
from src.algorithms.DFS import DFSSolver
from src.scenes.scene import Scene
from src.ui.element import *

ALGORITHMS: dict[str, type[ChessSolver]]= {
    "A*": AStarSolver,
    "BFS": BFSSolver,
    "DFS": DFSSolver
}

class AlgorithmHandler:
    def __init__(self, scene):
        self.scene = scene
        self.logic = scene.logic

        self.panel_width = scene.SCREEN_WIDTH // 5
        self.base_x = scene.SCREEN_WIDTH - self.panel_width - 50 
        self.start_y = scene.MARGIN + scene.SCREEN_HEIGHT // 8 + 10
        self.gap = 10

        self.stats_panels = {
            "A*": StatsPanel(self.base_x, 0, self.panel_width, 25, ["A* Status"]),
            "BFS": StatsPanel(self.base_x, 0, self.panel_width, 25, ["BFS Status"]),
            "DFS": StatsPanel(self.base_x, 0, self.panel_width, 25, ["DFS Status"])
        }
        
        self.active_algorithm_name = None  
        self.iterator = None
        self.solutions = {"A*": None, "BFS": None, "DFS": None}

    def start_search(self, algorithm_name):
        print(f"Starting {algorithm_name} search...")
        self.solutions[algorithm_name] = None
        self.active_algorithm_name = algorithm_name
        self.scene.game_won = False
        self.scene.is_playing_solution = False
        self.scene.playback_queue = []

        self.stats_panels[algorithm_name].update_stats(status="Starting...", nodes=0, path=[])
        
        algorithm_class = ALGORITHMS[algorithm_name]
        self.iterator = self.logic.solver_iterator(self.scene, algorithm_class)

    def update(self):
        if not self.iterator or self.scene.animating:
            return

        try:
            status, data = next(self.iterator)
            panel = self.stats_panels[self.active_algorithm_name]
            
            if status == "running":
                panel.update_stats(nodes=data, status="Searching...")
            
            elif status == "finished":
                self.solutions[self.active_algorithm_name] = data
                panel.update_stats(path=copy.deepcopy(data.get_final_path()), status="Solved!")
                self.iterator = None 
                self.active_algorithm_name = None 
            
            elif status == "failed":
                panel.update_stats(status="No Path")
                self.iterator = None
                self.active_algorithm_name = None
            
            elif status == "error":
                panel.update_stats(status="Error")
                self.iterator = None
                self.active_algorithm_name = None
                
        except StopIteration:
            self.iterator = None
            self.active_algorithm_name = None

    def draw(self, screen):
        """
        Draws panels and dynamically updates their Y positions 
        so they stack neatly.
        """
        current_y = self.start_y
        order = ["A*", "BFS", "DFS"]  
        for name in order:
            panel = self.stats_panels[name]
            panel.rect.y = current_y
            panel.draw(screen)
            current_y += panel.rect.height + self.gap

    def has_solution(self, algorithm_name):
        solver = self.solutions.get(algorithm_name)
        return solver is not None and len(solver.get_final_path()) > 0

    def get_solution_path(self, algorithm_name):
        return self.solutions[algorithm_name].get_final_path()
    
    def reset(self):
        self.iterator = None
        self.active_algorithm_name = None
        for name in self.solutions:
            self.solutions[name] = None
            self.stats_panels[name].update_stats(status="Ready", nodes=0, path=[])