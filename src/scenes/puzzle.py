import pygame
import json
import random
import time
import copy
import os

from src.scenes.scene import Scene
from settings import *
from src.utils.asset_loading import load_images, get_puzzle_limits, colorize_image
from src.ui.element import *
from src.ui.algorithm_handler import AlgorithmHandler
from src.entities.chess import ChessPuzzle


class PuzzleLogic:
    def __init__(self, mode, square_size, board_layout: list[list[int]] | None = None):
        self.mode = mode
        self.puzzle = ChessPuzzle(mode, board_layout)

        self.MIN_NUM_PIECES, self.MAX_NUM_PIECES = get_puzzle_limits(mode)

        self.initial_board_layout = self.puzzle.get_state()
        self.images = load_images(square_size)
        self.current_num_of_pieces = self.puzzle.board.count_pieces()
    
    def step(self, action: tuple[int, int, int, int]):
        return self.puzzle.step(action)
    
    def change_num_of_pieces(self, num: int) -> bool:
        if num < self.MIN_NUM_PIECES or num > self.MAX_NUM_PIECES:
            return False
        self.current_num_of_pieces = num
        
        try:
            with open(DATA_URL + f'chess_{self.mode}/puzzle_map.json') as json_data:
                map_list = json.load(json_data).get(str(num), [])
            
            if not map_list:
                blank_board = [[0 for _ in range(8)] for _ in range(8)]
                self.puzzle.reset(blank_board)
                self.initial_board_layout = blank_board
                return True

            new_map = self.puzzle.board.export_board()
            if len(map_list) > 1:
                while new_map == self.puzzle.board.export_board():
                    new_map = random.choice(map_list)
            else:
                new_map = map_list[0]

            self.puzzle.reset(new_map)
            self.initial_board_layout = new_map
            return True
            
        except Exception as e:
            print(f"Error changing num pieces: {e}")
            return False

    def change_map(self):
        try:
            with open(DATA_URL + f'chess_{self.mode}/puzzle_map.json') as json_data:
                map_list = json.load(json_data).get(str(self.current_num_of_pieces), [])
            if not map_list: return
            new_map = self.puzzle.board.export_board()
            if len(map_list) == 1 and map_list[0] == new_map:
                return
            while new_map == self.puzzle.board.export_board():
                new_map = random.choice(map_list)
            self.puzzle.reset(new_map)
            self.initial_board_layout = copy.deepcopy(new_map)
        except Exception as e:
            print(f"Error changing map: {e}")

    def reset(self):
        self.puzzle.reset(self.initial_board_layout)

    def solver_iterator(self, scene, algorithm_class):
        temp_env = ChessPuzzle(self.mode, self.puzzle.get_state())
        solver = algorithm_class(temp_env)
        iterations = 0
        
        while True:
            state, move = solver.take_action()
            if state is None and move is None:
                break
            
            self.puzzle.set_state(state)
            scene.trigger_move((move[0], move[1]), (move[2], move[3]))
            
            iterations += 1
            if iterations > 10000:
                yield ("error", "Timeout") 
                break
            yield ("running", iterations) 

        self.reset()
        if solver.solution_found:
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
    def __init__(self, manager, mode, initial_map=None):
        super().__init__(manager)
        self.update_screen()
        self.mode = mode
        self.MIN_NUM_PIECES, self.MAX_NUM_PIECES = get_puzzle_limits(mode)
        
        self.drag_piece = None
        self.drag_origin = None
        self.dragging = False
        self.valid_moves = []
        self.mouse_pos = (0, 0)
        self.logic = PuzzleLogic(mode, self.SQUARE_SIZE, initial_map)

        self.animating = False
        self.anim_piece = None      
        self.anim_start_pos = None  
        self.anim_end_pos = None
        self.final_move_data = (0,0,0,0)  
        self.anim_start_time = 0
        self.ANIMATION_DURATION = 250 
        self.current_anim_pos = pygame.math.Vector2(0, 0)
        
        self.is_playing_solution = False
        self.playback_queue = []
        self.game_won = False
        self.win_font = pygame.font.Font(None, 100)
        self.coord_font = pygame.font.SysFont("arial", 30, bold=True)
        self.coord_font.bold = True
        self.algorithm_handler = AlgorithmHandler(self)

        with open(DATA_URL + 'puzzle_info.json') as json_data:
            rules = json.load(json_data)[f"chess_{self.mode}"]["rules"]

        self.return_image = ClickableImage(APP_IMG_URL + "return.png", self.SCREEN_WIDTH // 32, self.MARGIN, (self.SCREEN_WIDTH // 32, self.SCREEN_WIDTH // 32), action = lambda: self.manager.switch_scene('menu'), func = lambda image: colorize_image(image, COLOR_DARK))

        btn_x = self.LEFT_MARGIN // 2 - self.SCREEN_WIDTH // 10
        btn_width = self.SCREEN_WIDTH // 5
        btn_height = 60
        start_y = self.MARGIN + self.SCREEN_HEIGHT // 5
        spacing = 20
    
        selector_x = self.LEFT_MARGIN // 2 - self.SCREEN_WIDTH // 20
        selector_y = start_y
        
        self.pieces_label_font = pygame.font.SysFont("tahoma", 45, bold=True)
        self.pieces_label_surf = self.pieces_label_font.render("Number of pieces", True, COLOR_LIGHT)
        self.pieces_label_pos = (selector_x - 100, selector_y - 80)

        self.num_of_pieces_selector = NumberSelector(
            selector_x, selector_y, 
            self.MIN_NUM_PIECES, self.MAX_NUM_PIECES, self.logic.get_num_of_pieces(), 
            APP_IMG_URL + "left-arrow.png", APP_IMG_URL + "right-arrow.png", 
            self.handle_num_of_pieces, self.handle_num_of_pieces,
            image_func=lambda image: colorize_image(image, COLOR_DARK)
        )
        
        self.change_map_button = ThemedButton("Change Map", btn_x, start_y + 120, btn_width, btn_height, font_size=40, action=self.handle_change_map)
        self.reset_button = ThemedButton("Start over", btn_x, start_y + 120 + btn_height + spacing, btn_width, btn_height, font_size=40, action=self.handle_reset)

        algo_start_y = start_y + 120 + (btn_height + spacing) * 2 + 40
        row_height = 80
        icon_size = (60, 60)
        
        label_w = self.SCREEN_WIDTH // 8
        total_w = label_w + 20 + icon_size[0] + 20 + icon_size[0]
        
        self.label_x = btn_x + (btn_width - total_w) // 2 + 8
        self.search_x = self.label_x + label_w + 11
        self.play_x = self.search_x + icon_size[0] + 11
        
        self.astar_y = algo_start_y
        self.astar_label = LabelBox("A* algorithm", self.label_x, self.astar_y + 10, label_w, self.SCREEN_HEIGHT // 25, font_size=28)
        self.astar_search_btn = ClickableImage(APP_IMG_URL + "search.png", self.search_x, self.astar_y, icon_size, action=lambda: self.handle_search("A*"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.astar_play_btn = ClickableImage(APP_IMG_URL + "play.png", self.play_x, self.astar_y, icon_size, action=lambda: self.start_solution_playback("A*"), func = lambda image: colorize_image(image, COLOR_DARK))

        self.bfs_y = algo_start_y + row_height
        self.bfs_label = LabelBox("BFS algorithm", self.label_x, self.bfs_y + 10, label_w, 40, font_size=28)
        self.bfs_search_btn = ClickableImage(APP_IMG_URL + "search.png", self.search_x, self.bfs_y, icon_size, action=lambda: self.handle_search("BFS"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.bfs_play_btn = ClickableImage(APP_IMG_URL + "play.png", self.play_x, self.bfs_y, icon_size, action=lambda: self.start_solution_playback("BFS"), func = lambda image: colorize_image(image, COLOR_DARK))

        self.dfs_y = algo_start_y + row_height * 2
        self.dfs_label = LabelBox("DFS algorithm", self.label_x, self.dfs_y + 10, label_w, 40, font_size=28)
        self.dfs_search_btn = ClickableImage(APP_IMG_URL + "search.png", self.search_x, self.dfs_y, icon_size, action=lambda: self.handle_search("DFS"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.dfs_play_btn = ClickableImage(APP_IMG_URL + "play.png", self.play_x, self.dfs_y, icon_size, action=lambda: self.start_solution_playback("DFS"), func = lambda image: colorize_image(image, COLOR_DARK))

        rule_box_x = self.SCREEN_WIDTH - self.SCREEN_WIDTH // 40 - self.SCREEN_WIDTH // 5
        self.rule_box = RuleBox(rule_box_x, self.MARGIN , self.SCREEN_WIDTH // 5, self.SCREEN_HEIGHT // 8, rules)

    def update_screen(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = 50 
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.LEFT_MARGIN = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
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

        self.algorithm_handler.update()
                    
        if self.is_playing_solution and not self.animating:
            if self.playback_queue:
                next_move = self.playback_queue.pop(0)
                self.trigger_move((next_move[0], next_move[1]), (next_move[2], next_move[3]))
            else:
                self.is_playing_solution = False

        for event in event_list:
            if self.animating: continue 

            if self.return_image.check_click(event): pass
            elif self.change_map_button.check_click(event): pass 
            elif self.reset_button.check_click(event): pass
            elif self.num_of_pieces_selector.handle_event(event): pass

            elif self.astar_search_btn.check_click(event): pass
            elif self.bfs_search_btn.check_click(event): pass
            elif self.dfs_search_btn.check_click(event): pass
    
            elif self.algorithm_handler.has_solution("A*") and self.astar_play_btn.check_click(event): pass
            elif self.algorithm_handler.has_solution("BFS") and self.bfs_play_btn.check_click(event): pass
            elif self.algorithm_handler.has_solution("DFS") and self.dfs_play_btn.check_click(event): pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    self.valid_moves = [] 
                    if row is not None and self.logic.get_board()[row][col] != '--':
                        self.dragging = True
                        self.drag_piece = self.logic.get_board()[row][col]
                        self.drag_origin = (row, col)
                        full_moves = self.logic.puzzle.board.get_all_valid_moves(specific_pos=(row, col))
                        self.valid_moves = [(m[2], m[3]) for m in full_moves]

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    move_made = False
                    if row is not None:
                        obs, reward, done, info = self.logic.step((self.drag_origin[0], self.drag_origin[1], row, col))
                        if reward != -10: 
                            move_made = True
                            if done: self.game_won = True
                    self.dragging = False
                    self.drag_piece = None
                    if move_made:
                        self.valid_moves = []   

    def draw(self):
        self.draw_board()
        screen = pygame.display.get_surface()
        
        self.rule_box.draw(screen)
        self.return_image.draw(screen)
        screen.blit(self.pieces_label_surf, self.pieces_label_pos)
        self.num_of_pieces_selector.draw(screen)
        self.change_map_button.draw(screen)
        self.reset_button.draw(screen)
        
        self.algorithm_handler.draw(screen) 

        self.astar_label.draw(screen)
        self.bfs_label.draw(screen)
        self.dfs_label.draw(screen)
        
        self.astar_search_btn.draw(screen)
        self.bfs_search_btn.draw(screen)
        self.dfs_search_btn.draw(screen)

        if self.algorithm_handler.has_solution("A*"):
            self.astar_play_btn.draw(screen)
        if self.algorithm_handler.has_solution("BFS"):
            self.bfs_play_btn.draw(screen)
        if self.algorithm_handler.has_solution("DFS"):
            self.dfs_play_btn.draw(screen)

        if self.animating and self.anim_piece:
            img = self.logic.get_image(self.anim_piece)
            screen.blit(img, (self.current_anim_pos.x, self.current_anim_pos.y))

        if self.dragging and self.drag_piece:
            img = self.logic.get_image(self.drag_piece)
            rect = img.get_rect(center=self.mouse_pos)
            screen.blit(img, rect)

        if self.game_won:
            s = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150)) 
            screen.blit(s, (0,0))
            text_surf = self.win_font.render("YOU WIN!", True, COLOR_DARK)
            text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(20, 20), 4)
            screen.blit(text_surf, text_rect)
    
    def reset_game(self):
        self.animating = False
        self.logic.reset()

    def trigger_move(self, start_grid_pos, end_grid_pos):
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
        self.anim_end_pos = pygame.math.Vector2(self.BOARD_X + c2*self.SQUARE_SIZE, self.BOARD_Y + r2*self.SQUARE_SIZE)
        self.final_move_data = (r1, c1, r2, c2)

    def handle_change_map(self):
        self.logic.change_map()
        self.algorithm_handler.reset()
        self.playback_queue = []
        self.is_playing_solution = False
        self.game_won = False

    def handle_search(self, algorithm_name):
        self.handle_reset()
        self.algorithm_handler.start_search(algorithm_name)

    def handle_reset(self):
        self.logic.reset()
        self.animating = False
        self.is_playing_solution = False
        self.playback_queue = []
        self.game_won = False

    def handle_num_of_pieces(self, num_of_pieces):
        self.logic.change_num_of_pieces(num_of_pieces)
        self.algorithm_handler.reset()
        self.game_won = False

    def start_solution_playback(self, algorithm_name):
        if not self.algorithm_handler.has_solution(algorithm_name):
            return 
        print(f"Replaying {algorithm_name} solution...")
        self.logic.reset()
        self.playback_queue = list(self.algorithm_handler.get_solution_path(algorithm_name))
        self.is_playing_solution = True
        self.game_won = False

    def get_square_under_mouse(self, pos):
        x, y = pos
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            col = (x - self.BOARD_X) // self.SQUARE_SIZE
            row = (y - self.BOARD_Y) // self.SQUARE_SIZE
            return row, col
        return None, None
    
    def draw_board(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                is_light_square = (r + c) % 2 == 0
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x_pos, y_pos, self.SQUARE_SIZE, self.SQUARE_SIZE))
                text_color = COLOR_DARK if is_light_square else COLOR_LIGHT
                if c == 0:
                    rank_text = str(8 - r)
                    text_surf = self.coord_font.render(rank_text, True, text_color)
                    screen.blit(text_surf, (x_pos + self.SQUARE_SIZE // 12, y_pos + self.SQUARE_SIZE // 24))
                if r == 7:
                    file_text = chr(97 + c)
                    text_surf = self.coord_font.render(file_text, True, text_color)
                    text_width = text_surf.get_width()
                    text_height = text_surf.get_height()
                    screen.blit(text_surf, (x_pos + self.SQUARE_SIZE - text_width - self.SQUARE_SIZE // 12, y_pos + self.SQUARE_SIZE - text_height - self.SQUARE_SIZE // 24))

        if self.dragging:
            hover_row, hover_col = self.get_square_under_mouse(self.mouse_pos)
            if hover_row is not None:
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(150) 
                s.fill(COLOR_HIGHLIGHT) 
                screen.blit(s, (self.BOARD_X + hover_col * self.SQUARE_SIZE, self.BOARD_Y + hover_row * self.SQUARE_SIZE))

        board = self.logic.get_board()
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = board[r][c]
                if piece != '--':
                    if self.dragging and (r, c) == self.drag_origin: continue
                    if self.animating and (r, c) == (self.final_move_data[0], self.final_move_data[1]): continue
                    x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                    y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                    screen.blit(self.logic.get_image(piece), (x_pos, y_pos))
        if self.valid_moves: 
            for (r, c) in self.valid_moves:
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                radius = self.SQUARE_SIZE // 8 
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(s, COLOR_ORANGE_HIGHLIGHT, (self.SQUARE_SIZE//2, self.SQUARE_SIZE//2), radius)
                screen.blit(s, (x_pos, y_pos))