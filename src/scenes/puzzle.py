import pygame
import json

from src.scenes.scene import Scene
# from src.logic import GameLogic  # Your existing logic class!
from settings import *
from src.utils.asset_loading import load_images
from src.ui.element import *

# Initialize Pygame

class PuzzleLogic:
    def __init__(self, square_size):
        self.board = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        self.images = load_images(square_size)

    def get_image(self, piece: str):
        return self.images[piece]
    
    def get_board(self):
        return self.board      

class PuzzleScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.update_screen()
        self.drag_piece = None
        self.drag_origin = None
        self.dragging = False
        self.mouse_pos = (0, 0)
        self.logic = PuzzleLogic(self.SQUARE_SIZE)

        self.return_image = ClickableImage(APP_IMG_URL + "return.png", self.SCREEN_WIDTH // 32, self.MARGIN, (self.SCREEN_WIDTH // 32, self.SCREEN_WIDTH // 32), action = lambda: self.manager.switch_scene('menu'))
        with open(DATA_URL + 'puzzle_info.json') as json_data:
            rules = json.load(json_data)["chess_ranger"]["rules"]
            json_data.close()
        self.rule_box = RuleBox(self.SCREEN_WIDTH - self.SCREEN_WIDTH // 40 - self.SCREEN_WIDTH // 5, self.MARGIN, self.SCREEN_WIDTH // 5, self.SCREEN_HEIGHT // 8, rules)
    
    def update_screen(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = 50 
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.SQUARE_SIZE = self.BOARD_SIZE // 8

        # Center the board
        self.BOARD_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        
    def update(self, event_list):
        self.update_screen()
        self.mouse_pos = pygame.mouse.get_pos()
        for event in event_list:
            if self.return_image.check_click(event):
                print("Switch to Menu button clicked!")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    if row is not None and self.logic.board[row][col] != '--':
                        self.dragging = True
                        self.drag_piece = self.logic.board[row][col]
                        self.drag_origin = (row, col)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    
                    if row is not None:
                        # Move the piece in data
                        old_r, old_c = self.drag_origin                 # type: ignore
                        self.logic.board[old_r][old_c] = '--'
                        self.logic.board[row][col] = self.drag_piece
                    
                    self.dragging = False
                    self.drag_piece = None

    def draw(self):
        self.draw_board()

        self.rule_box.draw(self.display_surface)
        self.return_image.draw(self.display_surface)

        # Draw dragged piece centered on mouse
        if self.dragging and self.drag_piece:
            img = self.logic.get_image(self.drag_piece)
            rect = img.get_rect(center=self.mouse_pos)
            self.display_surface.blit(img, rect)
    
    def get_square_under_mouse(self, pos):
        x, y = pos
        # Check if mouse is inside the board area
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            col = (x - self.BOARD_X) // self.SQUARE_SIZE
            row = (y - self.BOARD_Y) // self.SQUARE_SIZE
            return row, col
        return None, None
    
    def draw_board(self):
        self.display_surface.fill(COLOR_BG)
        
        # 1. Draw Checkerboard
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(self.display_surface, color, (x_pos, y_pos, self.SQUARE_SIZE, self.SQUARE_SIZE))

        # 2. Draw Highlight (Yellow square under mouse)
        if self.dragging:
            hover_row, hover_col = self.get_square_under_mouse(self.mouse_pos)
            if hover_row is not None:
                # Create a transparent surface for the highlight
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(150) 
                s.fill(COLOR_HIGHLIGHT) 
                self.display_surface.blit(s, (self.BOARD_X + hover_col * self.SQUARE_SIZE, self.BOARD_Y + hover_row * self.SQUARE_SIZE))    # type: ignore

        # 3. Draw Pieces
        board = self.logic.get_board()
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = board[r][c]
                if piece != '--':
                    if self.dragging and (r, c) == self.drag_origin:
                        continue
                        
                    x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                    y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                    self.display_surface.blit(self.logic.get_image(piece), (x_pos, y_pos))