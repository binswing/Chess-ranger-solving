import pygame
import json
import os

from src.scenes.scene import Scene
from src.ui.element import *
from settings import *
from src.utils.asset_loading import load_images
from src.entities.figure import int_to_piece
from src.entities.chess import ChessPuzzle
from src.algorithms.Astar import AStarSolver

class MapCreatorScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        
        self.setup_layout()
        self.images = load_images(self.SQUARE_SIZE)
        self.palette_images = load_images(self.SQUARE_SIZE // 1.5)
        self.trash_icon = pygame.font.SysFont("segoe ui emoji", 40).render("🗑️", True, (200, 50, 50))

        self.mode = "ranger" 
        self.board_data = [[0 for _ in range(8)] for _ in range(8)]
        self.drag_piece_code = None  
        self.selected_tool_code = 1 
        self.trash_rect = None 
        
        self.setup_ui()
        self.feedback = FeedbackToast(self.LEFT_PANEL_X, self.BOARD_Y + self.SCREEN_HEIGHT // 4 + 20)

    def setup_layout(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = 50 
        
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.BOARD_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        
        self.LEFT_PANEL_X = 20
        self.LEFT_PANEL_WIDTH = self.BOARD_X - 40
        self.PALETTE_X = self.BOARD_X + self.BOARD_SIZE + 20
        self.PALETTE_Y = self.BOARD_Y

    def setup_ui(self):
        btn_width = min(200, self.LEFT_PANEL_X + self.LEFT_PANEL_WIDTH - 20)
        start_y = self.BOARD_Y + 80
        
        self.back_btn = ClickableImage(APP_IMG_URL + "return.png", 20, 20, (50, 50), action=lambda: self.manager.switch_scene('menu'))
        
        self.mode_btn = ThemedButton(f"Mode: {self.mode.title()}", self.LEFT_PANEL_X, start_y, btn_width, 50, action=self.toggle_mode)
        self.save_btn = ThemedButton("Save Map", self.LEFT_PANEL_X, start_y + 70, btn_width, 50, action=self.save_map)
        self.clear_btn = ThemedButton("Clear Board", self.LEFT_PANEL_X, start_y + 140, btn_width, 50, action=self.clear_board)

        self.white_pieces = [1, 2, 3, 4, 5, 6] 
        self.black_pieces = [-1, -2, -3, -4, -5, -6]

    def toggle_mode(self):
        if self.mode == "ranger":
            self.mode = "melee"
        else:
            self.mode = "ranger"
            for r in range(8):
                for c in range(8):
                    if self.board_data[r][c] < 0:
                        self.board_data[r][c] = 0
                        
        self.mode_btn.text = f"Mode: {self.mode.title()}"
        self.feedback.show(f"Switched to {self.mode.title()}")

    def update(self, event_list):
        self.setup_layout()
        mouse_pos = pygame.mouse.get_pos()
        self.feedback.update()

        for event in event_list:
            if self.back_btn.check_click(event): return
            if self.mode_btn.check_click(event): return
            if self.save_btn.check_click(event): return
            if self.clear_btn.check_click(event): return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    r, c = self.get_square_under_mouse(mouse_pos)
                    if r is not None:
                        clicked_piece = self.board_data[r][c]
                        if self.selected_tool_code == 0:
                            if clicked_piece != 0:
                                self.board_data[r][c] = 0

                        elif clicked_piece == 0 and self.selected_tool_code != 0:
                            self.board_data[r][c] = self.selected_tool_code
                        
                        elif clicked_piece != 0:
                            self.drag_piece_code = clicked_piece
                            self.board_data[r][c] = 0
                            self.selected_tool_code = clicked_piece
                            
                    sel = self.get_palette_piece_under_mouse(mouse_pos)
                    if sel is not None:
                        self.selected_tool_code = sel
                        if sel != 0:
                            self.drag_piece_code = sel

                elif event.button == 3:
                    r, c = self.get_square_under_mouse(mouse_pos)
                    if r is not None:
                        self.board_data[r][c] = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.drag_piece_code is not None:
                        r, c = self.get_square_under_mouse(mouse_pos)
                        
                        if r is not None:
                            self.board_data[r][c] = self.drag_piece_code
                        else:
                            pass

                        self.drag_piece_code = None

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        
        self.draw_board(screen)
        self.draw_palette(screen)
        
        self.back_btn.draw(screen)
        self.mode_btn.draw(screen)
        self.save_btn.draw(screen)
        self.clear_btn.draw(screen)
        
        self.feedback.draw(screen)

        if self.drag_piece_code is not None:
            piece_cls = int_to_piece[abs(self.drag_piece_code)]
            p_obj = piece_cls(self.drag_piece_code > 0)
            img_key = p_obj.get_short_name()
            if img_key in self.images:
                img = self.images[img_key]
                rect = img.get_rect(center=pygame.mouse.get_pos())
                screen.blit(img, rect)

    def draw_board(self, screen):
        for r in range(8):
            for c in range(8):
                x = self.BOARD_X + c * self.SQUARE_SIZE
                y = self.BOARD_Y + r * self.SQUARE_SIZE
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                code = self.board_data[r][c]
                if code != 0:
                    piece_cls = int_to_piece[abs(code)]
                    p_obj = piece_cls(code > 0)
                    img_key = p_obj.get_short_name()
                    if img_key in self.images:
                        screen.blit(self.images[img_key], (x, y))

    def draw_palette(self, screen):
        col_width = self.SQUARE_SIZE
        row_height = self.SQUARE_SIZE
        start_x = self.PALETTE_X
        start_y = self.PALETTE_Y
        
        for row in range(6):
            for col in range(3):
                if self.mode == "ranger" and col == 2: continue
                
                code = None
                if col == 0:
                    if row == 0: code = 0 
                    else: continue 
                elif col == 1: code = self.white_pieces[row]
                elif col == 2: code = self.black_pieces[row]

                if code is None: continue

                x = start_x + col * (col_width + 10)
                y = start_y + row * (row_height + 10)
                
                if code == self.selected_tool_code:
                    color = (255, 50, 50) if code == 0 else (0, 255, 0)
                    pygame.draw.rect(screen, color, (x - 2, y - 2, col_width + 4, row_height + 4), 3)
                
                pygame.draw.rect(screen, (220, 220, 220), (x, y, col_width, row_height))
                
                if code == 0:
                    rect = self.trash_icon.get_rect(center=(x + col_width//2, y + row_height//2))
                    screen.blit(self.trash_icon, rect)
                    self.trash_rect = pygame.Rect(x, y, col_width, row_height)
                else:
                    piece_cls = int_to_piece[abs(code)]
                    p_obj = piece_cls(code > 0)
                    img_key = p_obj.get_short_name()
                    if img_key in self.palette_images:
                        img = self.palette_images[img_key]
                        rect = img.get_rect(center=(x + col_width//2, y + row_height//2))
                        screen.blit(img, rect)

    def get_palette_piece_under_mouse(self, pos):
        mx, my = pos
        col_width = self.SQUARE_SIZE
        row_height = self.SQUARE_SIZE
        start_x = self.PALETTE_X
        start_y = self.PALETTE_Y
        
        for row in range(6):
            for col in range(3):
                if self.mode == "ranger" and col == 2: continue
                
                code = None
                if col == 0:
                    if row == 0: code = 0
                    else: continue
                elif col == 1: code = self.white_pieces[row]
                elif col == 2: code = self.black_pieces[row]

                if code is None: continue

                x = start_x + col * (col_width + 10)
                y = start_y + row * (row_height + 10)
                
                rect = pygame.Rect(x, y, col_width, row_height)
                if rect.collidepoint(mx, my):
                    return code
        return None

    def get_square_under_mouse(self, pos):
        x, y = pos
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            return (y - self.BOARD_Y) // self.SQUARE_SIZE, (x - self.BOARD_X) // self.SQUARE_SIZE
        return None, None

    def clear_board(self):
        self.board_data = [[0]*8 for _ in range(8)]
        self.feedback.show("Board Cleared")

    def save_map(self):
        count = sum(1 for r in self.board_data for c in r if c != 0)
        if count < 2:
            self.feedback.show("Map too empty!", True)
            return

        self.feedback.show("Checking Solvability...", False)
        self.draw() 
        pygame.display.flip()
        
        puzzle_data = { "board": self.board_data, "turn": True }
        
        try:
            env = ChessPuzzle(self.mode, puzzle_data)
            solver = AStarSolver(env)
            steps = 0
            solved = False
            while steps < 5000:
                state, move = solver.take_action()
                if solver.solution_found:
                    solved = True
                    break
                if state is None and move is None:
                    break 
                steps += 1
            
            if not solved:
                self.feedback.show("Map is Unsolvable!", True)
                return
                
        except Exception as e:
            print(e)
            self.feedback.show("Error checking map!", True)
            return

        folder = "chess_ranger" if self.mode == "ranger" else "chess_melee"
        filepath = DATA_URL + f'{folder}/puzzle_map.json'
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try: data = json.load(f)
                except: data = {}
        
        key = str(count)
        if key not in data:
            data[key] = []
        
        if self.board_data not in data[key]:
            data[key].append(self.board_data)
            with open(filepath, 'w') as f:
                json.dump(data, f)
            self.feedback.show(f"Saved! ({count} pieces)")
        else:
            self.feedback.show("Map already exists!", True)