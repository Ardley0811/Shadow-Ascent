import pygame
import os

from scripts.constants import BLACK

# Base path for image assets
BASE_IMG_PATH = 'assets/images/'

 # Loads a single image from the given path
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey(BLACK) # Makes black pixels transparent
    return img


# Loads all images from a folder and returns them as a list
def load_images(path):
    images = []
    # Loops through all files in the folder
    for img_name in os.listdir(BASE_IMG_PATH + path):
        # Loads each image and appends it to the list
        images.append(load_image(path + '/' + img_name))
    return images


# Converts a pixel position to a tile position
def to_tile(pos, tile_size):
    return int(pos[0] // tile_size), int(pos[1] // tile_size)

# Converts a tile position to a pixel position
def to_pixel(tile, tile_size):
    return tile[0] * tile_size, tile[1] * tile_size


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur # Duration of each frame
        self.done= False # Set to True when non-looping animation finishes
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            # Loops infinitely through frames
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            # Moves to the next frame and stops at the last frame
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)

            if self.frame >= self.img_duration * len(self.images) -1:
                self.done = True


    def img(self):
        return self.images[int(self.frame / self.img_duration)]



