import pygame

pygame.font.init() # Initialize the font module

# Get a list of all available system fonts
all_fonts = pygame.font.get_fonts()

# Print the list of fonts (optional)
for font_name in all_fonts:
    print(font_name)