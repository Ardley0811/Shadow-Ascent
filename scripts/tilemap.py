import json
import pygame

from scripts.constants import TILE_SIZE

# Offsets used to check all of the neighbouring tiles around an entity
NEIGHBOUR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

# All tiles that entities can collide with
PHYSICS_TILES = {'stone', 'spike', 'ice_spike', 'ice_floor', 'lava_floor', 'lava_spike', 'cosmic_floor', 'cosmic_spike'}


class Tilemap:
    def __init__(self, main, tile_size=TILE_SIZE):
        self.main = main
        self.tile_size = tile_size
        # Dict storing all tiles
        self.tilemap = {}


    def extract(self, id_list, keep=False):
        found = [] # Stores all the tiles that match the given IDs

        # Loop through every tiles in a copy of the tilemap dict

        for loc, tile in self.tilemap.copy().items():
            # Checks if this tiles type and variant matches any in the list of the IDs its looking for
            if (tile['type'], tile['variant']) in id_list:
                # Make a copy of the tile to not modify the original
                tile_copy = tile.copy()

                tile_copy['pos'] = [tile_copy['pos'][0] * self.tile_size, tile_copy['pos'][1] * self.tile_size]
                # Adds this tile copy to the list of found tiles
                found.append(tile_copy)
                # If keep is false, removes this tile from the tilemap
                if not keep:
                    del self.tilemap[loc]

        # Returns all the tiles that matched
        return found

    # Returns the tiles that are around the entity
    def tiles_around(self, pos):
        tiles = []
        tiles_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOUR_OFFSETS:
            check_loc = str(tiles_loc[0] + offset[0]) + ';' + str(tiles_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    # Saves the tilemap to a JSON file
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size}, f)
        f.close()

    # Loads the map data from a JSON file
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']

    # Returns the tile data at a given pixel position
    # If there is no tile, then it returns None
    def tile_at_pixel(self, pos):
        x, y = int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)
        return self.tilemap.get(f"{x};{y}", None)

    # Creates a pygame.Rect() around all tiles surrounding the entity
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(
                    tile['pos'][0] * self.tile_size,
                    tile['pos'][1] * self.tile_size,
                    self.tile_size,
                    self.tile_size
                ))
        return rects

    # Returns the type of tile at the center of the rectangle
    def get_tile_type(self, rect):
        center = (rect.centerx, rect.centery)
        tile = self.tile_at_pixel(center)
        if tile:
            return tile['type']
        return None


    # Draws all tiles to the screen
    def render(self, surf):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile['type'] in self.main.assets:
                if isinstance(self.main.assets[tile['type']], list):
                    if tile['variant'] < len(self.main.assets[tile['type']]):
                        surf.blit(
                            self.main.assets[tile['type']][tile['variant']],
                            (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size)
                        )
                else:
                    surf.blit(
                        self.main.assets[tile['type']],
                        (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size)
                    )




