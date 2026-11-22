import pygame
import sys
import json
import os

from scripts.extras import load_image, load_images, Animation
from scripts.entities import Player, Enemy, WeakEnemy, FrostWarden, BlizzardShaman, FlameHound, FireballCaster, CloudshotGolem, SkyFlayer, BlinkingAssassin, ShadowMage, Collectible
from scripts.tilemap import Tilemap
from scripts.constants import *
from scripts.stack import Stack



# Base class for all menus
# Provides common methods for drawing options and handling results
class Menu:
    def __init__(self, game):
        self.game = game

    # Draws a list of menu options
    def draw_options(self, display, options, selected, pos, font, spacing=35, hover_colour=YELLOW, normal_colour=WHITE, mouse_scale=True):
        if mouse_scale:
            mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = (
                mouse_pos[0] * display.get_width() // self.game.screen.get_width(),
                mouse_pos[1] * display.get_height() // self.game.screen.get_height()
            )
        else:
            scaled_mouse_pos = pygame.mouse.get_pos()

        rects = []
        for i in range(len(options)):
            text = options[i]
            # Highlights the selected options
            if i == selected:
                colour = hover_colour
            else:
                colour = normal_colour

            # Grey out continue game if there is no save
            if text == "Continue Game" and not os.path.exists(SAVE_FILE):
                colour = LIGHT_GREY


            label = font.render(text, True, colour)
            label_rect = label.get_rect(topleft=(pos[0], pos[1] + i * spacing))
            display.blit(label, label_rect.topleft)

            if label_rect.collidepoint(scaled_mouse_pos):
                selected = i

            rects.append(label_rect)
        return selected, rects

    # This abstract method is overridden in later classes
    def run(self):
        pass

    # This abstract method is overridden in later classes
    def handle_result(self, result):
        pass

# MainMenu inherits from Menu
class MainMenu(Menu):
    def __init__(self):
        super().__init__(game)
        self.screen = game.screen
        self.display = pygame.Surface((DISPLAY_WIDTH,DISPLAY_HEIGHT))
        self.clock = game.clock

        self.buttons = ["Start Game", "Continue Game", "Settings", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.title_font = pygame.font.SysFont(FONT_NAME, MAIN_TITLE_FONT_SIZE, bold=True)
        self.title_colour = PURPLE

        self.save_exists = os.path.exists(SAVE_FILE)

        self.error_message = ""
        self.error_timer = 0

    def draw_gradient(self, surf, top_colour, bottom_colour):
        # Draws a coloured gradient which goes from purple to black top to down
        height = surf.get_height()
        for y in range(height):
            ratio = y / height
            r = int(top_colour[0] * (1- ratio) + bottom_colour[0] * ratio)
            g = int(top_colour[1] * (1- ratio) + bottom_colour[1] * ratio)
            b = int(top_colour[2] * (1- ratio) + bottom_colour[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (surf.get_width(), y))

    # This method overrides handle_result() from its parent class Menu
    def handle_result(self, result):
        if result == "Start Game":
            # Removes all menus from stack
            self.game.menu_stack.clear()

            # Delete old save if it exists
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            # Start a new game
            self.game.start_new_game()

        elif result == "Continue Game":
            # Removes all menus from stack
            self.game.menu_stack.clear()
            # Load existing save
            self.game.load_game()

        elif result == "Settings":
            # Adds Settings Menu to the top of stack
            self.game.menu_stack.push(SettingsMenu())

        elif result == "Quit":
            # Closes the application
            pygame.quit()
            sys.exit()


    # This method overrides run() from its parent class Menu
    def run(self):
        menu_pos = (40, self.display.get_height() - 160)
        while True:
            self.save_exists = os.path.exists(SAVE_FILE)
            self.draw_gradient(
                self.display,
                DARK_PURPLE,
                BLACK
            )

            # Title glow effect
            glow_surf = self.title_font.render("Shadow Ascent", True, DARK_BLUE)
            glow_rect = glow_surf.get_rect(center=(self.display.get_width() // 2 + 2, 82))
            self.display.blit(glow_surf, glow_rect)

            # Main title
            title_surf = self.title_font.render("Shadow Ascent", True, self.title_colour)
            title_rect = title_surf.get_rect(center=(self.display.get_width() // 2, 80))
            self.display.blit(title_surf, title_rect)

            # Draws the options for Main Menu
            self.selected, rects = self.draw_options(
                display=self.display,
                options = self.buttons,
                selected=self.selected,
                pos=menu_pos,
                font=self.font,
                spacing=35
            )

            if self.error_timer > 0:
                message_surf = self.font.render(self.error_message, True, LIGHT_RED)
                message_rect = message_surf.get_rect(center=(self.display.get_width() // 2, self.display.get_height() - 50))
                self.display.blit(message_surf, message_rect)
                self.error_timer -= 1


            selected_rect = rects[self.selected]
            # If there is no save, coninue game will be grey
            if self.buttons[self.selected] != "Continue Game" or self.save_exists:
                colour = YELLOW
            else:
                colour = LIGHT_GREY

            pygame.draw.line(
                self.display,
                colour,
                (selected_rect.left, selected_rect.bottom + 2),
                (selected_rect.right, selected_rect.bottom + 2),
                2
            )



            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        selected_text = self.buttons[self.selected]
                        if selected_text == "Continue Game":
                            if not os.path.exists(SAVE_FILE):
                                self.error_message = "No save file found"
                                self.error_timer = 120
                                continue
                            else:
                                return selected_text
                        else:
                            return selected_text




# SettingsMenu inherits from Menu
class SettingsMenu(Menu):
    def __init__(self):
        super().__init__(game)
        self.screen = game.screen
        self.display = pygame.Surface((DISPLAY_WIDTH,DISPLAY_HEIGHT))
        self.clock = game.clock
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.error_message = ""
        self.error_timer = 0


        self.sections = [
            "Controls",
            "Back"
        ]
        self.selected_section = 0


        self.control_options = ["Move Left",
                                "Move Right",
                                "Jump",
                                "Dash",
                                "Heal",
                                "Attack",
                                "Special_Attack"
                                ]

        # Default key bindings
        self.control_keys = {
            "Move Left": pygame.K_a,
            "Move Right": pygame.K_d,
            "Jump": pygame.K_SPACE,
            "Dash": pygame.K_RSHIFT,
            "Attack": pygame.K_j,
            "Heal": pygame.K_h,
            "Special_Attack": pygame.K_k
        }
        self.selected_control_option = 0
        self.waiting_for_key = False

        # Predefined presets for keybinds
        self.presets = {
            "WASD": {"Move Left": pygame.K_a, "Move Right": pygame.K_d, "Jump": pygame.K_SPACE, "Dash": pygame.K_RSHIFT, "Attack": pygame.K_j, "Heal": pygame.K_h, "Special_Attack": pygame.K_k},
            "Arrows": {"Move Left": pygame.K_LEFT, "Move Right": pygame.K_RIGHT, "Jump": pygame.K_UP, "Dash": pygame.K_LSHIFT, "Attack": pygame.K_z, "Heal": pygame.K_x, "Special_Attack": pygame.K_c}

        }

        self.load_settings()


    def save_settings(self):

        # Makes sure SETTINGS_FILE exists
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)

        # Prepares keybind data for saving to JSON
        data = {"controls": self.control_keys.copy()}

        # Save keybinds to SETTINGS_FILE
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        # Loads keybinds from SETTINGS_FILE if it exists
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                controls = data.get("controls", {})
                for key, value in controls.items():
                    if key in self.control_keys:
                        self.control_keys[key] = value


    # Handles menu result (overrides parent method)
    def handle_result(self, result):
        if result == "main_menu":
            # Apply any updated keybinds
            self.game.controls = self.control_keys.copy()
            # Remove Settings Menu from stack to return to the previous menu
            self.game.menu_stack.pop()


    def run(self):
        while True:
            self.display.fill(DARK_GREY)

            current_section = self.sections[self.selected_section] # The menu section which is selected

            # Draws the section buttons
            # This uses the method draw_options which is inherited from Menu Class
            self.selected_section, section_rect = self.draw_options(
                display=self.display,
                options=self.sections,
                selected=self.selected_section,
                pos=(50, 50),
                font=self.font,
                spacing=30
            )



            if current_section == "Controls":
                control_pos = (250, 50)
                # Display the current keybindings as text
                control_texts = [f"{opt}: {pygame.key.name(self.control_keys[opt])}" for opt in self.control_options]

                # Combines keybinds text with the presets
                combined_options = control_texts + [f"Preset: {p}" for p in self.presets]

                # Draws the combined options using the method draw_options which is inherited from Menu
                self.selected_control_option, control_rects = self.draw_options(
                    display=self.display,
                    options=combined_options,
                    selected=self.selected_control_option,
                    pos=control_pos,
                    font=self.font,
                    spacing=30
                )


            # Displays an error message if the user tries to change a keybind to a key which is already being used
            if self.error_timer > 0:
                error_surf = self.font.render(self.error_message, True, LIGHT_RED)
                self.display.blit(error_surf, (250, 320))
                self.error_timer -= 1

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                   if self.waiting_for_key:
                       try:
                           # If key entered by the user is already assigned to another control raise an error
                           if event.key in self.control_keys.values():
                               raise ValueError

                           # Assign the new key to the selected option
                           option = self.control_options[self.selected_control_option]
                           self.control_keys[option] = event.key
                           self.waiting_for_key = False
                       except ValueError:
                           self.error_message = "Key Already in use"
                           self.error_timer = 60

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        if current_section == "Back":
                            self.save_settings() # Keybinds get saved
                            return "main_menu" # Returns to the main menu screen
                        elif current_section == "Controls":
                            # If selected index is a control and not a preset
                            if self.selected_control_option < len(self.control_options):
                                self.waiting_for_key = True
                            else:
                                # If the selected index is a preset
                                preset_index = self.selected_control_option - len(self.control_options)
                                preset_name = list(self.presets.keys())[preset_index]
                                self.control_keys = self.presets[preset_name].copy() # Apply preset chosen
                                # Update the keybinds to match the preset chosen
                                self.control_options = list(self.control_keys.keys())
                                self.selected_control_option = 0


# GameOverScreen inherits from Menu
class GameOverScreen(Menu):
    def __init__(self):
        super().__init__(game)
        self.save_exists = None
        self.screen = game.screen
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = game.clock
        self.font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE, bold=True)
        self.font_options = pygame.font.SysFont(FONT_NAME, GAME_OVER_OPTIONS_FONT_SIZE)

        self.options = ["Play Again", "Main Menu"]
        self.selected = 0

    # Handles menu result (overrides parent method)
    def handle_result(self, result):
        if result == "Play Again":
            # Removes all menus from the stack
            self.game.menu_stack.clear()
            # Starts new game
            self.game.start_new_game()

        elif result == "Main Menu":
            # Removes all menus from the stack
            self.game.menu_stack.clear()
            # Adds MainMenu to the top of stack
            self.game.menu_stack.push(MainMenu())

    # This method overrides the method with the same name in its parent class Menu
    def run(self):
        while True:
            self.display.fill(BLACK)

            title = self.font.render("Game Over", True, LIGHT_RED)
            title_rect = title.get_rect(center=(self.display.get_width() // 2, 110))
            self.display.blit(title, title_rect)

            stars_text = f"Stars Collected: {self.game.player.collect_count}"
            starts_label = self.font_options.render(stars_text, True, YELLOW)
            stars_rect = starts_label.get_rect(center=(self.display.get_width() // 2, 160))
            self.display.blit(starts_label, stars_rect)

            # Draws the options using the method draw_options which is inherited from Menu
            self.selected, option_rects = self.draw_options(
                display=self.display,
                options=self.options,
                selected=self.selected,
                pos=(self.display.get_width() // 2 - 100, 200),
                font=self.font_options,
                spacing=50,
                hover_colour=YELLOW,
                normal_colour=WHITE,
                mouse_scale=True
            )

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    selected_text = self.options[self.selected]
                    return selected_text




# PauseMenu inherits from Menu
class PauseMenu(Menu):
    def __init__(self):
        super().__init__(game)
        self.screen = game.screen
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = game.clock
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.options = ["Continue", "Settings", "Save and Quit"]
        self.selected = 0
        self.waiting_for_key = False

    # Handles menu result (overrides parent method)
    def handle_result(self, result):
        if result == "Continue":
            # Removes Pause menu from stack
            self.game.menu_stack.pop()

        elif result == "Settings":
            # Add Settings Menu to stack on top of Pause Menu
            self.game.menu_stack.push(SettingsMenu())

        elif result == "Save and Quit":
            # Saves progress and return to Main Menu
            self.game.save_game()
            # Removes all menus from the stack
            self.game.menu_stack.clear()
            # Main Menu is added to the top of stack
            self.game.menu_stack.push(MainMenu())

    def run(self):
        while True:
            self.display.fill(BLACK)

            self.selected, option_rects = self.draw_options(
                display=self.display,
                options=self.options,
                selected=self.selected,
                pos=(200, 100),
                font=self.font,
                spacing=40,
                hover_colour=YELLOW,
                normal_colour=WHITE,
                mouse_scale=True
            )
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        return self.options[self.selected]


# Screen which appears before a new chapter
class ChapterScreen:
    def __init__(self, chapter_text, duration=2000, bonuses=None):
        self.game = game
        self.screen = game.screen
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = game.clock
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold=True)
        self.chapter_text = chapter_text
        self.duration = duration
        if bonuses:
            self.bonuses = bonuses
        else:
            self.bonuses = []

    def run(self):
        start_time = pygame.time.get_ticks()
        alpha = 255
        fade_out_started = False

        text_surface = self.font.render(self.chapter_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2 - 30))

        bonus_surfaces = []
        for i in range(len(self.bonuses)):
            text = self.bonuses[i]
            surf = self.font.render(text, True, LIGHT_BLUE)
            rect = surf.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2 + i * 30 + 10))
            bonus_surfaces.append((surf, rect))


        while True:
            self.display.fill(BLACK)
            self.display.blit(text_surface, text_rect)
            for surface, rect in bonus_surfaces:
                self.display.blit(surface, rect)

            elapsed = pygame.time.get_ticks() - start_time
            if elapsed > self.duration:
                fade_out_started = True

            if fade_out_started:
                alpha -= 5
                if alpha <= 0:
                    break
                text_surface.set_alpha(alpha)
                for surface, _ in bonus_surfaces:
                    surface.set_alpha(alpha)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



# Helper method to help load images
def load_animation(path, img_dur=50, loop=True):
    return Animation(load_images(path), img_dur=img_dur, loop=loop)

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Shadow Ascent")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH,DISPLAY_HEIGHT))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.controls = {
            "Move Left": pygame.K_a,
            "Move Right": pygame.K_d,
            "Jump": pygame.K_SPACE,
            "Dash": pygame.K_RSHIFT,
            "Attack": pygame.K_j,
            "Heal": pygame.K_h,
            "Special_Attack": pygame.K_k
        }

        self.assets = {
            'stone': load_images('tile/stone'),
            'spike': load_images('tile/spike'),
            'exit': load_images('tile/exit'),
            'ice_floor': load_images('tile/ice/ice_floor'),
            'ice_spike': load_images('tile/ice/ice_spike'),
            'lava_floor': load_images('tile/lava/lava_floor'),
            'lava_spike': load_images('tile/lava/lava_spike'),
            'cosmic_floor': load_images('tile/cosmic/cosmic_floor'),
            'cosmic_spike': load_images('tile/cosmic/cosmic_spike'),
            'Player': load_image('entities/Sprite.png'),
            'Collectible': load_image('entities/Collectible.png'),
            'backgrounds': [
                load_image('backgrounds/00.png'),
                load_image('backgrounds/01.png'),
                load_image('backgrounds/02.png'),
                load_image('backgrounds/03.png'),
                load_image('backgrounds/04.png'),
                load_image('backgrounds/05.png'),
                load_image('backgrounds/06.png'),
                load_image('backgrounds/07.png'),
                load_image('backgrounds/08.png'),
                load_image('backgrounds/09.png'),
                load_image('backgrounds/10.png'),
                load_image('backgrounds/11.png'),
                load_image('backgrounds/12.png'),
                load_image('backgrounds/13.png'),
                load_image('backgrounds/14.png'),
                load_image('backgrounds/15.png'),
                load_image('backgrounds/16.png'),
                load_image('backgrounds/17.png'),
                load_image('backgrounds/18.png'),
                load_image('backgrounds/19.png'),
                load_image('backgrounds/20.png'),
                load_image('backgrounds/21.png'),
                load_image('backgrounds/22.png'),
                load_image('backgrounds/23.png'),
                load_image('backgrounds/24.png'),


            ],
            'enemy/idle': load_animation('entities/enemy/idle', 50),
            'enemy/run': load_animation('entities/enemy/run', 15),
            'weak_enemy/idle':load_animation('entities/weak_enemy/idle', 50),
            'weak_enemy/run': load_animation('entities/weak_enemy/run', 15),
            'frost_warden/idle': load_animation('entities/frost_warden/idle', 50),
            'frost_warden/run': load_animation('entities/frost_warden/run', 15),
            'blizzard_shaman/idle': load_animation('entities/blizzard_shaman/idle', 50),
            'blizzard_shaman/run': load_animation('entities/blizzard_shaman/run', 15),
            'flame_hound/idle': load_animation('entities/flame_hound/idle', 50),
            'flame_hound/run': load_animation('entities/flame_hound/run', 15),
            'fireball_caster/idle': load_animation('entities/fireball_caster/idle', 50),
            'fireball_caster/run': load_animation('entities/fireball_caster/run', 15),
            'cloudshot_golem/idle': load_animation('entities/cloudshot_golem/idle', 50),
            'cloudshot_golem/run': load_animation('entities/cloudshot_golem/run', 15),
            'sky_flayer/idle': load_animation('entities/sky_flayer/idle', 50),
            'sky_flayer/run': load_animation('entities/sky_flayer/run', 15),
            'blinking_assassin/idle': load_animation('entities/blinking_assassin/idle', 50),
            'blinking_assassin/run': load_animation('entities/blinking_assassin/run', 15),
            'shadow_mage/idle': load_animation('entities/shadow_mage/idle', 50),
            'shadow_mage/run': load_animation('entities/shadow_mage/run', 15),

            'player/idle': load_animation('entities/player/idle', 10),
            'player/jump': load_animation('entities/player/jump', 30),
            'player/wall_slide': load_animation('entities/player/wall_slide'),
            'player/run': load_animation('entities/player/run'),
            'player/attack': load_animation('entities/player/attack', 5, loop=False)
        }



        self.start_pos = START_POS

        # Creates player with starting position, size and access to the game
        self.player = Player(self, self.start_pos.copy(), (8, 16))
        self.assets['font'] = pygame.font.SysFont(FONT_NAME, 16, bold=True)

        # Creates the tilemap for the level with a given tile size and game reference
        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)

        self.particles = []
        self.projectiles = []
        self.slash_arcs = []
        self.effects = []
        self.damage_numbers = []
        self.collectibles = []

        self.collectibles_collected = 0

        self.menu_stack = Stack()

        self.next_map_loading = False
        self.current_map_id = 0
        self.spawn_pos = [0, 0]
        self.current_chapter = 1
        self.current_background = self.assets['backgrounds'][0]

    # Called when the player completes a level
    # Moves on to the next level
    def next_level(self):
        self.current_map_id += 1
        self.load_level(self.current_map_id)
        if self.current_map_id < len(self.assets['backgrounds']):
            self.current_background = self.assets['backgrounds'][self.current_map_id]

        for chapter, start_level in CHAPTER_LEVELS.items():
            if self.current_map_id >= start_level:
                self.current_chapter = chapter

        self.player.apply_chapter_abilities(self.current_chapter)


    # Checks if the player has collided with the exit_collision tile
    def check_exit_collision(self):
        player_rect = self.player.rect().inflate(2, 2)


        for tile in self.tilemap.tiles_around(self.player.pos):
            if tile['type'] == 'exit':
                tile_rect = pygame.Rect(
                    tile['pos'][0] * self.tilemap.tile_size,
                    tile['pos'][1] * self.tilemap.tile_size,
                    self.tilemap.tile_size,
                    self.tilemap.tile_size
                )
                if player_rect.colliderect(tile_rect):
                    # Makes sure there are no more enemies left in that level
                    if len(self.enemies) == 0:
                        # If the player is on the last floor in chapter 1, move on to chapter 2
                        if self.current_chapter == 1 and self.current_map_id == 4:
                            self.current_chapter = 2
                            ChapterScreen("Chapter 2 - Frozen Bastion",
                                          bonuses=["Health +2", "Damage +2", "Dash Unlocked (Right Shift)"]).run()
                            self.player.reset_health_potions()
                            self.movement = [False, False]
                            self.player.HP_up()
                            self.next_level()
                            return

                        # If the player is on the last room in chapter 2, move on to chapter 3
                        elif self.current_chapter == 2 and self.current_map_id == 9:
                            self.current_chapter = 3
                            ChapterScreen("Chapter 3 - Ember Vaults",
                                          bonuses=["Health +2", "Damage +2", "Double Jump Unlocked"]).run()
                            self.player.reset_health_potions()
                            self.movement = [False, False]
                            self.player.HP_up()
                            self.next_level()
                            return

                        # If the player is on the last room in chapter 3, move on to chapter 4
                        elif self.current_chapter == 3 and self.current_map_id == 14:
                            self.current_chapter = 4
                            ChapterScreen("Chapter 4 - Storm Spire",
                                          bonuses=["Health +2", "Damage +2", "Special Attack Unlocked (K)"]).run()
                            self.player.reset_health_potions()
                            self.movement = [False, False]
                            self.player.HP_up()
                            self.next_level()
                            return

                        # If the player is on the last room in chapter 4, move on to chapter 5
                        elif self.current_chapter == 4 and self.current_map_id == 19:
                            self.current_chapter = 5
                            ChapterScreen("Chapter 5 - The Astral Apex",
                                          bonuses=["Health +2", "Damage +2", "Phantom Step Unlocked (Right Shift)"]).run()
                            self.player.reset_health_potions()
                            self.movement = [False, False]
                            self.player.HP_up()
                            self.next_level()
                            return

                        # If the player is on the last room on chapter 5, the user gets sent to the game over screen
                        elif self.current_chapter == 5 and self.current_map_id == 24:
                            self.menu_stack.clear()
                            self.menu_stack.push(GameOverScreen())
                            self.movement = [False, False]
                            return

                        # If the player is in a room thats not the last room of a chapter, move on to the next level
                        self.next_level()
                    break


    def load_level(self, map_id):
        # Dict mapping spawner tile variants to what they should create in the level
        SPAWNER_TYPES = {
            0: "player",
            1: Enemy,
            2: WeakEnemy,
            3: FrostWarden,
            4: BlizzardShaman,
            5: FlameHound,
            6: FireballCaster,
            7: CloudshotGolem,
            8: SkyFlayer,
            9: BlinkingAssassin,
            10: ShadowMage,
            11: Collectible
        }

        # Stores which map is currently loaded
        self.current_map_id = map_id

        # Load the tilemap data from the JSON file for this level
        self.tilemap.load('assets/images/maps/' + str(map_id) + '.json')



        # Clears lists so enemies and collectibles from previous levels are removed
        self.collectibles = []
        self.enemies = []

        # Find all spawner tiles in the map
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3), ('spawners', 4),('spawners', 5), ('spawners', 6), ('spawners', 7), ('spawners', 8), ('spawners', 9), ('spawners', 10), ('spawners', 11) ], keep=True):
            variant = spawner['variant']
            pos = spawner['pos']

            spawn_type = SPAWNER_TYPES.get(variant)
            # If the spawner is for the player, set their spawn
            if spawn_type == "player":
                self.spawn_pos = pos
                self.player.pos = self.spawn_pos.copy()
            # If it is an enemy, create that enemy and add to the list
            elif spawn_type and not spawn_type == Collectible:
                self.enemies.append(spawn_type(self, pos, (10, 15)))
            # If it is a collectible, create and store it separately
            elif spawn_type == Collectible:
                self.collectibles.append(Collectible(self, pos, (8, 8)))

    # Saves the game when the player presses save and quit
    def save_game(self):
        # All the data that is saved
        data = {
            "player": {
                "health": self.player.health_max,
                "stamina": self.player.stamina_max,
                "pos": self.start_pos,
                "abilities": {
                    "dash": self.player.can_dash,
                    "double_jump": self.player.can_double_jump,
                    "special_attack": self.player.can_special,
                    "phantom_step": self.player.can_phantom_step
                }
            },
            "world": {
                "current_map": self.current_map_id,
                "current_chapter": self.current_chapter,
                "background_index": self.current_map_id
            },
            "controls": self.controls
        }

        os.makedirs("saves", exist_ok=True)
        with open("saves/save.json", "w") as f:
            json.dump(data, f, indent=4)

    # loads saved game when player presses continue game
    def load_game(self):
        # If there is no save file then load_game does nothing
        if not os.path.exists(SAVE_FILE):
            return

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        # Retrieves data for the world, including map_id, current_chapter and chapter abilities
        world = data.get("world", {})
        self.current_map_id = world.get("current_map", 0)
        self.current_chapter = world.get("current_chapter", 1)
        self.player.apply_chapter_abilities(self.current_chapter)

        # Retrieves data for the current background
        bg_index = world.get("background_index", 0)
        self.current_background = self.assets['backgrounds'][bg_index]

        self.load_level(self.current_map_id)

        # Retrieves data for the player, including player health, player stamina, and the player position
        player_data = data.get("player", {})
        self.player.health = player_data.get("health", self.player.health_max)
        self.player.stamina = player_data.get("stamina", self.player.stamina_max)
        self.player.pos = player_data.get("pos", self.start_pos.copy())

        # Retrieves data for abilities, including whether the player can dash, double jump, special attack and phantom step
        abilities = player_data.get("abilities", {})
        self.player.can_dash = abilities.get("dash", False)
        self.player.can_double_jump = abilities.get("double_jump", False)
        self.player.can_special = abilities.get("special_attack", False)
        self.player.can_phantom_step = abilities.get("phantom_step", False)

        # Retrieves data for the saved controls
        saved_controls = data.get("controls", {})
        # Updates current controls with any saved custom keybinds
        self.controls = {**self.controls, **saved_controls}

    # Starts new game, called when player presses new game in the main menu or presses play again in the game over screen
    def start_new_game(self):
        self.player.collect_count = 0
        self.collectibles = []
        self.load_level(0)
        self.player.health = self.player.health_max
        self.player.stamina = self.player.stamina_max
        self.player.reset_health_potions()
        self.player.pos = self.spawn_pos.copy()
        self.player.velocity = [0, 0]
        self.player.jumps = 1
        self.current_chapter = 1
        self.player.apply_chapter_abilities(self.current_chapter)
        self.current_background = self.assets['backgrounds'][0]

        ChapterScreen("Chapter 1 - Tower Depths",
                      bonuses=["A/D - Move", "SPACE - Jump", "J - Attack", "H - Heal"]).run()


    def run(self):
        while True:
            # If there is a menu on the stack, run it and handle its result
            if not self.menu_stack.is_empty():
                current_menu = self.menu_stack.peek()
                result = current_menu.run()
                current_menu.handle_result(result)
                continue

            # Draw the current background
            self.display.blit(self.current_background, (0, 0))
            # Render the level tilemap onto the display
            self.tilemap.render(self.display)

            # Checks if the player has reached an exit point
            self.check_exit_collision()

            # Update and render all enemies
            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display)


            # Calculate horizontal player movement
            player_movement = (int(self.movement[1]) - int(self.movement[0]), 0)

            # Update player physics and position
            self.player.update(self.tilemap, player_movement)

            # Handles players death
            if self.player.health <= 0:
                self.load_level(self.current_map_id)
                self.player.health = self.player.health_max
                self.player.pos = self.spawn_pos.copy()
                self.player.velocity = [0, 0]
                self.player.jumps = self.player.max_jumps

            # Renders the player sprite
            self.player.render(self.display)

            # Updates slash attack arcs and removes finished ones
            self.slash_arcs = [slash for slash in self.slash_arcs if slash.update()]
            # Update visual effects and remove finished ones
            self.effects = [effect for effect in self.effects if effect.update()]
            # Update collectibles and remove collected ones
            self.collectibles = [collectible for collectible in self.collectibles if collectible.update()]
            # Update particles and remove finished ones
            self.particles = [particle for particle in self.particles if particle.update()]

            # Render collectibles
            for collectible in self.collectibles:
                collectible.render(self.display)

            # Render effects
            for effect in self.effects:
                effect.render(self.display)

            # Render slash arcs
            for slash in self.slash_arcs:
                slash.render(self.display)

            # Draw particles
            for particle in self.particles:
                particle.draw(self.display)

            # Update projectiles
            # Handles collisions with player
            for projectile in self.projectiles[:]:
                if not projectile.update(self.tilemap):
                    self.projectiles.remove(projectile)
                elif projectile.rect().colliderect(self.player.rect()):
                    self.player.take_damage(1)
                    self.projectiles.remove(projectile)

            # Render projectiles
            for projectile in self.projectiles:
                projectile.render(self.display)

            # Update damage number
            self.damage_numbers = [damage_num for damage_num in self.damage_numbers if damage_num.update()]
            # Render damage numbers
            for damage_num in self.damage_numbers:
                damage_num.render(self.display, self.assets.get('font', self.assets['font']))

            # Flash the screen red if the player takes damage
            if self.player.damage_flash_timer > 0:
                flash = pygame.Surface(self.display.get_size())
                flash.fill(RED)
                flash.set_alpha(100)
                self.display.blit(flash, (0, 0))
                self.player.damage_flash_timer -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # If the user presses Esc the Pause menu is opened
                        self.menu_stack.push(PauseMenu())
                        self.movement = [False, False]
                    if event.key ==pygame.K_n:
                        self.next_level()


                    if event.key == self.controls["Move Left"]:
                        self.movement[0] = True
                    if event.key == self.controls["Move Right"]:
                        self.movement[1] = True
                    if event.key == self.controls["Jump"]:
                        self.player.jump()
                        self.player.double_jump()
                    if event.key == self.controls["Dash"]:
                        self.player.dash()
                        self.player.phantom_step()
                    if event.key == self.controls["Attack"]:
                        self.player.attack()
                    if event.key == self.controls["Special_Attack"]:
                        self.player.special_attack()
                    if event.key == self.controls["Heal"]:
                        self.player.use_health_potions()
                if event.type == pygame.KEYUP:
                    if event.key == self.controls["Move Left"]:
                        self.movement[0] = False
                    if event.key == self.controls["Move Right"]:
                        self.movement[1] = False
                    if event.key == self.controls["Jump"]:
                        self.player.jump_pressed = False


            # Draws the health bar
            pygame.draw.rect(self.display, DARK_GREY, (HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
            current_width = int((self.player.health / self.player.health_max) * HEALTH_BAR_WIDTH)
            pygame.draw.rect(self.display, RED, (HEALTH_BAR_X, HEALTH_BAR_Y, current_width, HEALTH_BAR_HEIGHT))
            pygame.draw.rect(self.display, BLACK, (HEALTH_BAR_X, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 2)
            
    

            # Draws the stamina bar
            pygame.draw.rect(self.display, DARK_GREY, (STAMINA_X, STAMINA_Y, STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT))
            stamina_fill_width = int((self.player.stamina / self.player.stamina_max) * STAMINA_BAR_WIDTH)
            pygame.draw.rect(self.display, GREEN, (STAMINA_X, STAMINA_Y, stamina_fill_width, STAMINA_BAR_HEIGHT))
            pygame.draw.rect(self.display, BLACK, (STAMINA_X, STAMINA_Y, STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT), 2)

            # Render health potions
            self.player.render_health_potions(self.display, 20, 50)
            # Render collectibles
            self.player.render_collectibles_count(self.display, 12, 60, font=pygame.font.SysFont(FONT_NAME, 20))

            # Scales the render surface to the actual window
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)


game = Game()
game.menu_stack.push(MainMenu())
game.run()
