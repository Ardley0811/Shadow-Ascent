import pygame
import sys

from scripts.extras import  load_images
from scripts.tilemap import Tilemap
from scripts.constants import *



class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.display = pygame.Surface((DISPLAY_WIDTH,DISPLAY_HEIGHT))
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))

        self.clock = pygame.time.Clock()

        # Load all tile assets into a dict
        self.assets = {
            'stone': load_images('tile/stone'),
            'spike': load_images('tile/spike'),
            'spawners': load_images('tile/spawners'),
            'ice_floor': load_images('tile/ice/ice_floor'),
            'ice_spike': load_images('tile/ice/ice_spike'),
            'lava_floor': load_images('tile/lava/lava_floor'),
            'lava_spike': load_images('tile/lava/lava_spike'),
            'cosmic_floor': load_images('tile/cosmic/cosmic_floor'),
            'cosmic_spike': load_images('tile/cosmic/cosmic_spike'),

            'exit': load_images('tile/exit'),
        }


        # Create the tilemap object
        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)

        self.tile_list = list(self.assets) # List of all tile types
        self.tile_group = 0 # Currently selected tile type index
        self.tile_variant = 0 # Currently selected tile variant index

        self.error_message = ""
        self.error_timer = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False

        # Map management
        self.current_map = 0
        self.map_folder = 'assets/images/maps/'
        self.current_map_file = f"{self.map_folder}{self.current_map}.json"
        self.load_current_map() # Load the first map


    def count_player(self):
        # Counts the number of player spawn tiles on the current map
        # Makes sure that only one player spawner is allowed on a map
        count = 0
        for tile in self.tilemap.tilemap.values():
            if tile['type'] == 'spawners' and tile['variant'] == 0:
                count += 1

        return count

    def load_current_map(self):
        # Loads the current map from JSON
        # If there is no files, start with an empty map
        self.tilemap.tilemap = {}
        try:
            self.tilemap.load(f"{self.map_folder}{self.current_map}.json")
        except FileNotFoundError:
            self.tilemap.tilemap = {}

    def run(self):
        while True:

            self.display.fill(BLACK)

            self.tilemap.render(self.display)

            # Prepare the currently selected tile for preview
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            # Get mouse position and scale it to display coordinates
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)

            # Determines which tile the mouse is over
            tile_pos = (int((mouse_pos[0]) // self.tilemap.tile_size), int((mouse_pos[1]) // self.tilemap.tile_size))

            # Draw the preview tile at the mouse location
            self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size, tile_pos[1] * self.tilemap.tile_size))

            if self.clicking:
                try:
                    # Ensures only one player spawner exists
                    if self.tile_list[self.tile_group] == 'spawners' and self.tile_variant == 0:
                        if self.count_player() >= 1:
                            raise ValueError

                    # Place tile in the tilemap dict
                    self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}

                except ValueError:
                    # Display error message if user is trying to place multiple players
                    self.error_message = "Only one player is allowed"
                    self.error_timer = 120

            if self.right_clicking:
                # Removes tile from tilemap dict if the user right clicks on a tile
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]

            # Small preview of the selected tile in the top left of the screen
            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True

                    # Scrolls through tile variant
                    if self.shift:
                        if event.button == 4: # Scroll up
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5: # Scroll down
                            self.tile_variant = (self.tile_variant +1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4: # Scroll up
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5: # Scroll down
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        # Save the current map
                        self.tilemap.save(f"{self.map_folder}{self.current_map}.json")

                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                    # Navigates between maps
                    if event.key == pygame.K_RIGHT:
                        # If user is on the last map, pressing the right arrow does nothing
                        if self.current_map < MAX_MAP_INDEX:
                            self.current_map += 1
                            self.load_current_map()
                    if event.key == pygame.K_LEFT:
                        self.current_map = max(0, self.current_map - 1)
                        self.load_current_map()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            if self.error_timer > 0:
                font = pygame.font.SysFont(None, 20)
                text = font.render(self.error_message, True,RED)
                self.display.blit(text, (10, 30))
                self.error_timer -= 1

            # Scale the render surface to the actual window
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

Editor().run()
