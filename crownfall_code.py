# Amogh R and Sebastian M || CROWNFALL
import pygame, os, math, random
pygame.init()
os.chdir(os.path.dirname(__file__))  # Make working dir = script folder

# CONSTANTS
ROOM_WIDTH = 800
ROOM_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
MAX_UPGRADE_LEVEL = 5

# Basic set up
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)
title_font = pygame.font.SysFont(None, 80)

# Player and Room setup@
player = pygame.Rect(50, ROOM_HEIGHT - 100, 50, 50)
player_speed = 10
facing = "up" # Track direction player is facing
player_color = (255, 255, 0)
current_room = [0, 0, 0]
room_colliders = {}

# Speed setup
base_speed = 10
speed_potion_duration = 0  # Seconds remaining on active potions
speed_multiplier = 2

# Strength setup
damage_multiplier = 1
strength_potion_duration = 0  # Seconds remaining on active strength potion
strength_multiplier = 2

# Health set up
health = 100
max_health = 100

# Inventory set up
inventory = {"Gold": 0, "Artifacts": 0, "Health Potions": 0, "Speed Potions": 0, "Strength Potions": 0, "Upgrade Tokens": 0}
inventory_limits = {"Gold": 150, "Artifacts": 7, "Health Potions": 3, "Speed Potions": 3, "Strength Potions": 3, "Upgrade Tokens": 15}

# Collected sets
c_Artifacts = set()
c_Gold = set()
c_Health_Potions = set()
c_Speed_Potions = set()
c_Strength_Potions = set()

# On-screen notifications
message = ""
message_color = None
message_timer = 0.0
feedback = ""
feedback_timer = 0.0

# Flag variables
on_home = True # Player starts in home area
hud_visible = False # HUD hidden by default
map_visible = False # Map hidden by default
dialogue_active = False # No dialogue active at start
trading_prompt_active = False # Trade prompt not showing
trade_menu_active = False # Trade menu closed
upgrade_menu_active = False # Uograde menu closed
instructions_active = False # Instructions screen flag
trade_prompt_key = None # Tracks which villager is offering trade
trade_pending_key = None # Marks villager to show trade prompt after dialogue
active_villager_index = None # Which villager for multiple in a room

# Armor and Weapons set up
armor_level = 0  # Player's armor upgrade level (increases max health)
weapon_level = 0  # Player's weapon upgrade level (increases damage)
inventory_level = 0  # Player's inventory-size upgrade level (increases limits)
gold_pickup_level = 0  # Gold-per-pickup upgrade level
# Base multipliers derived from upgrades
weapon_base_multiplier = 1.0  # Multiplied into damage (combined with strength potions)
# UI selection index for upgrade menu (0 = Armor, 1 = Weapons, 2 = Inventory, 3 = Gold Pickup)
upgrade_selection = 0

# Gold pickup upgrade set up
gold_per_pickup_base = 10  # Base gold pickup amount
gold_per_pickup = gold_per_pickup_base + gold_pickup_level * 10  # Base pickup amount + 5 * 10 = 50 per pickup

# Globals used by draw_objects (will be set per-room in draw_room)
colliders = []
artifacts = []
gold = []
health_potions = []
speed_potions = []
strength_potions = []

# Tile collisions, interating with more then just collectables
water_tiles = []
villager_tiles = []
upgrade_hut_tiles = []

# Dialogue set up
dialogue_index = 0
current_dialogue = []

# Key format = (level, row, column, villager_index)
dialogues = {
    # LEVEL 1: bottom middle villager
    (0, 0, 1, 0): [
        "Villager: LALALA!",
        "Villager: BLA BLA",
        "Villager: Bye!"],
    # LEVEL 1: middle left villager
    (0, 1, 0, 0): [
        "Villager: STORY THINGS",
        "Villager: More story things"],
    # LEVEL 1: bottom right villager
    (0, 0, 2, 0): [
        "Villager: Sebastian, do something",
        "Villager: I wanna go to sleep"],
    # LEVEL 2: bottom right villagers
    (1, 0, 2, 0): [
        "Villager: I don't have a normal sleep schedule",
        "Villager: It's 4:12 am right now"],
    (1, 0, 2, 1): [
        "Villager: I am hungry",
        "Villager: I need to get some food"],
    (1, 0, 2, 2): [
        "Villager: AI is going to take my job",
        "Villlager: Im going to be jobless if I pick this as my job"],
    # LEVEL 3: bottom middle villagers
    (2, 0, 1, 0): [
        "Villager: I have a headache",
        "Villager: I need water"],
    (2, 0, 1, 1): [
        "Villager: Pokemon",
        "Villager: Knock, Knick. Whos there. IDK"],
}

# Trade set up
tradeable_villagers = { # Which villager keys are tradeable
    (0, 0, 1, 0),  # Level 1 bottom middle
    (1, 0, 2, 1),  # Level 2 bottom right (middle villager)
    (2, 0, 1, 0),  # Level 3 bottom middle (left villager)
}
trade_selection = 0
# (inventory key, price)
trade_items = [("Health Potions", 30), ("Speed Potions", 10), ("Strength Potions", 20), ("Upgrade Tokens", 20)]

# Upgrade cost level tables
upgrade_costs_gold = [10, 20, 30, 40, 50]  # Gold cost per level
upgrade_costs_tokens = [1, 2, 3, 4, 5]     # Token cost per level

# DRAWING ELEMENTS
def draw_objects(x, y, obj_type, surface):
    """Draws an object on the game surface and adds its collider or collectible
    reference to the appropriate list based on object type."""
    global colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles

    def load_img(name, w, h, offset=(0, 0)):
        """Loads, scales, trims transparent padding, draws the image and returns the rect."""
        img = pygame.image.load(f"crownfall_images/{name}.png").convert_alpha()

        # Scale up or down (if needed)
        w2, h2 = scale(name, w, h)
        w2, h2 = int(w2), int(h2)
        img = pygame.transform.scale(img, (w2, h2))

        # Draw to surface at anchor (x - offset[0], y - offset[1])
        draw_x = x - offset[0]
        draw_y = y - offset[1]
        surface.blit(img, (draw_x, draw_y))

        # Trim transparent padding so collider matches visible pixels only
        trim_rect = img.get_bounding_rect()
        rect = pygame.Rect(draw_x + trim_rect.x, draw_y + trim_rect.y, trim_rect.width, trim_rect.height)
        # Slightly shrink collider for smoother player contact
        rect.inflate_ip(-5, -5)
        return rect

    def scale(name, w, h):
        """Returns scaled width & height if object should be scaled up or down."""
        # Only certain objects were flagged to scale 1.5x and .75x
        scale_up_list = {"Rock_1", "Rock_2", "Wall_1", "Wall_2"}
        scale_down_list = {"Villager", "Gold"}
        if name in scale_up_list:
            return w * 1.5, h * 1.5
        elif name in scale_down_list:
            return w * .75, h * .75
        else:
            return w, h

    # environment objects
    if obj_type == "tree1":
        rect = load_img("Tree_1", 200, 250)
        colliders.append(rect)
        return rect
    elif obj_type == "tree2":
        rect = load_img("Tree_2", 150, 200)
        colliders.append(rect)
        return rect
    elif obj_type == "rock1":
        rect = load_img("Rock_1", 100, 100)
        colliders.append(rect)
        return rect
    elif obj_type == "rock2":
        rect = load_img("Rock_2", 50, 75)
        colliders.append(rect)
        return rect
    elif obj_type == "house1":
        rect = load_img("House_1", 300, 300)
        colliders.append(rect)
        return rect
    elif obj_type == "house2":
        rect = load_img("House_2", 500, 250)
        colliders.append(rect)
        return rect
    elif obj_type == "wall1":
        rect = load_img("Wall_1", 200, 150)
        colliders.append(rect)
        return rect
    elif obj_type == "wall2":
        rect = load_img("Wall_2", 150, 200)
        colliders.append(rect)
        return rect
    
    # Interactables 
    elif obj_type == "villager":
        rect = load_img("Villager", 100, 200)
        colliders.append(rect)
        villager_tiles.append(rect)
        return rect
    elif obj_type == "water":
        rect = load_img("Water", 400, 400)
        water_tiles.append(rect)
        return rect
    elif obj_type == "upgrade_hut":
        rect = load_img("Upgrade_Hut", 300, 300)
        colliders.append(rect)
        upgrade_hut_tiles.append(rect)
        return rect

    # Collectibles 
    elif obj_type == "artifact":
        rect = load_img("Artifact", 40, 40)
        artifacts.append((rect, x, y))
        return rect
    elif obj_type == "gold":
        rect = load_img("Gold", 50, 50)
        gold.append((rect, x, y))
        return rect
    elif obj_type == "health_potion":
        rect = load_img("Health_Potion", 40, 40)
        health_potions.append((rect, x, y))
        return rect
    elif obj_type == "speed_potion":
        rect = load_img("Speed_Potion", 40, 40)
        speed_potions.append((rect, x, y))
        return rect
    elif obj_type == "strength_potion":
        rect = load_img("Strength_Potion", 40, 40)
        strength_potions.append((rect, x, y))
        return rect

    return None  # Fallback

# DRAWING ROOMS
def draw_room(surface, level, row, col, c_Artifacts, c_Gold, c_Health_Potions):
    """Draws the current room based on the level, row, and column.  2
    Adds interactive and environmental objects to their respective lists."""
    global colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles, upgrade_hut_tiles

    # Draw background
    bg = pygame.image.load("crownfall_images/Level_bg_1.jpg").convert()
    bg = pygame.transform.scale(bg, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(bg, (0, 0))

    # Object containers for this room
    colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles, upgrade_hut_tiles = [], [], [], [], [], [], [], [], []

    def can_draw(anchor_x, anchor_y, set):
        """checks if a collectable should be drawn on the screen"""
        return (level, row, col, anchor_x, anchor_y) not in set

    # ----- LEVEL 1 -----
    # Level 1 Bottom Left
    if level == 0 and row == 0 and col == 0:
        draw_objects(400, 250, "house1", surface)  # House 1
        draw_objects(245, 320, "tree1", surface)   # Tree 1
        draw_objects(25, 50, "rock1", surface)     # Rock 1
        draw_objects(175, 25, "rock2", surface)    # Rock 2
        if can_draw(600, 150, c_Artifacts):
            draw_objects(600, 150, "artifact", surface)  # Artifact

    # Level 1: Bottom Middle
    elif level == 0 and row == 0 and col == 1:
        draw_objects(570, 320, "tree2", surface)  # Tree 2
        draw_objects(350, 250, "rock2", surface)  # Rock 2
        draw_objects(450, 100, "villager", surface)  # Villager
        if can_draw(400, 500, c_Gold):
            draw_objects(400, 500, "gold", surface)  # Gold
        if can_draw(150, 25, c_Speed_Potions):
            draw_objects(150, 25, "speed_potion", surface)  # Speed Potion
        if can_draw(300, 50, c_Strength_Potions):
            draw_objects(300, 50, "strength_potion", surface)  # Strength Potion

    # Level 1: Bottom Right
    elif level == 0 and row == 0 and col == 2:
        draw_objects(350, 150, "house2", surface)  # House 2
        draw_objects(120, 220, "tree1", surface)   # Tree 1
        draw_objects(450, 500, "rock1", surface)   # Rock 1
        draw_objects(600, 400, "villager", surface)  # Villager
        if can_draw(700, 100, c_Artifacts):
            draw_objects(700, 100, "artifact", surface)  # Artifact

    # Level 1: Middle Left
    elif level == 0 and row == 1 and col == 0:
        draw_objects(245, 270, "tree1", surface)  # Tree 1
        draw_objects(600, 350, "rock1", surface)  # Rock 1
        draw_objects(25, 25, "villager", surface)  # Villager
        if can_draw(400, 150, c_Health_Potions):
            draw_objects(400, 150, "health_potion", surface)  # Health Potion
        if can_draw(700, 500, c_Gold):
            draw_objects(700, 500, "gold", surface)  # Gold

    # Level 1: Middle
    elif level == 0 and row == 1 and col == 1:
        draw_objects(400, 250, "house1", surface)  # House 1
        draw_objects(150, 180, "tree1", surface)   # Tree 1
        if can_draw(600, 150, c_Gold):
            draw_objects(600, 150, "gold", surface)  # Gold
        if can_draw(700, 400, c_Artifacts):
            draw_objects(700, 400, "artifact", surface)  # Artifact

    # Level 1: Middle Right
    elif level == 0 and row == 1 and col == 2:
        draw_objects(100, 200, "rock2", surface)  # Rock 2
        if can_draw(500, 250, c_Speed_Potions):
            draw_objects(500, 250, "speed_potion", surface)  # Speed Potion
        draw_objects(400, 400, "water", surface)  # Water

    # Level 1: Top Left
    elif level == 0 and row == 2 and col == 0:
        draw_objects(220, 245, "tree1", surface)  # Tree 1
        draw_objects(400, 400, "rock1", surface)  # Rock 1
        draw_objects(400, 100, "upgrade_hut", surface) # Upgrade hut
        if can_draw(200, 150, c_Gold):
            draw_objects(200, 150, "gold", surface)  # Gold

    # Level 1: Top Middle
    elif level == 0 and row == 2 and col == 1:
        draw_objects(620, 170, "tree2", surface)  # Tree 2
        draw_objects(200, 25, "house1", surface)  # House 1
        if can_draw(100, 200, c_Health_Potions):
            draw_objects(100, 200, "health_potion", surface)  # Health Potion
        if can_draw(50, 100, c_Gold):
            draw_objects(50, 100, "gold", surface)  # Gold

    # Level 1: Top Right
    elif level == 0 and row == 2 and col == 2:
        if can_draw(200, 150, c_Gold):
            draw_objects(200, 150, "gold", surface)  # Gold

    # ----- LEVEL 2 -----
    # Level 2: Bottom Left
    if level == 1 and row == 0 and col == 0:
        draw_objects(620, 420, "tree2", surface)  # Tree 2
        if can_draw(100, 100, c_Gold):
            draw_objects(100, 100, "gold", surface)  # Gold
        if can_draw(500, 350, c_Health_Potions):
            draw_objects(500, 350, "health_potion", surface)  # Health potion

    # Level 2: Bottom Middle
    elif level == 1 and row == 0 and col == 1:
        draw_objects(400, 300, "rock2", surface)  # Rock 2
        draw_objects(200, 170, "tree1", surface)  # Tree 1

    # Level 2: Bottom Right
    elif level == 1 and row == 0 and col == 2:
        draw_objects(-200, 200, "wall1", surface) # Wall 1
        draw_objects(0, 200, "wall1", surface) # Wall 1
        draw_objects(200, 200, "wall1", surface) # Wall 1
        draw_objects(600, 200, "wall1", surface) # Wall 1
        draw_objects(-130, 500, "wall2", surface) # Wall 2
        draw_objects(-130, 450, "wall2", surface) # Wall 2
        draw_objects(-130, 400, "wall2", surface) # Wall 2
        draw_objects(-130, 350, "wall2", surface) # Wall 2
        draw_objects(200, 400, "villager", surface) # Villager
        draw_objects(400, 350, "villager", surface) # Villager
        draw_objects(650, 400, "villager", surface) # Villager

    # Level 2: Middle Left
    elif level == 1 and row == 1 and col == 0:
        draw_objects(300, 250, "rock1", surface) # Rock 1
        draw_objects(520, 420, "tree2", surface) # Tree 2
        draw_objects(715, 0, "wall1", surface) # Wall 1
        draw_objects(600, -100, "wall2", surface) # Wall 2
        if can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion
        if can_draw(150, 300, c_Speed_Potions):
            draw_objects(150, 300, "speed_potion", surface) # Speed Potion
        if can_draw(200, 200, c_Strength_Potions):
            draw_objects(200, 200, "strength_potion", surface) # Strength Potion

    # Level 2: Middle
    elif level == 1 and row == 1 and col == 1:
        draw_objects(-100, 0, "wall1", surface) # Wall 1
        draw_objects(0, 0, "wall1", surface) # Wall 1
        draw_objects(200, 0, "wall1", surface) # Wall 1
        draw_objects(600, 0, "wall1", surface) # Wall 1
        if can_draw(400, 400, c_Health_Potions):
            draw_objects(400, 400, "health_potion", surface) # Health Potion
        if can_draw(700, 200, c_Gold):
            draw_objects(700, 200, "gold", surface) # Gold

    # Level 2: Middle Right
    elif level == 1 and row == 1 and col == 2:
        draw_objects(-100, 0, "wall1", surface) # Wall 1
        draw_objects(0, 0, "wall1", surface) # Wall 1
        draw_objects(200, 0, "wall1", surface) # Wall 1
        draw_objects(400, 0, "wall1", surface) # Wall 1
        draw_objects(600, 0, "wall1", surface) # Wall 1
        draw_objects(100, 350, "tree1", surface) # Tree 1
        draw_objects(550, 400, "upgrade_hut", surface) # Upgrade hut
        if can_draw(500, 300, c_Artifacts):
            draw_objects(500, 300, "artifact", surface) # Artifact

    # Level 2: Top Left
    elif level == 1 and row == 2 and col == 0:
        draw_objects(600, -200, "wall2", surface) # Wall 2
        draw_objects(600, 0, "wall2", surface) # Wall 2
        draw_objects(600, 200, "wall2", surface) # Wall 2
        draw_objects(600, 400, "wall2", surface) # Wall 2
        draw_objects(400, 300, "rock1", surface) # Rock 1
        draw_objects(220, 220, "tree2", surface) # Tree 2
        if can_draw(450, 100, c_Artifacts):
            draw_objects(450, 100, "artifact", surface) # Artifact

    # Level 2: Top Middle
    elif level == 1 and row == 2 and col == 1:
        if can_draw(300, 250, c_Health_Potions):
            draw_objects(300, 250, "health_potion", surface) # Health Potion
        if can_draw(500, 350, c_Artifacts):
            draw_objects(500, 350, "artifact", surface) # Artifact
        if can_draw(700, 150, c_Gold):
            draw_objects(700, 150, "gold", surface) # Gold
        if can_draw(100, 450, c_Gold):
            draw_objects(100, 450, "gold", surface) # Gold

    # Level 2: Top Right
    elif level == 1 and row == 2 and col == 2:
        if can_draw(400, 300, c_Gold):
            draw_objects(400, 300, "gold", surface) # Gold
        if can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion

    # ----- LEVEL 3 -----
    # Level 3: Bottom Left
    if level == 2 and row == 0 and col == 0:
        draw_objects(200, 300, "tree1", surface) # Tree 1
        draw_objects(400, 300, "water", surface) # Water

    # Level 3: Bottom Middle
    elif level == 2 and row == 0 and col == 1:
        draw_objects(100, 300, "villager", surface) # Villager
        draw_objects(500, 300, "villager", surface) # Villager
        draw_objects(620, 160, "tree1", surface) # Tree 1

    # Level 3: Bottom Right
    elif level == 2 and row == 0 and col == 2:
        draw_objects(20, 170, "tree1", surface) # Tree 1
        if can_draw(700, 25, c_Gold):
            draw_objects(700, 25, "gold", surface) # Gold
        if can_draw(700, 500, c_Health_Potions):
            draw_objects(700, 500, "health_potion", surface) # Health Potion
        if can_draw(500, 250, c_Speed_Potions):
            draw_objects(500, 250, "speed_potion", surface) # Speed Potion
        if can_draw(600, 300, c_Strength_Potions):
            draw_objects(600, 300, "strength_potion", surface) # Strength Potion
        draw_objects(500, 600, "water", surface)

    # Level 3: Middle Left
    elif level == 2 and row == 1 and col == 0:
        draw_objects(400, 300, "rock2", surface) # Rock 2
        draw_objects(170, 170, "tree2", surface) # Tree 2
        draw_objects(400, 100, "upgrade_hut", surface) # Upgrade hut

        if can_draw(350, 200, c_Health_Potions):
            draw_objects(350, 200, "health_potion", surface) # Health Potion

    # Level 3: Middle
    elif level == 2 and row == 1 and col == 1:
        draw_objects(300, 100, "house2", surface) # House 2
        if can_draw(700, 25, c_Gold):
            draw_objects(700, 25, "gold", surface) # Gold

    # Level 3: Middle Right
    elif level == 2 and row == 1 and col == 2:
        draw_objects(220, 320, "tree2", surface) # Tree
        if can_draw(50, 100, c_Health_Potions): 
            draw_objects(50, 100, "health_potion", surface) # Health Potion
        if can_draw(500, 200, c_Gold):
            draw_objects(500, 200, "gold", surface) # Gold
        if can_draw(400, 450, c_Speed_Potions):
            draw_objects(400, 450, "speed_potion", surface) # Speed Potion
        if can_draw(450, 400, c_Strength_Potions):
            draw_objects(450, 400, "strength_potion", surface) # Strength Potion

    # Level 3: Top Left
    elif level == 2 and row == 2 and col == 0:
        draw_objects(270, 120, "tree1", surface) # Tree 1

    # Level 3: Top Middle
    elif level == 2 and row == 2 and col == 1:
        draw_objects(20, 170, "tree1", surface) # Tree 1
        draw_objects(420, 270, "tree2", surface) # Tree 2
        if can_draw(500, 25, c_Gold):
            draw_objects(500, 25, "gold", surface) # Gold
        if can_draw(400, 600, c_Gold):
            draw_objects(400, 600, "gold", surface) # Gold

    # Level 3: Top Right
    elif level == 2 and row == 2 and col == 2:
        if can_draw(600, 250, c_Gold):
            draw_objects(600, 250, "gold", surface) # Gold

# DRAWING HUD
def draw_hud(surface):
    """Draws the player HUD (health + inventory) when visible."""
    if not hud_visible:
        return  # Don't draw anything if HUD is hidden

    global map_visible
    if map_visible:
        map_visible = not map_visible # Turn off map when HUD is visible

    draw_overlay(surface)

    # --- Health bar ---
    box_width = 520
    box_height = 52
    box_x = (ROOM_WIDTH - box_width) // 2
    box_y = 10
    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

    label = font.render("Health", True, (255, 255, 255))
    surface.blit(label, (box_x + 12, box_y + 8))

    bar_x = box_x + 110
    bar_y = box_y + 12
    bar_width = 380
    bar_height = 28
    pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, max(0, bar_width * (health / max_health)), bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    health_text = font.render(f"{int(health)} / {max_health}", True, (255, 255, 255))
    text_rect = health_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    surface.blit(font.render(f"{int(health)} / {max_health}", True, (0, 0, 0)), (text_rect.x + 1, text_rect.y + 1))
    surface.blit(health_text, text_rect)

    # --- Inventory ---
    inv_w = 520
    inv_h_line = 28
    inv_padding = 12
    inv_x = (ROOM_WIDTH - inv_w) // 2
    inv_y = box_y + box_height + 12

    num_items = len(inventory)
    inventory_height = inv_padding + num_items * inv_h_line + inv_padding + 30

    inventory_rect = pygame.Rect(inv_x, inv_y, inv_w, inventory_height)
    pygame.draw.rect(surface, (0, 0, 0), inventory_rect)
    pygame.draw.rect(surface, (255, 255, 255), inventory_rect, 2)

    inv_title = font.render("Inventory", True, (255, 255, 255))
    inv_title_rect = inv_title.get_rect(center=(ROOM_WIDTH // 2, inventory_rect.top + 18))
    surface.blit(inv_title, inv_title_rect)

    y = inventory_rect.top + 42
    left_pad = inventory_rect.left + 16
    for item, count in inventory.items():
        txt = font.render(f"{item}: {count}", True, (255, 255, 255))
        surface.blit(txt, (left_pad, y))
        y += inv_h_line

    # --- Upgrades (armor/weapon) ---
    aw_box_w = 520
    aw_box_h = 84
    aw_box_x = inv_x
    aw_box_y = inventory_rect.bottom + 8
    pygame.draw.rect(surface, (0, 0, 0), (aw_box_x, aw_box_y, aw_box_w, aw_box_h))
    pygame.draw.rect(surface, (255, 255, 255), (aw_box_x, aw_box_y, aw_box_w, aw_box_h), 2)

    aw_title = font.render("Upgrades", True, (255, 255, 255))
    aw_title_rect = aw_title.get_rect(center=(ROOM_WIDTH // 2, aw_box_y + 18))
    surface.blit(aw_title, aw_title_rect)

    armor_txt = font.render(f"Armor Level: {armor_level}", True, (255, 255, 255))
    weapon_txt = font.render(f"Weapon Level: {weapon_level}", True, (255, 255, 255))
    surface.blit(armor_txt, (aw_box_x + 12, aw_box_y + 44))
    surface.blit(weapon_txt, (aw_box_x + 240, aw_box_y + 44))

    # --- Gold per pickup box inventory ---
    pickup_box_w = 300
    pickup_box_h = 60
    pickup_box_x = (ROOM_WIDTH - pickup_box_w) // 2
    pickup_box_y = aw_box_y + aw_box_h + 10

    pygame.draw.rect(surface, (0, 0, 0), (pickup_box_x, pickup_box_y, pickup_box_w, pickup_box_h))
    pygame.draw.rect(surface, (255, 255, 255), (pickup_box_x, pickup_box_y, pickup_box_w, pickup_box_h), 2)

    current_gold_pickup = gold_per_pickup_base + gold_pickup_level * 10
    pickup_txt = font.render(f"Picking up +{current_gold_pickup} gold", True, (255, 255, 255))
    pickup_lvl_txt = font.render(f"(Level {gold_pickup_level})", True, (255, 255, 255))
    pickup_txt_rect = pickup_txt.get_rect(center=(ROOM_WIDTH // 2, pickup_box_y + 22))
    pickup_lvl_rect = pickup_lvl_txt.get_rect(center=(ROOM_WIDTH // 2, pickup_box_y + 44))
    surface.blit(pickup_txt, pickup_txt_rect)
    surface.blit(pickup_lvl_txt, pickup_lvl_rect)

    # --- MINI-MAP ---
    # Draw a small minimap of the current room
    map_size = 90
    cell_size = map_size // GRID_WIDTH
    map_x = (ROOM_WIDTH - map_size) // 2
    map_y = pickup_box_y + pickup_box_h + 20

    pygame.draw.rect(surface, (0, 0, 0), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    pygame.draw.rect(surface, (255, 255, 255), (map_x - 5, map_y - 5, map_size + 10, map_size + 10), 2)

    level, row, col = current_room
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            x = map_x + c * cell_size
            y = map_y + (GRID_HEIGHT - 1 - r) * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            if r == row and c == col:
                pygame.draw.rect(surface, (255, 255, 255), rect)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect, 1)

    # Draw the level text info 
    level_text = f"Level {level + 1} - {['Bottom', 'Middle', 'Top'][row]} {['Left', 'Middle', 'Right'][col]}"
    info_surf = font.render(level_text, True, (255, 255, 255))
    info_rect = info_surf.get_rect(center=(ROOM_WIDTH // 2, map_y + map_size + 16))

    pygame.draw.rect(surface, (0, 0, 0), (info_rect.left - 8, info_rect.top - 4, info_rect.width + 16, info_rect.height + 8))
    pygame.draw.rect(surface, (255, 255, 255), (info_rect.left - 8, info_rect.top - 4, info_rect.width + 16, info_rect.height + 8), 2)
    surface.blit(info_surf, info_rect)

    # --- Potion Effects Box ---
    effect_box_w = 520
    effect_box_h = 100
    effect_box_x = (ROOM_WIDTH - effect_box_w) // 2
    effect_box_y = info_rect.bottom + 12

    pygame.draw.rect(surface, (0, 0, 0), (effect_box_x, effect_box_y, effect_box_w, effect_box_h))
    pygame.draw.rect(surface, (255, 255, 255), (effect_box_x, effect_box_y, effect_box_w, effect_box_h), 2)

    effect_title = font.render("Active Effects", True, (255, 255, 255))
    effect_title_rect = effect_title.get_rect(center=(ROOM_WIDTH // 2, effect_box_y + 20))
    surface.blit(effect_title, effect_title_rect)

    y_offset = effect_box_y + 44
    if speed_potion_duration > 0:
        effect_text = font.render(f"{speed_multiplier}x speed ({int(speed_potion_duration)}s)", True, (0, 255, 255))
        effect_rect = effect_text.get_rect(center=(ROOM_WIDTH // 2, y_offset))
        surface.blit(effect_text, effect_rect)
        y_offset += 26
    if strength_potion_duration > 0:
        effect_text = font.render(f"{strength_multiplier}x damage ({int(strength_potion_duration)}s)", True, (255, 100, 100))
        effect_rect = effect_text.get_rect(center=(ROOM_WIDTH // 2, y_offset))
        surface.blit(effect_text, effect_rect)

# DRAWING TRADE PROMOPT
def draw_trade_prompt(surface):
    """Draws the simple yes/no prompt when near a tradeable villager."""
    if not trading_prompt_active:
        return # Dont draw anything if villager isn't tradeable

    box_w, box_h = 420, 120
    box_x = (ROOM_WIDTH - box_w) // 2
    box_y = ROOM_HEIGHT - box_h - 20
    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_w, box_h), 3)
    txt = font.render("Would u like to trade? (Y/N)", True, (255, 255, 255))
    trect = txt.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
    surface.blit(txt, trect)

# DRAW TRADEING SCREEN
def draw_trade_menu(surface):
    """Draw trade menu full-screen semi-transparent overlay with SHOP/INVENTORY/help and in-menu feedback"""
    if not trade_menu_active:
        return # Don't draw anything if not tradeing

    draw_overlay(surface)

    # Content box area (centered panel)
    box_w, box_h = ROOM_WIDTH - 120, ROOM_HEIGHT - 120
    box_x = (ROOM_WIDTH - box_w) // 2
    box_y = (ROOM_HEIGHT - box_h) // 2

    # Draw an inner panel to place text on (solid-ish)
    inner = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    inner.fill((25, 25, 25, 230))
    surface.blit(inner, (box_x, box_y))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_w, box_h), 3)

    # SHOP title
    shop_title = title_font.render("SHOP", True, (255, 255, 255))
    shop_title_rect = shop_title.get_rect(center=(box_x + box_w // 2, box_y + 50))
    surface.blit(shop_title, shop_title_rect)

    # Draw shop items area
    shop_area_x = box_x + 40
    shop_area_y = shop_title_rect.bottom + 10

    # Item headers
    hdr_item = font.render("Item", True, (255, 255, 255))
    hdr_price = font.render("Price", True, (255, 255, 255))
    hdr_qty = font.render("You", True, (255, 255, 255))
    surface.blit(hdr_item, (shop_area_x, shop_area_y))
    surface.blit(hdr_price, (box_x + box_w // 2, shop_area_y))
    surface.blit(hdr_qty, (box_x + box_w - 140, shop_area_y))

    # --- Item selection ---
    y = shop_area_y + 34
    for idx, (Item_key, price) in enumerate(trade_items):
        # Use simple indented arrow marker
        sell_marker = "     ->" if idx == trade_selection else "      "
        
        # Render the item name and selection arrow
        line = font.render(f"{sell_marker} {Item_key}", True, (255, 255, 255))
        # Draw the item name + arrow to the screen at the shop column position
        surface.blit(line, (shop_area_x, y))

        # Render the item's price in gold
        price_txt = font.render(f"{price} gold", True, (255, 255, 255))
        # Draw the item's price text in the middle section of the shop box
        surface.blit(price_txt, (box_x + box_w // 2, y))

        # Render the quantity of this item currently in the player's inventory
        qty_txt = font.render(str(inventory.get(Item_key, 0)), True, (255, 255, 255))
        # Draw the item quantity near the right edge of the shop box
        surface.blit(qty_txt, (box_x + box_w - 140, y))

        y += 40

    # Draw in-menu feedback
    feedback_y = y + 6
    if feedback:
        fb_surf = font.render(feedback, True, (255, 255, 255))
        fb_rect = fb_surf.get_rect(center=(box_x + box_w // 2, feedback_y))
        surface.blit(fb_surf, fb_rect)
    inventory_top = feedback_y + 40

    # INVENTORY title
    inventory_title = title_font.render("INVENTORY", True, (255, 255, 255))
    inventory_title_rect = inventory_title.get_rect(center=(box_x + box_w // 2, inventory_top))
    surface.blit(inventory_title, inventory_title_rect)

    # Draw inventory items under the inventory title
    inventory_y = inventory_title_rect.bottom + 8
    inventory_x_left = box_x + 40
    line_h = 28
    keys_list = list(inventory.keys())
    for i, item in enumerate(keys_list):
        txt = font.render(f"{item}: {inventory.get(item,0)}", True, (255, 255, 255))
        surface.blit(txt, (inventory_x_left, inventory_y + i * line_h))

    # --- BUY BUTTON ---
    # Upgrade button visual
    b_btn_w, b_btn_h = 220, 56
    b_btn_x = box_x + (box_w - b_btn_w) // 2
    b_btn_y = box_y + box_h - b_btn_h - 10
    b_btn_rect = pygame.Rect(b_btn_x, b_btn_y, b_btn_w, b_btn_h)
    pygame.draw.rect(surface, (100, 180, 100), b_btn_rect)
    pygame.draw.rect(surface, (255, 255, 255), b_btn_rect, 2)
    b_btn_txt = font.render("BUY", True, (255, 255, 255))
    b_btn_tr = b_btn_txt.get_rect(center= b_btn_rect.center)
    surface.blit(b_btn_txt, b_btn_tr)

    # --- SELL BUTTON ---
    s_btn_w, s_btn_h = 220, 56
    s_btn_x = box_x + (box_w - s_btn_w) // 2
    s_btn_y = box_y + box_h - s_btn_h - 75
    s_btn_rect = pygame.Rect(s_btn_x, s_btn_y, s_btn_w, s_btn_h)
    pygame.draw.rect(surface, (100, 0, 0), s_btn_rect)
    pygame.draw.rect(surface, (255, 255, 255), s_btn_rect, 2)
    s_btn_txt = font.render("SELL", True, (255, 255, 255))
    s_btn_tr = b_btn_txt.get_rect(center= s_btn_rect.center)
    surface.blit(s_btn_txt, s_btn_tr)

# DRAW UPGRADE SCREEN
def draw_upgrade_menu(surface):
    """Draw upgrade menu full-screen semi-transparent overlay with SHOP/INVENTORY/help and in-menu feedback"""
    if not upgrade_menu_active:
        return # Don't draw anything if not tradeing
    
    global gold_per_pickup

    draw_overlay(surface)

    # Content box area (centered panel)
    box_w, box_h = 700, 520
    box_x = (ROOM_WIDTH - box_w) // 2
    box_y = (ROOM_HEIGHT - box_h) // 2

    # Draw an inner panel to place text on (solid-ish)
    inner = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    inner.fill((20, 20, 30, 230))
    surface.blit(inner, (box_x, box_y))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_w, box_h), 3)

    # Title
    title = title_font.render("UPGRADE HUT", True, (255, 255, 255))
    title_rect = title.get_rect(center=(box_x + box_w//2, box_y + 44))
    surface.blit(title, title_rect)

    # Draw four category tabs (Armor, Weapons, Inventory, Gold)
    tabs = ["Armor", "Weapons", "Inventory", "Gold"]
    tab_x = box_x + 40
    tab_y = box_y + 100
    tab_w = (box_w - 40*2 - 20*3) // 4
    for i, t in enumerate(tabs):
        rect = pygame.Rect(tab_x + i * (tab_w + 20), tab_y, tab_w, 48)
        # Highlight selected
        if i == upgrade_selection:
            pygame.draw.rect(surface, (255, 215, 0), rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        else:
            pygame.draw.rect(surface, (30, 30, 30), rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        txt = font.render(t, True, (255, 255, 255))
        trect = txt.get_rect(center=rect.center)
        surface.blit(txt, trect)

    # Compute & display current level, next-level effects and costs
    info_x = box_x + 40
    info_y = tab_y + 80

    def get_costs_for_level(level):
        """Return (gold_cost, token_cost) for next level index 'level' (current level)."""
        if level >= MAX_UPGRADE_LEVEL:
            return None, None
        return upgrade_costs_gold[level], upgrade_costs_tokens[level]

    # Selected category string
    sel_cat = ["Armor", "Weapons", "Inventory", "Gold"][upgrade_selection]
    # Show current levels
    cur_level = {"Armor": armor_level, "Weapons": weapon_level, "Inventory": inventory_level, "Gold": gold_pickup_level}[sel_cat]
    # Costs
    next_cost_gold, next_cost_token = get_costs_for_level(cur_level)
    # Benefit description based on category
    if sel_cat == "Armor":
        benefit_desc = f"+50 Max Health per level"
    elif sel_cat == "Weapons":
        benefit_desc = f"x1.5 damage multiplier per level"
    elif sel_cat == "Inventory":
        benefit_desc = f"+50 gold slots, +2 potion slots, +5 token slots per level"
    else:
        benefit_desc = f"+10 gold per pickup per level"

    # Draw current level and benefit
    lvl_surf = font.render(f"{sel_cat} - Level {cur_level}", True, (255, 255, 255))
    lvl_rect = lvl_surf.get_rect(topleft=(info_x, info_y))
    surface.blit(lvl_surf, lvl_rect)
    benefit_surf = font.render(benefit_desc, True, (255, 255, 255))
    surface.blit(benefit_surf, (info_x, info_y + 32))

    # Draw cost box
    cost_y = info_y + 80
    cost_box = pygame.Rect(info_x, cost_y, box_w - 80, 90)
    pygame.draw.rect(surface, (0, 0, 0), cost_box)
    pygame.draw.rect(surface, (255, 255, 255), cost_box, 2)

    # Show required gold and tokens (price)
    if next_cost_gold is None:
        txt_cost = font.render("Max Level Reached", True, (255, 215, 0))
        surface.blit(txt_cost, (cost_box.left + 12, cost_box.top + 20))
    else:
        txt_gold = font.render(f"Cost: {next_cost_gold} Gold", True, (255, 215, 0))
        txt_token = font.render(f"Cost: {next_cost_token} Tokens", True, (255, 215, 0))
        surface.blit(txt_gold, (cost_box.left + 12, cost_box.top + 10))
        surface.blit(txt_token, (cost_box.left + 12, cost_box.top + 40))

    # Show player's current gold & tokens
    you_gold = font.render(f"You have: {inventory.get('Gold',0)} gold", True, (255, 255, 255))
    you_tokens = font.render(f"You have: {inventory.get('Upgrade Tokens',0)} tokens", True, (255, 255, 255))
    surface.blit(you_gold, (cost_box.right - 250, cost_box.top + 10))
    surface.blit(you_tokens, (cost_box.right - 250, cost_box.top + 40))

    # Upgrade button visual
    btn_w, btn_h = 220, 56
    btn_x = box_x + (box_w - btn_w) // 2
    btn_y = box_y + box_h - btn_h - 28
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(surface, (255, 215, 0), btn_rect)
    pygame.draw.rect(surface, (255, 255, 255), btn_rect, 2)
    btn_txt = font.render("UPGRADE", True, (255, 255, 255))
    btn_tr = btn_txt.get_rect(center=btn_rect.center)
    surface.blit(btn_txt, btn_tr)

        # Draw upgrade feedback message inside the upgrade menu
    if feedback and feedback_timer > 0:
        msg_surf = font.render(feedback, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(center=(ROOM_WIDTH // 2, cost_box.bottom + 30))
        surface.blit(msg_surf, msg_rect)

# ATTEMP TO UPGRADE
def attempt_upgrade(selected):
    """Attempts to apply the selected upgrade. Returns a (success, message) tuple."""
    global armor_level, weapon_level, inventory_level, gold_pickup_level, max_health, health, weapon_base_multiplier, gold_per_pickup
    # Get current level for selected
    if selected == "Armor":
        cur_lvl = armor_level
    elif selected == "Weapons":
        cur_lvl = weapon_level
    elif selected == "Inventory":
        cur_lvl = inventory_level
    elif selected == "Gold":
        cur_lvl = gold_pickup_level
    else:
        return False, "Unknown upgrade"

    # Check max
    if cur_lvl >= MAX_UPGRADE_LEVEL:
        return False, "Max Level Reached"

    # Costs are indexed by current level (next upgrade is index cur_lvl)
    gold_cost = upgrade_costs_gold[cur_lvl]
    token_cost = upgrade_costs_tokens[cur_lvl]

    if inventory.get("Gold", 0) < gold_cost:
        return False, "Not enough gold"
    if inventory.get("Upgrade Tokens", 0) < token_cost:
        return False, "Not enough tokens"

    # Charge and apply upgrade
    inventory["Gold"] -= gold_cost
    inventory["Upgrade Tokens"] -= token_cost

    if selected == "Armor":
        armor_level += 1
        max_health += 50
        health = min(max_health, health + 50)
        return True, f"Armor upgraded to level {armor_level}"
    elif selected == "Weapons":
        weapon_level += 1
        # Multiplicative 1.5x per level
        weapon_base_multiplier *= 1.5
        return True, f"Weapons upgraded to level {weapon_level}"
    elif selected == "Inventory":
        inventory_level += 1
        for k in inventory_limits.keys():
            if k == "Gold":
                inventory_limits[k] += 50
            elif k == "Artifacts":
                pass
            elif k == "Upgrade Tokens":
                inventory_limits[k] += 5
            else:
                inventory_limits[k] += 2
        return True, f"Inventory size increased (level {inventory_level})"
    elif selected == "Gold":
        gold_pickup_level += 1
        gold_per_pickup = gold_per_pickup_base + gold_pickup_level * 10
        return True, f"Gold increased (now {gold_per_pickup} gold per pickup, level {gold_pickup_level})"

    return False, "Unknown upgrade"

# DRAW INSTRUCTIONS
def draw_instructions(surface):
    """Draws the How To Play / Controls page as a centered panel."""
    # semi-transparent background
    draw_overlay(surface)

    # panel
    w, h = 720, 520
    x = (ROOM_WIDTH - w) // 2
    y = (ROOM_HEIGHT - h) // 2
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((12, 12, 18, 240))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 3)

    # Title
    hdr = title_font.render("HOW TO PLAY", True, (255, 255, 255))
    surface.blit(hdr, hdr.get_rect(center=(x + w//2, y + 40)))

    # Controls text
    lines = [
        "Movement:  WASD  or  Arrow Keys",
        "Use Speed Potion:  1",
        "Use Health Potion: 2",
        "Use Strength Potion: 3",
        "Toggle HUD:  E",
        "Toggle Map:  M",
        "Interact / Talk:  Right-Click",
        "Close Menus: ESC",
        "",
        "Collect resources by walking over them.",
        "Open SHOP use UP/DOWN to select",
        "Open UPGRADES use LEFT/RIGHT to select"
    ]

    # Draw each line
    start_y = y + 100
    for i, line in enumerate(lines):
        txt = font.render(line, True, (255, 255, 255))
        surface.blit(txt, (x + 36, start_y + i * 30))

    # Closing hint / buttons
    hint = font.render("Press ESC to return", True, (180, 180, 180))
    surface.blit(hint, hint.get_rect(center=(x + w//2, y + h - 36)))

# DRAWING MINIMAP
def draw_minimap(surface, level, row, col):
    """Draws a simple minimap for the current level under the level text."""
    if not map_visible:
        return  # Don't draw anything if map is hidden

    map_size = 90  # total width/height of the map
    cell_size = map_size // GRID_WIDTH

    map_x = ROOM_WIDTH - map_size - 20
    map_y = 60  # positioned just below the level text

    # background box
    pygame.draw.rect(surface, (0, 0, 0), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    pygame.draw.rect(surface, (255, 255, 255), (map_x - 5, map_y - 5, map_size + 10, map_size + 10), 2)

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            x = map_x + c * cell_size
            y = map_y + (GRID_HEIGHT - 1 - r) * cell_size  # flip vertically so top is top

            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)

            # highlight the current room
            if r == row and c == col:
                pygame.draw.rect(surface, (255, 255, 255), rect)  # player position
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect, 1)

    # Level location
    text = f"Level {level + 1} - {['Bottom','Middle','Top'][row]} {['Left','Middle','Right'][col]}"
    info = font.render(text, True, (255, 255, 255))
    rect = info.get_rect(topright=(ROOM_WIDTH - 20, 20))
    pygame.draw.rect(surface, (0, 0, 0), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10))
    pygame.draw.rect(surface, (255, 255, 255), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10), 2)
    surface.blit(info, rect)

# DRAWING MESSAGE
def draw_message(surface, text, timer, color):
    """Displays a temporary on-screen message with colored outline."""
    if timer > 0 and text:
        msg = font.render(text, True, color)
        rect = msg.get_rect(center=(ROOM_WIDTH // 2, 50))
        bg_rect = rect.inflate(20, 10)

        # Glow effect around box
        glow_rect = bg_rect.inflate(8, 8)
        pygame.draw.rect(surface, color, glow_rect, 2)

        # Draw semi-transparent dark background
        pygame.draw.rect(surface, (255, 255, 255), bg_rect)

        # Draw outline in message color
        pygame.draw.rect(surface, color, bg_rect, 3)

        surface.blit(msg, rect)

# DRAWING DIALOGUE
def draw_dialogue(surface):
    """Draws the active dialogue box with word-wrapped text at the bottom of the screen."""
    if not dialogue_active or not current_dialogue:
        return

    box_width, box_height = 600, 120
    box_x = (ROOM_WIDTH - box_width) // 2
    box_y = ROOM_HEIGHT - box_height - 20

    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_width, box_height), 3)

    # Clamp index to valid range
    idx = max(0, min(dialogue_index, len(current_dialogue) - 1))
    text = current_dialogue[idx]
    words = text.split(" ")
    lines, line, max_width = [], "", box_width - 40

    # Simple word wrapping
    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] < max_width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y = box_y + 25
    for l in lines:
        t_surf = font.render(l.strip(), True, (255, 255, 255))
        surface.blit(t_surf, (box_x + 20, y))
        y += font.get_height() + 5

    # Hint to continue (subtle)
    hint = font.render("Right-click to continue...", True, (180, 180, 180))
    hint_rect = hint.get_rect(bottomright=(box_x + box_width - 12, box_y + box_height - 8))
    surface.blit(hint, hint_rect)

# COLLISION
def colllision_check(dx, dy, coll_list):
    """Moves the player while preventing overlap with collidable objects."""
    player.x += dx
    for c in coll_list:
        if player.colliderect(c):
            if dx > 0:
                player.right = c.left
            elif dx < 0:
                player.left = c.right

    player.y += dy
    for c in coll_list:
        if player.colliderect(c):
            if dy > 0:
                player.bottom = c.top
            elif dy < 0:
                player.top = c.bottom

# MOVEMENT
def room_transition():
    """Handles transitions between rooms and levels based on player position."""
    global current_room
    level, row, col = current_room

    # Move left
    if player.left < 0:
        if col > 0:
            current_room[2] -= 1
            player.right = ROOM_WIDTH
        else:
            player.left = 0

    # Move right
    elif player.right > ROOM_WIDTH:
        if col < GRID_WIDTH - 1:
            current_room[2] += 1
            player.left = 0
        else:
            player.right = ROOM_WIDTH

    # Move up
    elif player.top < 0:
        if row < GRID_HEIGHT - 1:
            current_room[1] += 1
            player.bottom = ROOM_HEIGHT
        # Transition to NEXT level from top-right room
        elif row == GRID_HEIGHT - 1 and col == GRID_WIDTH - 1 and level < LEVELS - 1:
            current_room = [level + 1, 0, 0]
            player.x, player.y = 50, ROOM_HEIGHT - 100
        else:
            player.top = 0

    # Move down
    elif player.bottom > ROOM_HEIGHT:
        if row > 0:
            current_room[1] -= 1
            player.top = 0
        # Transition BACK a level from bottom-left room
        elif row == 0 and col == 0 and level > 0:
            current_room = [level - 1, GRID_HEIGHT - 1, GRID_WIDTH - 1]
            player.x, player.y = ROOM_WIDTH - 150, 50
        else:
            player.bottom = ROOM_HEIGHT

# Helper to draw dark overlay
def draw_overlay(surface):
    # Create a semi-transparent fullscreen overlay
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    # Pygame.SRCALPHA = RGBA instead of just RGB
    overlay.fill((0, 0, 0, 180))  # Black with alpha 180 for semi-transparent effect
    surface.blit(overlay, (0, 0))

# Helper to draw home bg
def draw_home_background(surface):
    base = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT))
    base.fill((0, 0, 0))

    # Adds small random bright specks to give the surface subtle texture.
    noise = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    for _ in range(100):
        x = random.randint(0, ROOM_WIDTH - 1)
        y = random.randint(0, ROOM_HEIGHT - 1)
        # Each dot is a light grey pixel with low alpha
        shade = random.randint(130, 180)
        noise.set_at((x, y), (shade, shade, shade, 25))

    base.blit(noise, (0, 0))

    # Creates a sequence of transparent circles from outside -> inside.
    burn = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    center = (ROOM_WIDTH // 2, ROOM_HEIGHT // 2)
    max_radius = max(ROOM_WIDTH, ROOM_HEIGHT)

    # Each smaller circle has lower intensity, producing a smooth fade.
    for r in range(max_radius, 0, -6):
        # Dark brown edge fade
        alpha = int(255 * (1 - (r / max_radius)))
        color = (150, 145, 155, alpha)
        pygame.draw.circle(burn, color, center, r)

    # Combine onto main surface
    surface.blit(base, (0, 0))
    surface.blit(burn, (0, 0))

# MAIN LOOP
running = True
while running:
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    # ---------- EVENT HANDLING ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        # ----- Home Screen Start -----
        if on_home and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            on_home = False
            player.x, player.y = 50, ROOM_HEIGHT - 100
        
        if instructions_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                instructions_active = False

            # If instructions menu is active, do NOT let other events run  
            continue

        # ----- Mouse interactions -----
        if event.type == pygame.MOUSEBUTTONDOWN and not on_home:
            # ---Villager interactions---
            # If right-click and dialogue active -> advance dialogue 
            if event.button == 3:
                if trading_prompt_active or trade_menu_active:
                    continue

                if dialogue_active:
                    # Advance dialogue line
                    dialogue_index += 1
                    # If dialogue finished, close and maybe open trade prompt
                    if dialogue_index >= len(current_dialogue):
                        dialogue_active = False
                        dialogue_index = 0
                        # If this villager was set to trigger trade after dialogue, open prompt
                        if trade_pending_key:
                            trading_prompt_active = True
                            trade_prompt_key = trade_pending_key
                            trade_pending_key = None
                    continue

                # If not currently in dialogue, right-click should attempt to start dialogue with nearby villager
                found_villager = False
                for i, vrect in enumerate(villager_tiles):
                    if vrect and player.colliderect(vrect.inflate(50, 50)):
                        # Start dialogue always
                        level, row, col = current_room
                        key = (level, row, col, i)
                        current_dialogue = list(dialogues.get(
                            key,
                            ["Villager: Hello there!",
                            "Villager: Sorry, I don't have much to say."]
                        ))
                        dialogue_index = 0
                        dialogue_active = True
                        active_villager_index = i
                        # If villager is tradeable, we set trade_pending_key so that after dialogue ends we show the trading prompt
                        if key in tradeable_villagers:
                            trade_pending_key = key
                        else:
                            trade_pending_key = None
                        found_villager = True
                        break
                if found_villager:
                    continue

                # --- Upgrade Hut Interaction ---
                for hut_rect in upgrade_hut_tiles:
                    if hut_rect and player.colliderect(hut_rect.inflate(60, 60)):
                        upgrade_menu_active = True
                        # When entering upgrade menu, hide HUD/map and reset selection
                        hud_visible = False
                        map_visible = False
                        upgrade_selection = 0
                        break
                continue

            # Handle left click for upgrade button when upgrade menu is active
            if event.button == 1:
                if trade_menu_active:
                    # Recompute the trade menu button rect exactly as in draw_trade_menu
                    box_w, box_h = 700, 520
                    box_x = (ROOM_WIDTH - box_w) // 2
                    box_y = (ROOM_HEIGHT - box_h) // 2
                    # Buy buttton set up
                    b_btn_w, b_btn_h = 220, 56
                    b_btn_x = box_x + (box_w - b_btn_w) // 2
                    b_btn_y = box_y + box_h - b_btn_h + 56
                    b_btn_rect = pygame.Rect(b_btn_x, b_btn_y, b_btn_w, b_btn_h)
                    if b_btn_rect.collidepoint(event.pos):
                        # Item and price based on selection
                        Item_key, price = trade_items[trade_selection]
                        # If can buy, add item, remove gold, display feedback
                        if inventory.get("Gold", 0) >= price:
                            # Check inventory limits for item
                            max_limit = max(inventory_limits.values())
                            if inventory.get(Item_key, 0) < inventory_limits.get(Item_key, max_limit):
                                inventory["Gold"] -= price
                                inventory[Item_key] = inventory.get(Item_key, 0) + 1
                                feedback, feedback_timer = f"Bought 1 {Item_key}", 2.5
                            else:
                                feedback, feedback_timer = f"{Item_key} inventory full!", 2.5
                        # If not enough gold to buy the item
                        else:
                            feedback, feedback_timer = "Not enough gold!", 2.5
                        continue
                    # Sell button set up
                    s_btn_w, s_btn_h = 220, 56
                    s_btn_x = box_x + (box_w - s_btn_w) // 2
                    s_btn_y = box_y + box_h - s_btn_h
                    s_btn_rect = pygame.Rect(s_btn_x, s_btn_y, s_btn_w, s_btn_h)
                    if s_btn_rect.collidepoint(event.pos):
                        # Item and price based on selection
                        Item_key, price = trade_items[trade_selection]
                        current_gold = inventory.get("Gold", 0)
                        gold_limit = inventory_limits.get("Gold", 150)
                        # If gold is full, block selling
                        if current_gold >= gold_limit:
                            feedback, feedback_timer = "Gold is full! Cannot sell.", 2.5
                        # If sale would exceed gold limit, block selling
                        elif current_gold + price > gold_limit:
                            feedback, feedback_timer = "Not enough space for more gold! Cannot sell.", 2.5
                        # If can sell, remove item, add gold, display feedback
                        elif inventory.get(Item_key, 0) > 0:
                            inventory[Item_key] -= 1
                            inventory["Gold"] = current_gold + price
                            feedback, feedback_timer = f"Sold 1 {Item_key}", 2.5
                        # If not enough to sell item
                        else:
                            feedback, feedback_timer = f"No {Item_key} to sell!", 2.5
                        continue

                if upgrade_menu_active:
                    # Recompute the upgrade menu button rect exactly as in draw_upgrade_menu
                    box_w, box_h = 700, 520
                    box_x = (ROOM_WIDTH - box_w) // 2
                    box_y = (ROOM_HEIGHT - box_h) // 2
                    btn_w, btn_h = 220, 56
                    btn_x = box_x + (box_w - btn_w) // 2
                    btn_y = box_y + box_h - btn_h - 28
                    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                    if btn_rect.collidepoint(event.pos):
                        # Attempt the upgrade for the selected category
                        selected = ["Armor", "Weapons", "Inventory", "Gold"][upgrade_selection]
                        success, msg = attempt_upgrade(selected)
                        if success:
                            feedback, feedback_timer = "Upgraded Item", 2.5
                        else:
                            # Give user feedback for not enough resources or max
                            if msg == "Not enough gold":
                                feedback, feedback_timer = msg, 2.5
                            elif msg == "Not enough tokens":
                                feedback, feedback_timer = msg, 2.5
                            elif msg == "Not enough items":
                                feedback, feedback_timer = msg, 2.5
                            elif msg == "Max Level Reached":
                                feedback, feedback_timer = msg, 2.5
                            else:
                                feedback, feedback_timer = "NONE", 2.5
                    continue

        # ----- Toggles & Keyboard -----
        elif event.type == pygame.KEYDOWN and not on_home:
            # --- Villager Interaction ---
            # If trade prompt is active, handle Y/N keys here first
            if trading_prompt_active:
                if event.key == pygame.K_y:
                    # Open trade menu
                    trade_menu_active = True
                    trading_prompt_active = False
                    dialogue_active = False
                    trade_selection = 0
                    # Automatically close HUD and Map when trading opens and clear trade feedback
                    hud_visible = False 
                    map_visible = False 
                    feedback = ""  # Clear any prior feedback
                    feedback_timer = 0.0 
                    continue
                elif event.key == pygame.K_n:
                    # Decline trading, close prompt
                    trading_prompt_active = False
                    trade_prompt_key = None
                    trade_pending_key = None  # Clear any pending trade request
                    continue

            # If trade menu is active, allow navigation and buy/sell/exit (only trade controls work)
            if trade_menu_active:
                # Item seceltion control
                if event.key == pygame.K_UP:
                    trade_selection = max(0, trade_selection - 1)
                    continue
                elif event.key == pygame.K_DOWN:
                    trade_selection = min(len(trade_items) - 1, trade_selection + 1)
                    continue

                # exit the trade menu and reset flags
                elif event.key == pygame.K_ESCAPE:
                    trade_menu_active = False
                    trade_prompt_key = None
                    trade_pending_key = None  # Clear any pending trade
                    feedback = ""
                    feedback_timer = 0.0
                    continue

            # While trading menu is active, block toggles for HUD/Map and potions
            # If not trading, allow toggles as before
            if not trade_menu_active and not upgrade_menu_active:
                if event.key == pygame.K_e:
                    hud_visible = not hud_visible
                elif event.key == pygame.K_m:
                    map_visible = not map_visible

                # ----- Potions -----
                if event.key == pygame.K_1:  # Speed Potion
                    if inventory.get("Speed Potions", 0) > 0:
                        inventory["Speed Potions"] -= 1
                        speed_potion_duration += 30
                        message, message_color, message_timer = f"Speed potion used! Duration: {int(speed_potion_duration)}s", (0, 0, 255), 0.75
                    else:
                        message, message_color, message_timer = "No Speed Potions left!", (0, 0, 255), 0.75

                elif event.key == pygame.K_2:  # Health Potion
                    if inventory["Health Potions"] > 0 and health < max_health:
                        old_health = health
                        heal_amount = 20
                        health = min(health + heal_amount, max_health)
                        actual_healed = health - old_health
                        inventory["Health Potions"] -= 1
                        message, message_color, message_timer = f"+{actual_healed} Health", (0, 255, 0), 0.75
                    elif health >= max_health:
                        message, message_color, message_timer = "Your health is already full!", (0, 255, 0), 0.75
                    else:
                        message, message_color, message_timer = "You have no health potions!", (255, 0, 0), 0.75

                elif event.key == pygame.K_3:  # Strength Potion
                    if inventory.get("Strength Potions", 0) > 0:
                        inventory["Strength Potions"] -= 1
                        # Add the fixed constant duration
                        strength_potion_duration += 120
                        message, message_color, message_timer = f"Strength potion used! Duration: {int(strength_potion_duration)}s", (255, 0, 0), 0.75
                    else:
                        message, message_color, message_timer = "No Strength Potions left!", (255, 0, 0), 0.75

            # --- Upgrade Hut Interaction ---
            if upgrade_menu_active:
                # Navigate upgrade categories
                if event.key == pygame.K_LEFT:
                    upgrade_selection = max(0, upgrade_selection - 1)
                    continue
                elif event.key == pygame.K_RIGHT:
                    upgrade_selection = min(3, upgrade_selection + 1)
                    continue
                elif event.key == pygame.K_ESCAPE:
                    upgrade_menu_active = False
                    feedback, feedback_timer = "", 0
                    continue

    # ---------- HOME SCREEN ----------
    if on_home:
        draw_home_background(screen)

        # --- Title ---
        title_text = "Crownfall"

        # Fonts
        home_title_font = pygame.font.SysFont(None, 135)

        # Base colors
        main_color = (180, 210, 255) # main bright light blue
        shadow_color = (80, 110, 160) # dark cool shadow
        glow_color = (200, 230, 255) # soft blue glow

        # Shadow
        shadow = home_title_font.render(title_text, True, shadow_color)
        shadow_rect = shadow.get_rect(center=(ROOM_WIDTH // 2 + 4, 120 + 4))
        screen.blit(shadow, shadow_rect)

        # Glow passes
        for expand in [2, 4, 6]:
            glow_font = pygame.font.SysFont(None, 120 + expand)
            glow = glow_font.render(title_text, True, glow_color)
            glow.set_alpha(40)
            rect = glow.get_rect(center=(ROOM_WIDTH // 2, 120))
            screen.blit(glow, rect)

        # Safe adjusted shades for top and bottom layers
        main_top = (min(main_color[0] + 5, 255), min(main_color[1] + 5, 255), min(main_color[2] + 5, 255))
        main_bottom = (max(main_color[0] - 25, 0), max(main_color[1] - 25, 0), max(main_color[2] - 25, 0))

        # Draw layered main text
        main_top_surf = home_title_font.render(title_text, True, main_top)
        screen.blit(main_top_surf, main_top_surf.get_rect(center=(ROOM_WIDTH // 2, 120 - 2)))

        main_mid_surf = home_title_font.render(title_text, True, main_color)
        screen.blit(main_mid_surf, main_mid_surf.get_rect(center=(ROOM_WIDTH // 2, 120)))

        main_bottom_surf = home_title_font.render(title_text, True, main_bottom)
        screen.blit(main_bottom_surf, main_bottom_surf.get_rect(center=(ROOM_WIDTH // 2, 120 + 2)))

        # --- Halo ---
        hx = ROOM_WIDTH // 2
        hy = ROOM_HEIGHT // 2

        halo_radius = 150
        halo_thickness = 10

        t = pygame.time.get_ticks() * 0.003
        halo_alpha = int((math.sin(t) * 0.5 + 0.5) * 60 + 60)
        rot_angle = t * 0.25

        halo_surf = pygame.Surface((halo_radius * 4, halo_radius * 4), pygame.SRCALPHA)
        center = halo_radius * 2
        segments = 64

        for i in range(segments):
            angle = (i / segments) * (math.pi * 2) + rot_angle
            x1 = center + math.cos(angle) * halo_radius
            y1 = center + math.sin(angle) * halo_radius
            x2 = center + math.cos(angle) * (halo_radius + halo_thickness)
            y2 = center + math.sin(angle) * (halo_radius + halo_thickness)

            pygame.draw.line(halo_surf, (200, 225, 255, halo_alpha), (x1, y1), (x2, y2), 2)

        screen.blit(halo_surf, (hx - center, hy - center))
        pygame.draw.circle(screen, (200, 225, 255), (hx, hy), halo_radius, 2)

        # --- Menu Options ---
        menu_font = pygame.font.SysFont(None, 55)

        option_color = (180, 210, 255)
        option_shadow = (70, 90, 130)

        options = ["Play", "How to Play", "Quit"]
        option_rects = []
        start_y = ROOM_HEIGHT // 2 - 80

        for i, opt in enumerate(options):
            shadow = menu_font.render(opt, True, option_shadow)
            shadow_rect = shadow.get_rect(center=(ROOM_WIDTH // 2 + 2, start_y + i * 70 + 2))
            screen.blit(shadow, shadow_rect)

            surf = menu_font.render(opt, True, option_color)
            rect = surf.get_rect(center=(ROOM_WIDTH // 2, start_y + i * 70))
            screen.blit(surf, rect)
            option_rects.append(rect)

        # --- Pulsing text ---
        pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.004))
        prompt_surf = font.render("PRESS SPACE OR CLICK PLAY", True, (180, 210, 255))
        prompt_surf.set_alpha(pulse)
        prompt_rect = prompt_surf.get_rect(center=(ROOM_WIDTH // 2, ROOM_HEIGHT - 120))
        screen.blit(prompt_surf, prompt_rect)

        # --- Home Menu Click Handling ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Play
            if option_rects[0].collidepoint(pos):
                on_home = False
                player.x, player.y = 50, ROOM_HEIGHT - 100

            # How to Play
            elif option_rects[1].collidepoint(pos):
                instructions_active = True

            # Quit
            elif option_rects[2].collidepoint(pos):
                running = False

        if instructions_active:
            draw_instructions(screen)
            pygame.display.flip()
            continue

        pygame.display.flip()
        continue

    # ---------- GAMEPLAY ----------
    mv_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    mv_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

    # Prevent movement input from affecting player when trade menu or upgrade menu is active
    if trade_menu_active or upgrade_menu_active or hud_visible:
        mv_x = 0
        mv_y = 0

    # Determine facing direction
    if mv_x < 0:
        facing = "left"
    elif mv_x > 0:
        facing = "right"
    elif mv_y < 0:
        facing = "up"
    elif mv_y > 0:
        facing = "down"

    # Draw Room + Update Globals
    draw_room(screen, *current_room, c_Artifacts, c_Gold, c_Health_Potions)
    room_colliders[tuple(current_room)] = colliders

    # ----- Water Movement Check -----
    in_water = any(player.colliderect(wrect) for wrect in water_tiles)

    # ----- Effective Speed -----
    effective_speed = base_speed
    if speed_potion_duration > 0:
        effective_speed *= speed_multiplier
    if in_water:
        effective_speed *= 0.5

    # Movement + Collision
    dx, dy = mv_x * effective_speed, mv_y * effective_speed

    # Only apply movement and room transitions if trading menu or upgrade menu is NOT active
    if not trade_menu_active and not upgrade_menu_active:
        colllision_check(dx, dy, room_colliders.get(tuple(current_room), []))
        room_transition()
    else:
        pass

    # ----- Pickups -----
    def pickup(item_list, inventory_key, limit_key, count, color, msg):
        """Adds colectables to inventory and removes them from the screen"""
        global message, message_color, message_timer
        for rect, ax, ay in item_list:
            if player.colliderect(rect):
                if inventory[inventory_key] < inventory_limits[limit_key]:
                    inventory[inventory_key] += count
                    globals()[f"c_{inventory_key.replace(' ', '_')}"].add((*current_room, ax, ay))
                    message, message_color, message_timer = msg, color, 0.75
                else:
                    message, message_color, message_timer = f"Inventory full of {inventory_key}", (255, 0, 0), 0.75

    # Update gold_per_pickup in case it changed
    gold_per_pickup = gold_per_pickup_base + gold_pickup_level * 10

    # Do not pick up items while trading or upgrading (player shouldn't move or pick while these menus are open)
    if not trade_menu_active and not upgrade_menu_active:
        pickup(gold, "Gold", "Gold", gold_per_pickup, (255, 215, 0), f"+{gold_per_pickup} gold")
        pickup(health_potions, "Health Potions", "Health Potions", 1, (0, 255, 0), "+1 health potion")
        pickup(speed_potions, "Speed Potions", "Speed Potions", 1, (173, 216, 230), "+1 speed potion")
        pickup(strength_potions, "Strength Potions", "Strength Potions", 1, (255, 70, 0), "+1 strength potion")
        pickup(artifacts, "Artifacts", "Artifacts", 1, (160, 32, 240), "+1 artifact")

    # ----- Player Drawing -----
    player_colors = {"up": (255, 255, 0), "down": (0, 255, 0), "left": (255, 0, 0), "right": (0, 0, 255)}
    pygame.draw.rect(screen, player_colors.get(facing, (255, 255, 255)), player)

    # ----- UI Elements -----
    draw_hud(screen)
    draw_minimap(screen, *current_room)
    draw_message(screen, message, message_timer, message_color)
    draw_dialogue(screen)
    draw_trade_prompt(screen)
    draw_trade_menu(screen)
    draw_upgrade_menu(screen)

    # ----- Villager Interaction -----
    # Dialogue End Check
    if dialogue_active and active_villager_index is not None:
        vrect = villager_tiles[active_villager_index] if 0 <= active_villager_index < len(villager_tiles) else None
        if not vrect or not player.colliderect(vrect.inflate(60, 60)):
            # If player moves away while dialogue pending trade, clear pending trade
            dialogue_active, current_dialogue, dialogue_index, active_villager_index = False, [], 0, None
            trade_pending_key = None

    # If trading prompt is active, close it if player moves away from villager
    if trading_prompt_active and trade_prompt_key is not None:
        # Find the villager rectangle by index; if not near, close prompt
        level, row, col, idx = trade_prompt_key
        if idx < 0 or idx >= len(villager_tiles):
            trading_prompt_active = False
            trade_prompt_key = None
        else:
            vrect = villager_tiles[idx]
            if not player.colliderect(vrect.inflate(60, 60)):
                trading_prompt_active = False
                trade_prompt_key = None

    # ----- Timers -----
    # Potion effect timer update
    if strength_potion_duration > 0:
        # Combine weapon multiplier and strength potion when damage is used elsewhere
        damage_multiplier = strength_multiplier * (1.0 + 0.2 * weapon_level)
        strength_potion_duration = max(0, strength_potion_duration - dt / 1000.0)
    else:
        # Not using strength potion
        damage_multiplier = (1.0 + 0.2 * weapon_level) * weapon_base_multiplier

    if speed_potion_duration > 0:
        speed_potion_duration = max(0, speed_potion_duration - dt / 1000.0)

    # Global message timers
    if message_timer > 0:
        message_timer = max(0, message_timer - dt / 1000.0)
        if message_timer == 0:
            message = ""
            message_color = None

    if feedback_timer > 0:
        feedback_timer = max(0, feedback_timer - dt / 1000.0)
        if feedback_timer == 0:
            feedback = ""
    pygame.display.flip()
pygame.quit()