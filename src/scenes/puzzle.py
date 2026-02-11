import pygame
import json
import random
import time
import copy

from src.scenes.scene import Scene
# from src.logic import GameLogic  # Your existing logic class!
from settings import *
from src.utils.asset_loading import load_images
from src.ui.element import *
from src.entities.chess import ChessRangerPuzzle
from src.algorithms.Astar import AStarSolver
with open(DATA_URL + 'chess_ranger/puzzle_map.json') as json_data:
    num_pieces_list = list(map(lambda x: int(x), json.load(json_data).keys()))
    json_data.close()
MIN_NUM_PIECES = min(num_pieces_list)
MAX_NUM_PIECES = max(num_pieces_list)

class PuzzleLogic:
    def __init__(self, square_size, board_layout: list[list[int]] | None = None):
        self.puzzle = ChessRangerPuzzle(board_layout)
        self.initial_board_layout = self.puzzle.get_state()
        self.images = load_images(square_size)
        self.current_num_of_pieces = self.puzzle.board.count_pieces()
    
    def step(self, action: tuple[int, int, int, int]):
        return self.puzzle.step(action)
    
    def change_num_of_pieces(self, num: int) -> bool:
        if num < MIN_NUM_PIECES or num > MAX_NUM_PIECES:
            return False
        self.current_num_of_pieces = num
        with open(DATA_URL + 'chess_ranger/puzzle_map.json') as json_data:
            map_list = json.load(json_data)[str(num)]
            json_data.close()
        new_map = self.puzzle.board.export_board()
        while new_map == self.puzzle.board.export_board():
            new_map = random.choice(map_list)
        self.puzzle.reset(new_map)
        self.initial_board_layout = new_map
        return True

    def change_map(self):
        with open(DATA_URL + 'chess_ranger/puzzle_map.json') as json_data:
            map_list = json.load(json_data)[str(self.current_num_of_pieces)]
            json_data.close()
        new_map = self.puzzle.board.export_board()
        if len(map_list) == 1 and map_list[0] == new_map:
            return
        while new_map == self.puzzle.board.export_board():
            new_map = random.choice(map_list)
        self.puzzle.reset(new_map)
        self.initial_board_layout = copy.deepcopy(new_map)

    def reset(self):
        self.puzzle.reset(self.initial_board_layout)

    def A_star(self, scene):
        """
        Runs the A* Search to find the solution path.
        Returns: List of moves [(r1, c1, r2, c2), ...]
        """
        temp_env = ChessRangerPuzzle(self.puzzle.get_state())
        solver = AStarSolver(temp_env)
        iterations = 0
        
        while True:
            state, move = solver.take_action()
            
            # FINISHED?
            if state is None and move is None:
                break
            
            # VISUALIZE
            self.puzzle.set_state(state)
            scene.trigger_move((move[0], move[1]), (move[2], move[3]))
            
            iterations += 1
            if iterations > 10000:
                yield ("error", "Timeout") # Send error status
                break
            
            # YIELD PROGRESS: Send ("running", iterations)
            yield ("running", iterations) 

        # DONE
        self.reset()
        if solver.solution_found:
            path = solver.get_final_path()
            # Send ("finished", path)
            yield ("finished", solver)
        else:
            yield ("failed", [])

    def get_image(self, piece: str):
        return self.images[piece]
    
    def get_board(self):
        return self.puzzle.export_board_string()

    def get_num_of_pieces(self) -> int:
        return self.current_num_of_pieces
        
class PuzzleScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.update_screen()

        self.drag_piece = None
        self.drag_origin = None
        self.dragging = False
        self.mouse_pos = (0, 0)
        self.logic = PuzzleLogic(self.SQUARE_SIZE)

        self.animating = False
        self.anim_piece = None      
        self.anim_start_pos = None  
        self.anim_end_pos = None
        self.final_move_data = (0,0,0,0)  
        self.anim_start_time = 0
        self.ANIMATION_DURATION = 250 
        self.current_anim_pos = pygame.math.Vector2(0, 0)
        self.solver_iterator = None

        self.return_image = ClickableImage(APP_IMG_URL + "return.png", self.SCREEN_WIDTH // 32, self.MARGIN, (self.SCREEN_WIDTH // 32, self.SCREEN_WIDTH // 32), action = lambda: self.manager.switch_scene('menu'))

        with open(DATA_URL + 'puzzle_info.json') as json_data:
            rules = json.load(json_data)["chess_ranger"]["rules"]
        
        self.num_of_pieces_selector = NumberSelector(
            self.SCREEN_WIDTH // 40, 
            self.MARGIN + self.SCREEN_HEIGHT // 8 + 20, 
            MIN_NUM_PIECES, 
            MAX_NUM_PIECES, 
            self.logic.get_num_of_pieces(), 
            APP_IMG_URL + "left-arrow.png", 
            APP_IMG_URL + "right-arrow.png", 
            lambda x: self.logic.change_num_of_pieces(x), 
            lambda x: self.logic.change_num_of_pieces(x)
        )
        self.change_map_button = ThemedButton(
            "Change Map", 
            self.LEFT_MARGIN // 2 - self.SCREEN_WIDTH // 10, 
            self.MARGIN + self.SCREEN_HEIGHT // 8 + 20 + 20 + 80 * 1, 
            self.SCREEN_WIDTH // 5, 60, 
            font_size = 40, 
            action = self.handle_change_map
        )
        self.reset_button = ThemedButton("Reset", 
            self.LEFT_MARGIN // 2  - self.SCREEN_WIDTH // 10, 
            self.MARGIN + self.SCREEN_HEIGHT // 8 + 20 + 20 + 80 * 2, 
            self.SCREEN_WIDTH // 5, 60, 
            font_size = 40, 
            action = self.handle_reset
        )
        self.A_star_solve_button = ThemedButton(
            "A* Solve", 
            self.LEFT_MARGIN // 2 - self.SCREEN_WIDTH // 10, 
            self.MARGIN + self.SCREEN_HEIGHT // 8 + 20 + 20 + 80 * 3, 
            self.SCREEN_WIDTH // 5, 60, 
            font_size = 40, 
            action = self.start_visual_search
        )
        self.play_solution_btn = ThemedButton(
            "Play Solution - A*", 
            self.LEFT_MARGIN // 2 - self.SCREEN_WIDTH // 10, 
            self.MARGIN + self.SCREEN_HEIGHT // 8 + 20 + 20 + 80 * 4, 
            self.SCREEN_WIDTH // 5, 60, font_size=40, 
            action=self.start_solution_playback
        )
        
        self.rule_box = RuleBox(self.SCREEN_WIDTH - self.SCREEN_WIDTH // 40 - self.SCREEN_WIDTH // 5, self.MARGIN * 2, self.SCREEN_WIDTH // 5, self.SCREEN_HEIGHT // 8, rules)
        self.stats_panel = StatsPanel(self.SCREEN_WIDTH - self.SCREEN_WIDTH // 40 - self.SCREEN_WIDTH // 5, self.MARGIN * 2 + self.SCREEN_HEIGHT // 8, self.SCREEN_WIDTH // 5, self.SCREEN_HEIGHT // 8, 35, ["A* Solver result"])
        self.A_star_solver = None
        self.is_playing_solution = False
        self.playback_queue = []

    def update_screen(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = 50 
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.LEFT_MARGIN = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        
        # Center the board
        self.BOARD_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        
    def update(self, event_list):
        self.update_screen()
        self.mouse_pos = pygame.mouse.get_pos()

        if self.animating:
            current_time = pygame.time.get_ticks()
            time_passed = current_time - self.anim_start_time
            progress = time_passed / self.ANIMATION_DURATION

            if progress >= 1.0:
                self.animating = False
                r1, c1, r2, c2 = self.final_move_data 
                self.logic.step((r1, c1, r2, c2)) 
            else:
                self.current_anim_pos = self.anim_start_pos.lerp(self.anim_end_pos, progress)

        if self.solver_iterator:
            if not self.animating: 
                try:
                    status, data = next(self.solver_iterator)
                    if status == "running":
                        self.stats_panel.update_stats(nodes=data, status="Searching...")
                    elif status == "finished":
                        self.A_star_solver = data
                        path_len = len(data.get_final_path())
                        self.stats_panel.update_stats(length=path_len, status="Solved!")
                        print(f"Path found: {path_len} steps")
                        self.solver_iterator = None 
                    elif status == "failed":
                        self.stats_panel.update_stats(status="No Path")
                        self.solver_iterator = None
                except StopIteration:
                    self.solver_iterator = None
                    
        if self.is_playing_solution and not self.animating:
            if self.playback_queue:
                next_move = self.playback_queue.pop(0)
                self.trigger_move((next_move[0], next_move[1]), (next_move[2], next_move[3]))
            else:
                self.is_playing_solution = False

        for event in event_list:
            if self.animating: 
                continue 

            if self.A_star_solver and self.play_solution_btn.check_click(event):
                pass
            if self.return_image.check_click(event):
                pass
            elif self.change_map_button.check_click(event):
                pass 
            elif self.reset_button.check_click(event):
                pass
            elif self.A_star_solve_button.check_click(event):
                pass
            elif self.num_of_pieces_selector.handle_event(event):
                pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    if row is not None and self.logic.get_board()[row][col] != '--':
                        self.dragging = True
                        self.drag_piece = self.logic.get_board()[row][col]
                        self.drag_origin = (row, col)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    
                    if row is not None:
                        # Manual move also uses (r1, c1, r2, c2)
                        self.logic.step((self.drag_origin[0], self.drag_origin[1], row, col))
                    
                    self.dragging = False
                    self.drag_piece = None

    def draw(self):
        self.draw_board()
        screen = pygame.display.get_surface()
        
        self.rule_box.draw(screen)
        self.return_image.draw(screen)
        self.num_of_pieces_selector.draw(screen)
        self.change_map_button.draw(screen)
        self.reset_button.draw(screen)
        self.A_star_solve_button.draw(screen)
        self.stats_panel.draw(pygame.display.get_surface())

        if self.A_star_solver:
            self.play_solution_btn.draw(pygame.display.get_surface())

        if self.animating and self.anim_piece:
            img = self.logic.get_image(self.anim_piece)
            screen.blit(img, (self.current_anim_pos.x, self.current_anim_pos.y))

        if self.dragging and self.drag_piece:
            img = self.logic.get_image(self.drag_piece)
            rect = img.get_rect(center=self.mouse_pos)
            screen.blit(img, rect)
    
    def reset_game(self):
        """ Stops any animation and resets logic """
        self.animating = False
        self.logic.reset()

    def trigger_move(self, start_grid_pos, end_grid_pos):
        """ Call this function to start the 1-second animation """
        r1, c1 = start_grid_pos
        r2, c2 = end_grid_pos

        piece = self.logic.get_board()[r1][c1]
        if piece == '--': return

        self.animating = True
        self.anim_piece = piece
        self.anim_start_time = pygame.time.get_ticks()

        start_x = self.BOARD_X + (c1 * self.SQUARE_SIZE)
        start_y = self.BOARD_Y + (r1 * self.SQUARE_SIZE)
        self.anim_start_pos = pygame.math.Vector2(start_x, start_y)

        end_x = self.BOARD_X + (c2 * self.SQUARE_SIZE)
        end_y = self.BOARD_Y + (r2 * self.SQUARE_SIZE)
        self.anim_end_pos = pygame.math.Vector2(end_x, end_y)

        self.final_move_data = (r1, c1, r2, c2)

    def start_visual_search(self):
        """ Starts the A* Search """
        self.A_star_solver = None 
        self.solver_iterator = self.logic.A_star(self)

    def handle_change_map(self):
        print("Changing Map...")
        self.logic.change_map()
        
        self.A_star_solver = None
        self.playback_queue = []
        self.is_playing_solution = False
        self.stats_panel.update_stats(status="Ready", nodes=0, length=0)

    def handle_reset(self):
        print("Resetting Board...")
        self.logic.reset()
        self.animating = False
        self.is_playing_solution = False
        self.playback_queue = []

    def start_solution_playback(self):
        if not self.A_star_solver:
            return
            
        print("Replaying solution...")
        self.logic.reset()
        self.playback_queue = list(self.A_star_solver.get_final_path())
        self.is_playing_solution = True

    def get_square_under_mouse(self, pos):
        x, y = pos
        # Check if mouse is inside the board area
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            col = (x - self.BOARD_X) // self.SQUARE_SIZE
            row = (y - self.BOARD_Y) // self.SQUARE_SIZE
            return row, col
        return None, None
    
    def draw_board(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        
        # 1. Draw Checkerboard
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x_pos, y_pos, self.SQUARE_SIZE, self.SQUARE_SIZE))

        # 2. Draw Highlight (Yellow square under mouse)
        if self.dragging:
            hover_row, hover_col = self.get_square_under_mouse(self.mouse_pos)
            if hover_row is not None:
                # Create a transparent surface for the highlight
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(150) 
                s.fill(COLOR_HIGHLIGHT) 
                screen.blit(s, (self.BOARD_X + hover_col * self.SQUARE_SIZE, self.BOARD_Y + hover_row * self.SQUARE_SIZE))    # type: ignore

        # 3. Draw Pieces
        board = self.logic.get_board()
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = board[r][c]
                if piece != '--':
                    if self.dragging and (r, c) == self.drag_origin:
                        continue
                    
                    if self.animating and (r, c) == (self.final_move_data[0], self.final_move_data[1]):
                        continue
                    
                    x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                    y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                    screen.blit(self.logic.get_image(piece), (x_pos, y_pos))