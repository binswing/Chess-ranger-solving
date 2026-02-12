import pygame
import sys

from settings import *

# --- Theme Colors (Matches a Chess/Puzzle Vibe) ---
THEME = {
    'primary': (210, 180, 140),    # Tan/Wood
    'shadow': (139, 69, 19),       # SaddleBrown (Darker wood)
    'highlight': (255, 248, 220),  # Cornsilk (Lighter)
    'text': (50, 30, 10),          # Dark Brown text
    'box_bg': (30, 30, 30, 200)    # Dark transparent background for rules
}

class ThemedButton:
    def __init__(self, text, x, y, width, height, font_size=30, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        
        # Visuals
        self.font = pygame.font.Font(None, font_size)
        self.elevation = 5  # Height of the "3D" effect
        self.dynamic_elevation = self.elevation
        self.y_original = y

        # State
        self.pressed = False
        self.hovered = False

    def draw(self, screen):
        # 1. Update Logic (Hover & Click)
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # 2. Calculate "3D" logic
        # If clicked, "press" the button down (reduce elevation)
        if self.pressed:
            self.dynamic_elevation = 0
            curr_y = self.y_original + self.elevation
            main_color = THEME['shadow'] # Darker when pressed
        elif self.hovered:
            self.dynamic_elevation = self.elevation
            curr_y = self.y_original
            main_color = THEME['highlight'] # Lighter when hovered
        else:
            self.dynamic_elevation = self.elevation
            curr_y = self.y_original
            main_color = THEME['primary']

        # 3. Draw Bottom Shadow (The "Side" of the button)
        shadow_rect = pygame.Rect(self.rect.x, self.y_original + self.elevation, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, THEME['shadow'], shadow_rect, border_radius=12)

        # 4. Draw Top Face (The clicky part)
        # We move the visual rect up/down based on elevation
        self.top_rect = pygame.Rect(self.rect.x, curr_y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, main_color, self.top_rect, border_radius=12)
        
        # Border
        pygame.draw.rect(screen, THEME['text'], self.top_rect, 2, border_radius=12)

        # 5. Draw Text
        text_surf = self.font.render(self.text, True, THEME['text'])
        text_rect = text_surf.get_rect(center=self.top_rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, event):
        """ Returns True if this button was clicked """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.top_rect.collidepoint(event.pos):
                self.pressed = True
                return False
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if self.top_rect.collidepoint(event.pos):
                    if self.action:
                        self.action()
                    return True # Valid Click
        return False


class RuleBox:
    def __init__(self, x, y, width, height, text_list):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_list = text_list # A generic list of strings ["Rule 1...", "Rule 2..."]
        self.font = pygame.font.Font(None, 24)
        self.bg_color = THEME['box_bg']
        self.text_color = (240, 240, 240)
        
        # Pre-render the lines to save performance
        self.rendered_lines = self.wrap_text(self.text_list)

    def wrap_text(self, lines):
        """ Breaks long lines into smaller ones that fit the box width """
        wrapped_lines = []
        for line in lines:
            words = line.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                # Check width of the line + new word
                fw, fh = self.font.size(test_line)
                if fw < self.rect.width - 20: # -20 for padding
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word + " "
            wrapped_lines.append(current_line)
        return wrapped_lines

    def draw(self, screen):
        # 1. Draw Transparent Background
        # We need a separate surface to support alpha (transparency)
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color) 
        screen.blit(s, (self.rect.x, self.rect.y))
        
        # 2. Draw Border
        pygame.draw.rect(screen, THEME['primary'], self.rect, 3)

        # 3. Draw Text
        y_offset = 15 # Top padding
        for line in self.rendered_lines:
            text_surf = self.font.render(line, True, self.text_color)
            screen.blit(text_surf, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 25 # Line height spacing

class Image:
    def __init__(self, image_url, x, y, size = None) -> None:
        self.x = x
        self.y = y
        self.size = size
        try:
            self.logo_image = pygame.image.load(image_url).convert_alpha()
            if size is not None:
                self.logo_image = pygame.transform.smoothscale(self.logo_image, size)
        except pygame.error as e:
            print(f"Error loading image: {e}")
            sys.exit()

    def draw(self, screen):
        screen.blit(self.logo_image, (self.x, self.y))

class ClickableImage:
    def __init__(self, image_path, x, y, size=None, action=None):
        self.x = x
        self.y = y
        self.action = action  
        self.is_hovered = False

        try:
            self.surface = pygame.image.load(image_path).convert_alpha()
            
            if size is not None:
                self.surface = pygame.transform.smoothscale(self.surface, size)
            width = self.surface.get_width()
            height = self.surface.get_height()
            self.hover_surface = pygame.transform.smoothscale(
                self.surface, 
                (int(width * 1.2), int(height * 1.2))
            )
                
        except pygame.error as e:
            print(f"Error loading image: {e}")
            sys.exit()

        self.rect = self.surface.get_rect(topleft=(x, y))
        self.hover_rect = self.hover_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered:
            screen.blit(self.hover_surface, self.hover_rect)
        else:
            screen.blit(self.surface, self.rect)

    def check_click(self, event):
        """ Checks if the image was clicked and triggers the action """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action() # Run the assigned function
                return True
        return False
    
class NumberSelector:
    def __init__(self, x, y, min_val, max_val, initial_val, left_img_path, right_img_path, left_action=None, right_action=None):
        self.x = x
        self.y = y
        self.value = initial_val
        self.min_val = min_val
        self.max_val = max_val
        self.left_action = left_action
        self.right_action = right_action
        
        # Style Settings
        self.font = pygame.font.Font(None, 40)
        self.text_color = (255, 255, 255)
        self.spacing = 20 # Space between buttons and text
        self.text_area_width = 60

        def decrease():
            if self.value > self.min_val:
                self.value -= 1
                self.update_text() # Refresh the text surface
                if self.left_action:
                    self.left_action(self.value)

        self.btn_left = ClickableImage(
            left_img_path, 
            x, y, 
            size=(40, 40), 
            action=decrease
        )

        self.text_area_width = 60
        
        def increase():
            if self.value < self.max_val:
                self.value += 1
                self.update_text()
                if self.right_action:
                    self.right_action(self.value)

        btn_right_x = x + 40 + self.spacing + self.text_area_width + self.spacing
        self.btn_right = ClickableImage(
            right_img_path, 
            btn_right_x, y, 
            size=(40, 40), 
            action=increase
        )

        self.text_surf = None
        self.text_rect = None
        self.update_text()

    def update_text(self):
        """ Renders the number text centered between the buttons """
        text_str = str(self.value)
        self.text_surf = self.font.render(text_str, True, self.text_color)
        
        start_x = self.x + 40 + self.spacing
        center_x = start_x + (self.text_area_width // 2)
        center_y = self.y + 20 # Half of button height (40/2)
        
        self.text_rect = self.text_surf.get_rect(center=(center_x, center_y))

    def handle_event(self, event):
        """ Passes the event down to the child buttons """
        self.btn_left.check_click(event)
        self.btn_right.check_click(event)

    def draw(self, screen):
        # Draw Left Button
        self.btn_left.draw(screen)
        
        # Draw Text
        if self.text_surf:
            screen.blit(self.text_surf, self.text_rect)
            
        # Draw Right Button
        self.btn_right.draw(screen)
        
    def get_value(self):
        return self.value

class StatsPanel:
    def __init__(self, x, y, width, font_size=30, text_list:list[str]=[]):
        self.rect = pygame.Rect(x, y, width, 0)
        self.font = pygame.font.Font(None, font_size)
        self.font_size = font_size
        self.bg_color = (30, 30, 30, 200)
        self.text_color = (255, 255, 255)
        self.base_text_list = text_list

        self.nodes_visited = 0
        self.path_length = 0
        self.status = "Ready"
        self.path = None
        
        self.lines_to_draw = []
        self.line_height = font_size + 5
        self.side_padding = 15
        self.top_margin = 20    
        self.bottom_padding = 10 
        
        self.recalculate_layout()

    def update_stats(self, nodes=None, status=None, path=None):
        if nodes is not None: self.nodes_visited = nodes
        if status is not None: self.status = status
        if path is not None: 
            self.path = path
            self.path_length = len(path)
        
        self.recalculate_layout()

    def recalculate_layout(self):
        self.lines_to_draw = self.base_text_list[:]
        self.lines_to_draw.append(f"Status: {self.status}")
        self.lines_to_draw.append(f"Nodes: {self.nodes_visited}")
        
        if self.path is not None:
            self.lines_to_draw.append(f"Steps: {self.path_length}")
            if self.path_length > 0:
                self.lines_to_draw.append("Path:")
                moves_str = []
                for move in self.path:
                    start = f"{chr(move[1]+97)}{8-move[0]}"
                    end = f"{chr(move[3]+97)}{8-move[2]}"
                    moves_str.append(f"{start}-{end}")
                
                full_path_str = " -> ".join(moves_str)
                chars_per_line = int(self.rect.width / (self.font_size * 0.34)) 
                for i in range(0, len(full_path_str), chars_per_line):
                    self.lines_to_draw.append(full_path_str[i : i + chars_per_line])
        num_lines = len(self.lines_to_draw)
        new_height = self.top_margin + (num_lines * self.line_height) + self.bottom_padding
        self.rect.height = new_height

    def draw(self, screen):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        screen.blit(s, self.rect.topleft)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        y_offset = self.top_margin 
        
        for line in self.lines_to_draw:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (self.rect.x + self.side_padding, self.rect.y + y_offset))
            y_offset += self.line_height

class FeedbackToast:
    def __init__(self, x, y, min_width=200):
        self.x = x
        self.y = y
        self.min_width = min_width
        self.text = ""
        self.is_visible = False
        self.timer = 0
        self.duration = 3000
        self.font = pygame.font.SysFont("arial", 24)
        self.color = (0, 255, 0)
        self.bg_color = (30, 30, 30, 220)
        self.border_color = (100, 100, 100)

    def show(self, text, is_error=False):
        self.text = text
        self.is_visible = True
        self.timer = pygame.time.get_ticks()
        self.color = (255, 80, 80) if is_error else (100, 255, 100)
        self.border_color = (200, 50, 50) if is_error else (50, 200, 50)

    def update(self):
        if self.is_visible:
            if pygame.time.get_ticks() - self.timer > self.duration:
                self.is_visible = False

    def draw(self, screen):
        if not self.is_visible:
            return
        text_surf = self.font.render(self.text, True, self.color)
        width = max(self.min_width, text_surf.get_width() + 40)
        height = 50
        rect = pygame.Rect(self.x, self.y, width, height)
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        screen.blit(s, (self.x, self.y)) 
        pygame.draw.rect(screen, self.border_color, rect, 2)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)