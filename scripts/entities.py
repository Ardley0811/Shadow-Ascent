import pygame
import random


from scripts.particles import (Particle)
from scripts.extras import to_tile, to_pixel
from scripts.tilemap import PHYSICS_TILES
from scripts.constants import *
from scripts.queue import Queue

# Normalising vectors: normalised v = v/mag(v)
# Keeps the directions but makes the length = 1
# Ensures consistent movement regardless of the distance between the entities
def normalise_vector(v):
    magnitude = (v[0] ** 2 + v[1] ** 2) ** 0.5
    if magnitude == 0:
        return [0, 0]
    return [v[0] / magnitude, v[1] / magnitude]


# Base class for all entities that require physics (Player, enemies)
class PhysicsEntity:
    def __init__(self, main, e_type, pos, size):
        self.spike_cooldown = 0
        self.main = main
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.health = 10
        self.velocity = [float(0),float(0)]
        self.collisions = {'up' : False, 'down': False, 'right' : False, 'left': False}

        self.action = ''
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    # Helper function that returns the center of an object
    def get_center(self):
        return (
            self.pos[0] + self.size[0] // 2,
            self.pos[1] + self.size[1] // 2
        )

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.main.assets[self.type + '/' + self.action].copy()

    # Helper function that returns true if the entity is touching the floor
    def on_ground(self):
        return self.collisions['down']

    def spawn_hit_effect(self, pos, colour=WHITE, amount=8):
        for _ in range(amount):
            self.main.particles.append(Particle(pos, colour=colour))

    def spawn_heal_effect(self):
        center_x, center_y = self.get_center()

        for _ in range(20):
            p = Particle(
                (center_x, center_y),
                colour=LIGHT_GREEN
            )
            p.velocity = [
                random.uniform(-0.5, 0.5),
                random.uniform(-1.5, -0.3)
            ]
            p.gravity = 0.03
            self.main.particles.append(p)

    # Resets the collisions every frame, called in PhysicsEntity.update()
    def reset_collisions(self):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

    # Calculates the movement of the entity each frame
    # Combines input movement with physics velocity
    def calculate_frame_movement(self, movement):
        return (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1]
        )

    # Handles collisions in the horizontal direction
    def handle_x_collision(self, tilemap, dx):
        self.pos[0] += dx
        entity_rect = self.rect()

        for tile_rect, tile_type in self.get_colliding_tiles(tilemap):
            if entity_rect.colliderect(tile_rect):
                if self.handle_hazard(tile_type):
                    return

                if dx > 0:
                    entity_rect.right = tile_rect.left
                    self.collisions['right'] = True
                elif dx < 0:
                    entity_rect.left = tile_rect.right
                    self.collisions['left'] = True

                self.pos[0] = entity_rect.x


    def handle_spike_cooldown(self):
        if hasattr(self, 'spike_cooldown') and self.spike_cooldown > 0:
            self.spike_cooldown -= 1

    # Handles collisions in the vertical direction
    def handle_y_collision(self, tilemap, dy):
        self.pos[1] += dy
        entity_rect = self.rect()

        for tile_rect, tile_type in self.get_colliding_tiles(tilemap):
            if entity_rect.colliderect(tile_rect):
                if self.handle_hazard(tile_type):
                    return

                if dy > 0:
                    entity_rect.bottom = tile_rect.top
                    self.collisions['down'] = True
                elif dy < 0:
                    entity_rect.top = tile_rect.bottom
                    self.collisions['up'] = True

                self.pos[1] = entity_rect.y

    # Flips the sprite depending on the direction they are moving
    # If the entity is moving left, the sprite is flipped otherwise it is not
    def update_sprite_facing(self, movement):
        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True


    def apply_gravity(self):
        gravity = 0.12 # Accerlation due to gravity
        self.velocity[1] += gravity

        # Terminal velocity
        if self.velocity[1] > 5:
            self.velocity[1] = 5


    # Returns all nearby tiles and their types as pairs
    def get_colliding_tiles(self, tilemap):
        for tile_rect in tilemap.physics_rects_around(self.pos):
            tile_type = tilemap.get_tile_type(tile_rect)
            yield tile_rect, tile_type

    # Handles what happens when an entity collides with a spike
    # self.on_hazard() is called, which does different things depending on if the entity is the player or an enemy
    def handle_hazard(self, tile_type):
        if tile_type not in HAZARD_TILES:
            return False

        # Prevents self.on_hazard() from being called every frame
        # Entity is immune from spikes after a certain amount of frames after colliding
        if hasattr(self, "spike_cooldown") and self.spike_cooldown > 0:
            return False

        self.on_hazard()
        return True

    # This method is overridden in Player and Enemy
    # Polymorphism is used here
    def on_hazard(self):
        pass


    # Applies friction to the entities velocity when they are on the ground
    def apply_friction(self):
        if self.on_ground():
            self.velocity[0] *= FRICTION
            if abs(self.velocity[0]) < 0.05:
                self.velocity[0] = 0


    def update(self, tilemap, movement=(0,0)):
        self.reset_collisions()
        frame_movement = self.calculate_frame_movement(movement)

        self.handle_spike_cooldown()

        self.handle_x_collision(tilemap, frame_movement[0])
        self.handle_y_collision(tilemap, frame_movement[1])

        self.update_sprite_facing(movement)

        self.last_movement = movement
        self.apply_gravity()


        if self.on_ground() or self.collisions['up']:
            self.velocity[1] = 0


        self.apply_friction()
        self.animation.update()


    def take_damage(self, amount):
        pass

    def die(self):
        for _ in range(30):
            self.main.particles.append(Particle(self.pos, colour=RED))
        if isinstance(self, Enemy):
            if self in self.main.enemies:
                self.main.enemies.remove(self)


# Visual effect when the player attacks an enemy
class SlashArc:
    def __init__(self, pos, direction, lifetime=8):
        self.pos = list(pos)
        self.direction = direction
        self.timer = lifetime
        self.max_timer = lifetime

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def render(self, surf):
        progress = 1 - (self.timer / self.max_timer)
        radius = int(20 + progress * 10)

        start_angle = SLASH_ARC_START_ANGLE
        end_angle = SLASH_ARC_END_ANGLE

        if self.direction == -1:
            start_angle = PI - SLASH_ARC_END_ANGLE
            end_angle = PI - SLASH_ARC_START_ANGLE

        arc_rect = pygame.Rect(
            self.pos[0] - radius,
            self.pos[1] - radius,
            radius * 2,
            radius * 2
        )

        pygame.draw.arc(
            surf,
            WHITE,
            arc_rect,
            start_angle,
            end_angle,
            3
        )

# Visual effect for when the player heals
class HealPulse:
    def __init__(self, pos):
        self.pos = pos
        self.radius = 4
        self.max_radius = 30
        self.alpha = 200

    def update(self):
        self.radius += 2
        self.alpha -= 15
        return self.alpha > 0

    def render(self, surf):
        if self.alpha <= 0:
            return
        temp = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(
            temp,
            (*LIGHT_GREEN, self.alpha),
            (self.radius, self.radius),
            self.radius,
            2
        )

        surf.blit(
            temp,
            (self.pos[0] - self.radius, self.pos[1] - self.radius)
        )




class Projectile:
    def __init__(self, pos, target_pos, speed=4, colour=CYAN, lifetime=120):

        self.pos = list(pos)
        self.speed = speed
        self.colour = colour
        self.lifetime = lifetime
        self.timer = 0




        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        direction = normalise_vector([dx, dy])
        self.velocity = [
            direction[0] * speed,
            direction[1] * speed
        ]

        self.size = 4

    def rect(self):
        return pygame.Rect(self.pos[0] - self.size // 2, self.pos[1] - self.size // 2, self.size, self.size)

    def update(self, tilemap):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.timer += 1

        # If the projectiles collides with a tile, it disappears
        projectile_rect = self.rect()
        for tile_rect in tilemap.physics_rects_around(self.pos):
            if projectile_rect.colliderect(tile_rect):
                return False


        return self.timer < self.lifetime



    def render(self, surf):
        pygame.draw.circle(surf, self.colour, (int(self.pos[0]), int(self.pos[1])), 2)


# Visual effect that displays the damage done when a player attacks an enemy
class DamageNumber:
    def __init__(self, pos, amount=3, colour=RED):
        self.pos = list(pos)
        self.amount = amount
        self.colour = colour
        self.timer = 60
        self.velocity = [0, -0.5]
        self.alpha = 255

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.timer -= 1
        if self.timer < 30:
            self.alpha = int((self.timer / 30) * 255)
        if self.alpha < 0:
            self.alpha = 0

        return self.timer > 0

    def render(self, surf, font):
        label = font.render(str(self.amount), True, self.colour)
        label.set_alpha(self.alpha)
        label_rect = label.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        surf.blit(label, label_rect)


class Collectible:
    def __init__(self, game, pos, size=(10, 15)):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.image = game.assets['Collectible']

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self):
        if self.rect().colliderect(self.game.player.rect()):
            self.game.player.collect_item()
            return False
        return True

    def render(self, surf):
        surf.blit(self.image, self.pos)


# Base class for all enemies
# Inherits from PhysicsEntity
class Enemy(PhysicsEntity):
    def __init__(self, main, pos, size, enemy_type='enemy'):
        super().__init__(main, enemy_type, pos, size)


        self.walking = 0
        self.attack_cooldown = 0
        self.active = False
        self.knockback_timer = 0
        self.direction = 1
        self.anim_offset = (-10, -16)

        self.health = 5
        self.vision_range = 200
        self.damage = 1

        self.behaviour_queue = Queue()
        self.behaviour_queue.enqueue("patrol")


    # Checks if the tile in front of them on their level is a spike, if so the enemy turns around
    # Checks if the tile in front of them but under them is nothing, if so the enemy turns around
    def hazard_ahead(self, tilemap, dir_sign, steps=1):
        foot_y = self.pos[1] + self.size[1]
        mid_y = self.pos[1] + self.size[1] // 2

        for i in range(1, steps + 1):
            current_tile = to_tile(self.pos, tilemap.tile_size)
            target_tile = (current_tile[0] + dir_sign * i, current_tile[1])

            look_x, _ = to_pixel(target_tile, tilemap.tile_size)
            look_x += self.size[0] // 2

            below_tile = tilemap.tile_at_pixel((look_x, foot_y))
            if below_tile is None:
                return True

            mid_tile = tilemap.tile_at_pixel((look_x, mid_y))
            if mid_tile and mid_tile['type'] in HAZARD_TILES:
                return True

        return False

    def render(self, surf):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]))

    # If the enemies health goes below 0 they die
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    # Pushes the enemy back and up when hit by the player
    def handle_knockback(self, tilemap):
        if self.knockback_timer <= 0:
            return False

        self.knockback_timer -= 1
        self.velocity[0] *= 0.85

        if abs(self.velocity[0]) < 0.05:
            self.velocity[0] = 0

        super().update(tilemap, movement=(0, 0))

        if self.collisions['left'] or self.collisions['right']:
            self.velocity[0] = 0

        return True


    # Checks if there is a clear line of sight from the enemy to the player
    def can_see_player(self, tilemap):
        player = self.main.player
        start_x, start_y = self.get_center()


        end_x = player.pos[0] + player.size[0] // 2
        end_y = player.pos[1] + player.size[1] // 2

        # Distance vector from enemy to player
        dx = end_x - start_x
        dy = end_y - start_y

       # Straight line distance between player and enemy
        distance = int((dx ** 2 + dy ** 2) ** 0.5)
        if distance == 0:
            # Player is on the same position as the enemy
            return True

        # Normalise vectpr to step along the line
        direction = normalise_vector([dx, dy])
        step_x, step_y = direction

        x = start_x
        y = start_y

        for _ in range(distance):
            # Checks each tile along the line for any tiles blocking the way
            tile = tilemap.tile_at_pixel((x, y))
            if tile and tile['type'] in PHYSICS_TILES:
                return False # Obstacles blocks sight
            x += step_x
            y += step_y

        return True # No obstacles, the enemy can see the player

    # Checks if the player is within detection range and on the same level
    def player_detection(self):
        player = self.main.player
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        distance_sq = dx ** 2 + dy ** 2
        same_level = abs(dy) < self.size[1] // 2

        if distance_sq < self.vision_range ** 2 and same_level:
            # Player is in range and on the same level
            self.active = self.can_see_player(self.main.tilemap)
        else:
            self.active = False

        if self.active:
            # If the enemy has spotted the player, the current behaviour is removed and 'chase' is added
            self.behaviour_queue.dequeue()
            self.behaviour_queue.enqueue("chase")
        else:
            # If the player has stopped seeing the player and patrol is not at the top of the queue, the current behaviour is removed and 'patrol' is added
            if self.behaviour_queue.peek() != "patrol":
                self.behaviour_queue.dequeue()
                self.behaviour_queue.enqueue("patrol")


    def patrol(self, tilemap):
        # While patrolling the enemy walks randomly
        if self.walking <= 0 and random.random() < 0.01:
            self.walking = random.randint(30, 120)

        if self.walking > 0:
            # If there is a hazard ahead (no tile or spike), the enemy changes direction
            if self.hazard_ahead(tilemap, self.direction):
                self.direction *= -1

            self.walking -= 1
            return SPEED * self.direction

        return 0.0




    def chasing_player(self, tilemap):
        # Horizontal distance to the player
        player_dx = self.main.player.pos[0] - self.pos[0]

        # If the player is on the enemy, dont move
        if abs(player_dx) < 1:
            return 0.0

        # Sets direction towards the player: -1 = left, 1 = right
        if player_dx < 0:
            self.direction = -1
        else:
            self.direction = 1

        # If there is a hazard in the chose direction, turn around
        if self.hazard_ahead(tilemap, self.direction):
            self.direction *= -1


        # Returns the horixontal speed for this frame
        return SPEED * self.direction

    def decide_movement(self, tilemap):
        if self.behaviour_queue.is_empty():
            # Patrol is always added to the queue if it is empty
            self.behaviour_queue.enqueue("patrol")

        behaviour = self.behaviour_queue.peek()

        # If the top of the queue is 'patrol' then the enemy patrols
        if behaviour == "patrol":
            return self.patrol(tilemap)
        # If the top of the queue is 'chase' then the enemy chases the player
        if behaviour == "chase":
            return self.chasing_player(tilemap)
        # If the top of the queue is 'attack' then the enemy attacks the player
        if behaviour == "attack":
            self.handle_attacking(tilemap)
            return 0 # Enemy is not moving

        return 0 # Enemy is not moving


    # Prevents the enemy from leaving the screen
    def screen_restrictions(self):
        self.pos[0] = max(0, min(self.pos[0], self.main.display.get_width() - self.size[0]))
        self.pos[1] = max(0, min(self.pos[1], self.main.display.get_height() - self.size[1]))

    # If the enemy collides with a wall, they change directions
    def handle_wall_collision(self):
        if self.collisions['left'] or self.collisions['right']:
            self.direction *= -1
            self.flip = self.direction == -1


    def handle_attacking(self, tilemap):
        # If the enemy is not locked onto the player they dont attack
        if not self.active:
            return

        # if the enemy cant see the player, they dont attack
        if not self.can_see_player(tilemap):
            return

        # Prevent enemies from attacking the player every frame
        # After attacking, the enemy cant attack for a certain amount of frames
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        # If the enemy collides with the player they attack
        if self.rect().colliderect(self.main.player.rect()):
            self.main.player.take_damage(self.damage)
            self.attack_cooldown = 30

    # If the enemy collides with a spike they die
    def on_hazard(self):
        self.die()


    def update_animation(self, move_x):
        # If the enemy is moving, 'run' animation is used
        if abs(move_x) > 0.01:
            self.set_action('run')
        # If the enemy is stood still, 'idle' animation is used
        else:
            self.set_action('idle')

    def update(self, tilemap, movement=(0, 0)):
        if self.handle_knockback(tilemap):
            return

        self.player_detection()

        if self.active and self.rect().colliderect(self.main.player.rect()):
            self.behaviour_queue.dequeue()
            self.behaviour_queue.enqueue("attack")

        move_x = self.decide_movement(tilemap)

        self.screen_restrictions()


        super().update(tilemap, movement=[move_x, 0])
        self.update_sprite_facing([move_x, 0])


        self.handle_wall_collision()
        self.handle_attacking(tilemap)
        self.handle_hazard(tilemap)

        self.update_animation(move_x)



# A specific enemy class which inherits from Enemy
class WeakEnemy(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'weak_enemy')
        self.health = 3
        self.attack_cooldown = 20
        self.vision_range = 150
        self.damage = 1



# A specific enemy class which inherits from Enemy
class FrostWarden(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'frost_warden')
        self.health = 7
        self.vision_range = 220
        self.attack_cooldown = 25
        self.damage = 2


# A specific enemy class which inherits from Enemy
class BlizzardShaman(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'blizzard_shaman')

        self.shoot_cooldown = 0
        self.current_projectile = None

        self.health = 5
        self.vision_range = 250
        self.attack_cooldown = 60
        self.damage = 2

    # This enemy fires projectiles at the enemy instead of melee attacking like the standard enemies do
    def handle_attacking(self, tilemap):

        if not self.active:
            return

        if not self.can_see_player(tilemap):
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return

        player_dy = self.main.player.pos[1] - self.pos[1]
        if self.shoot_cooldown == 0:
            vertical_diff = abs(player_dy)
            if vertical_diff < self.size[1] * 2:
                projectile = Projectile(
                    pos=self.get_center(),
                    target_pos=self.main.player.rect().center
                )
                self.main.projectiles.append(projectile)
                self.current_projectile = projectile
                self.shoot_cooldown = 60



# A specific enemy class which inherits from Enemy
class FlameHound(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'flame_hound')
        self.health = 11
        self.attack_cooldown = 10
        self.vision_range = 170
        self.damage = 3


# A specific enemy class which inherits from Enemy
class FireballCaster(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'fireball_caster')

        self.shoot_cooldown = 0
        self.current_projectile = None

        self.health = 9
        self.vision_range = 270
        self.attack_cooldown = 50
        self.damage = 3


    # This enemy fires projectiles at the enemy instead of melee attacking like the standard enemies do
    def handle_attacking(self, tilemap):
        if not self.active:
            return

        if not self.can_see_player(tilemap):
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return

        player_dy = self.main.player.pos[1] - self.pos[1]
        if self.shoot_cooldown == 0:
            vertical_diff = abs(player_dy)
            if vertical_diff < self.size[1] * 2:
                projectile = Projectile(
                    pos=self.get_center(),
                    target_pos=self.main.player.rect().center
                )
                self.main.projectiles.append(projectile)
                self.current_projectile = projectile
                self.shoot_cooldown = 50



# A specific enemy class which inherits from Enemy
class CloudshotGolem(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'cloudshot_golem')
        self.health = 19
        self.vision_range = 240
        self.attack_cooldown = 20
        self.damage = 4



# A specific enemy class which inherits from Enemy
class SkyFlayer(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'sky_flayer')

        self.shoot_cooldown = 0
        self.current_projectile = None

        self.health = 17
        self.vision_range = 290
        self.attack_cooldown = 40
        self.damage = 4



    # This enemy fires projectiles at the enemy instead of melee attacking like the standard enemies do
    def handle_attacking(self, tilemap):

        if not self.active:
            return

        if not self.can_see_player(tilemap):
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return

        player_dy = self.main.player.pos[1] - self.pos[1]
        if self.shoot_cooldown == 0:
            vertical_diff = abs(player_dy)
            if vertical_diff < self.size[1] * 2:
                projectile = Projectile(
                    pos=self.get_center(),
                    target_pos=self.main.player.rect().center
                )
                self.main.projectiles.append(projectile)
                self.current_projectile = projectile
                self.shoot_cooldown = 40



# A specific enemy class which inherits from Enemy
class BlinkingAssassin(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'blinking_assassin')
        self.health = 35
        self.attack_cooldown = 15
        self.vision_range = 260
        self.damage = 5




# A specific enemy class which inherits from Enemy
class ShadowMage(Enemy):
    def __init__(self, main, pos, size):
        super().__init__(main, pos, size, 'shadow_mage')

        self.shoot_cooldown = 0
        self.current_projectile = None

        self.health = 33
        self.vision_range = 310
        self.attack_cooldown = 30
        self.damage = 5



    # This enemy fires projectiles at the enemy instead of melee attacking like the standard enemies do
    def handle_attacking(self, tilemap):

        if not self.active:
            return

        if not self.can_see_player(tilemap):
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return

        player_dy = self.main.player.pos[1] - self.pos[1]
        if self.shoot_cooldown == 0:
            vertical_diff = abs(player_dy)
            if vertical_diff < self.size[1] * 2:
                projectile = Projectile(
                    pos=self.get_center(),
                    target_pos=self.main.player.rect().center
                )
                self.main.projectiles.append(projectile)
                self.current_projectile = projectile
                self.shoot_cooldown = 30


# Class for the player, inherits from PhysicsEntity
class Player(PhysicsEntity):
    def __init__(self, main, pos, size):
        super().__init__(main, 'player', pos, size)

        self.anim_offset = (-10, -11)
        self.health_max = 10
        self.health = self.health_max
        self.base_damage = 3
        self.damage_per_chapter = 2
        self.health_per_chapter = 2
        self.damage_flash_timer = 0

        self.air_time = 0
        self.max_jumps = 1
        self.jumps = self.max_jumps

        self.was_on_ground = False
        self.wall_slide = False
        self.jump_time = 0
        self.jump_time_max = 30
        self.jump_pressed = False

        self.dashing= 0
        self.spike_cooldown = 0
        self.velocity = [float(0), float(0)]
        self.air_accel = 0.06
        self.stamina = 100
        self.stamina_max = 100
        self.dash_cost = 20
        self.stamina_regen = 0.03


        self.special_radius = 80
        self.special_damage = 15
        self.special_stamina_cost = self.stamina_max * 0.5

        self.phantom_iframes = 0
        self.phantom_cooldown = 0
        self.phantom_damage = 15
        self.phantom_stamina_cost = 30
        self.phantom_hit_enemies = set()


        self.can_dash = False
        self.can_double_jump = False
        self.can_special = False
        self.can_phantom_step = False

        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 15
        self.attack_cooldown = 0

        self.collect_count = 0

        self.max_health_potions = 3
        self.health_potions = self.max_health_potions

    def render(self, surf):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]))


    def collect_item(self):
        self.collect_count += 1


    # Applies chapter specific abilities whenever the player reaches that chapter
    def apply_chapter_abilities(self, chapter):
        if chapter >= 2:
            self.can_dash = True
        else:
            self.can_dash = False

        if chapter >= 3:
            self.can_double_jump = True

        else:
            self.can_double_jump = False


        if chapter >= 4:
            self.can_special = True
        else:
            self.can_special = False

        if chapter >= 5:
            self.can_phantom_step = True
        else:
            self.can_phantom_step = False

        # Clamps the remaing jumps, so the player cant exceed max jumps
        self.jumps = min(self.jumps, self.max_jumps)

    # Resets health potions back to 3
    # This is called when the player reaches a new chapter
    def reset_health_potions(self):
        self.health_potions = self.max_health_potions

    # Uses up one of the health potions
    def use_health_potions(self):
        # Checks if there are any health potions left and the player is not at full health
        if self.health_potions > 0 and self.health < self.health_max:
            # Removes one of the health potions
            self.health_potions -= 1
            # Increases health by 5 unless that would cause health to go above max health, if so health is set to max health
            self.health = min(self.health + 5, self.health_max)
            self.spawn_heal_effect()

            center = self.get_center()
            self.main.effects.append(HealPulse(center))

    # Displays how many stars the player has collected
    def render_collectibles_count(self, surf, x, y, font):
        text = f"Stars: {self.collect_count}"
        label = font.render(text, True, YELLOW)
        surf.blit(label, (x, y))

    # Displays the visual of the health potions which spawns under the stamina bar as 3 red circles
    def render_health_potions(self, surf, x, y):
        radius = 5
        spacing = 15
        for i in range(self.max_health_potions):
            colour = RED if i < self.health_potions else DARK_RED
            pygame.draw.circle(surf, colour, (x + i * spacing, y), radius)

    # Spawn a purple trail under the player when they use phantom step
    def spawn_shadow_trail(self):
        if self.phantom_iframes <= 0:
            return

        center = self.get_center()

        p = Particle(
            center,
            colour=DARK_PURPLE
        )
        p.velocity = [
            random.uniform(-0.3, 0.3),
            random.uniform(-0.2, 0.2)
        ]
        p.gravity = 0
        p.lifetime = 20

        self.main.particles.append(p)

    def update_air_and_ground_status(self):
        currently_on_ground = self.on_ground()
        # If the player is on the ground, their jumps get reset and air time is set to 0
        if currently_on_ground and not self.was_on_ground:
            self.jumps = self.max_jumps
            self.air_time = 0

        # While the player is not on the ground air time increase by 1 each frame
        if not currently_on_ground:
            self.air_time += 1

        self.was_on_ground = currently_on_ground


    def handle_wall_slide(self):
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True

            self.set_action('wall_slide')

    def handle_jump_action(self):
        if not self.attacking:
            if not self.wall_slide:
                if self.air_time > 4:
                    self.set_action('jump')
                else:
                    self.set_action('idle')

    def update_dash(self):
        # Reduces dashing counter toward 0
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        elif self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        # Only start applying dash velocity after threshold
        if abs(self.dashing) > 50:
            # Determines direction: 1 = right, -1 = left
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            # Slightly slow the first frame of the dash for smooth feel
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1

    def handle_friction(self, movement):
        # Friction is only applied if the player is standing on the ground
        if self.on_ground():
            friction = 0.15
            self.velocity[0] *= (1 - friction) # Reduce horizontal speed by 15% each frame

            # If the friction were to reverse the players direction, stop movement
            if (movement[0] < 0 < self.velocity[0]) or (movement[0] > 0 > self.velocity[0]):
                self.velocity[0] = 0

    def handle_air_accel(self):
        if not self.on_ground(): # Checks if the player is in the air
            self.air_accel = 0.06 # Set the air acceleration slightly higher when in the air
        else:
            self.air_accel = 0.05 # Set a slightly lower value when on the ground

    def handle_movement(self, movement):
        if movement[0] != 0: # Checks if the player is pressing left (-1) or right (1)
            # SUVAT: v = u + at
            self.velocity[0] += movement[0] * self.air_accel # Updates horizontal speed based on input and accleration

            # Clamps the horizontal velocity between -4 (max left) and 4 (max right)
            self.velocity[0] = max(-4, min(4, self.velocity[0]))
        else:
            self.velocity[0] *= 0.95 # Apply gradual deceleration if no input

    # Prevents the player from leaving the screen
    def screen_restrictions(self):
        self.pos[0] = max(0, min(self.pos[0], self.main.display.get_width() - self.size[0]))
        self.pos[1] = max(0, min(self.pos[1], self.main.display.get_height() - self.size[1]))


    def handle_phantom_damage(self):
        if self.phantom_iframes <= 0:
            return

        # Loops through each enemy and checks if they have been hit by phantom step
        for enemy in self.main.enemies:
            if enemy in self.phantom_hit_enemies:
                continue

            if self.rect().colliderect(enemy.rect()):
                enemy.take_damage(self.phantom_damage)
                enemy.knockback_timer = 10
                self.phantom_hit_enemies.add(enemy)

                dmg_pos = (
                    enemy.pos[0] + enemy.size[0] // 2,
                    enemy.pos[1]
                )
                self.main.damage_numbers.append(
                    DamageNumber(dmg_pos, amount=self.phantom_damage, colour=LIGHT_BLUE)
                )

                enemy.spawn_hit_effect(
                    dmg_pos,
                    colour=SLATE_BLUE,
                    amount=10
                )


    def handle_jumping(self):
        if self.jump_pressed: # Checks if the jump button is being held
            if self.jump_time < self.jump_time_max:
                self.velocity[1] -= 0.09 # Applies an upward force to make the player go up
                self.jump_time += 1
                if not self.can_double_jump:
                    self.jumps -= 1





    def regenerate_stamina(self, movement):
        if movement[0] == 0 and movement[1] == 0:
            # Stamina increases exponentially
            # The further away self.stamina is from self.stamina_max, the faster the stamina increases
            self.stamina += (self.stamina_max - self.stamina) * self.stamina_regen
            self.stamina = min(self.stamina, self.stamina_max)



    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)


        self.update_air_and_ground_status()

        if self.phantom_iframes > 0:
            self.phantom_iframes -= 1
            self.spawn_shadow_trail()

        if self.phantom_cooldown > 0:
            self.phantom_cooldown -= 1

        self.handle_phantom_damage()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attacking:
            self.attack_timer -= 1
            self.velocity[0] *= 0.8

            if self.attack_timer <= 0:
                self.attacking = False

        self.handle_wall_slide()
        self.handle_jump_action()
        self.update_dash()



        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        self.handle_friction(movement)
        self.handle_jumping()


        self.handle_air_accel()
        self.handle_movement(movement)
        self.screen_restrictions()

        self.regenerate_stamina(movement)
        self.handle_hazard(tilemap)

    # If the player collides with a spike, they get sent back to the start of the room they were in
    # Their health, stamina and health potions remain the same
    def on_hazard(self):
        self.spike_cooldown = 20
        self.pos = list(self.main.start_pos)
        self.velocity = [0, 0]
        self.air_time = 0
        self.jumps = self.max_jumps

    def jump(self):
        if self.wall_slide:
            if self.collisions['right']:
                self.velocity[0] = -2.5
            else:
                self.velocity[0] = 2.5

            self.velocity[1] = -2.2
            self.air_time = 5
            return True

        if self.on_ground():
            self.velocity[1] = -1.5
            self.jump_time = 0
            self.jump_pressed = True
            self.air_time = 5
            self.jumps -= 1

            return True

        if self.jumps > 0:
            self.velocity[1] = -1.5
            self.jumps -= 1
            self.jump_time = 0
            self.jump_pressed = True
            self.air_time = 5
            return True
        return False

    def dash(self):
        if not self.can_dash:
            return
        if not self.dashing and self.stamina >= self.dash_cost:
            if self.flip:
                # If the player is facing left, dash to the left
                self.dashing = -70
            else:
                # If the player is facing right dash to the right
                self.dashing = 70
            self.stamina -= self.dash_cost

    def HP_up(self):
        # Increase the health of the player every chapter
        self.health_max += self.health_per_chapter
        self.health = self.health_max

    def attack(self):
        # If the player is attacking or just attacked then they cant do it again for a certain amount of frames
        if self.attacking or self.attack_cooldown > 0:
            return
        self.attacking = True
        self.attack_timer = self.attack_duration
        self.attack_cooldown = 20
        # Increases the damage based on the chapter they are on
        damage = self.base_damage + (self.main.current_chapter - 1) * self.damage_per_chapter

        attack_rect = self.rect().inflate(30, 0)
        hit_enemy = False

        for enemy in self.main.enemies:
            if attack_rect.colliderect(enemy.rect()):
                enemy.take_damage(damage)
                direction = -1 if self.flip else 1
                enemy.velocity[0] += direction * 3.5
                enemy.velocity[1] = -1.2
                enemy.knockback_timer = 10
                hit_enemy = True
                damage_number_pos = (self.pos[0] + self.size[0] / 2, self.pos[1])
                self.main.damage_numbers.append(DamageNumber(damage_number_pos, amount=damage))

                hit_x = enemy.pos[0] + enemy.size[0] // 2
                hit_y = enemy.pos[1] + enemy.size[1] // 2
                enemy.spawn_hit_effect((hit_x, hit_y), colour=LIGHT_PINK, amount=12)

        if hit_enemy:
            direction = -1 if self.flip else 1
            arc_x = self.pos[0] + (0 if self.flip else self.size[0])
            arc_y = self.pos[1] + self.size[1] // 2
            self.main.slash_arcs.append(
                SlashArc((arc_x, arc_y), direction)
            )
        self.set_action('attack')

    def double_jump(self):
        if not self.can_double_jump:
            return

        self.max_jumps = 2

        if self.jumps > self.max_jumps:
            self.jumps = self.max_jumps

    def special_attack(self):
        if not self.can_special:
            return

        if self.stamina < self.special_stamina_cost:
            return

        self.stamina -= self.special_stamina_cost

        center_x, center_y = self.get_center()



        for enemy in self.main.enemies[:]:
            enemy_x = enemy.pos[0] + enemy.size[0] // 2
            enemy_y = enemy.pos[1] + enemy.size[1] // 2

            distance = ((enemy_x - center_x) ** 2 + (enemy_y - center_y) ** 2) ** 0.5

            if distance <= self.special_radius:
                enemy.take_damage(self.special_damage)
                enemy.knockback_timer = 12
                enemy.velocity[1] = -1.5


                enemy.spawn_hit_effect((enemy_x, enemy_y), colour=LIGHT_PURPLE, amount=18)

                self.main.damage_numbers.append(
                    DamageNumber((enemy_x, enemy_y), amount=self.special_damage, colour=LIGHT_PURPLE)
                )

        self.main.effects.append(HealPulse((center_x, center_y)))

    def phantom_step(self):
        if not self.can_phantom_step:
            return

        if self.phantom_cooldown > 0:
            return

        if self.stamina < self.phantom_stamina_cost:
            return

        if not self.dashing:
            return

        self.phantom_iframes = 12
        self.phantom_cooldown = 45
        self.stamina -= self.phantom_stamina_cost
        self.phantom_hit_enemies.clear()




    def take_damage(self, amount):

        if self.phantom_iframes > 0:
            return

        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.stamina = self.stamina_max
        self.damage_flash_timer = 5





