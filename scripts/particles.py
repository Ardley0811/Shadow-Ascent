import math
import random
import pygame

from scripts.constants import RED


class Particle:
    def __init__(self, pos, colour=RED, lifetime=30):
        self.pos = list(pos)
        self.colour = colour
        self.lifetime = lifetime
        self.timer = 0

        # Generate a random initial direction and speed
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 2)

        # Converts polar coordinates (angle, speed) to velocity vector
        self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]


    def update(self):
        # Move particles bases on its current velocity
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # Apply gravity
        self.velocity[1] += 0.15

        self.timer += 1

        # Return whether the particles is still alive
        return self.timer < self.lifetime

    def draw(self, surf):
        if self.timer < self.lifetime:
            pygame.draw.circle(surf, self.colour, (int(self.pos[0]), int(self.pos[1])), 2)

