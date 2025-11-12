# Amogh R and Sebastian M || CROWNFALL
import pygame, os
pygame.init()
os.chdir(os.path.dirname(__file__))  # make working dir = script folder

# CONSTANTS
ROOM_WIDTH = 800
ROOM_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3

# Basic set up
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 80)

# Player and Room setup
player = pygame.Rect(50, ROOM_HEIGHT - 100, 50, 50)
player_speed = 10
facing = "up" # Track direction player is facing
player_color = (255, 255, 0)
current_room = [0, 0, 0]
room_colliders = {}

# Speed setup
base_speed = 10
speed_potion_duration = 0  # seconds remaining on active potion
speed_multiplier = 2

# Strength setup
damage_multiplier = 1
strength_potion_duration = 0  # seconds remaining on active strength potion
strength_multiplier = 2

# Health set up
health = 80
max_health = 100

# Inventory set up
inventory = {"Gold": 0, "Artifacts": 0, "Health Potions": 0, "Speed Potions": 0, "Strength Potions": 0}
inventory_limits = {"Gold": 150, "Artifacts": 7, "Health Potions": 5, "Speed Potions": 5, "Strength Potions": 5}

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
trade_feedback = ""
trade_feedback_timer = 0.0

# Flag variables
on_home = True # Player starts in home area
hud_visible = False # HUD hidden by default
map_visible = False # Map hidden by default
dialogue_active = False # No dialogue active at start
trading_prompt_active = False # Trade prompt not showing
trade_menu_active = False # Trade menu closed
trade_prompt_key = None # Tracks which villager is offering trade
trade_pending_key = None # Marks villager to show trade prompt after dialogue
active_villager_index = None # Which villager for multiple in a room

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

# Dialogue set up
dialogue_index = 0
current_dialogue = []

# Key format = (level, row, column, villager_index)
dialogues = {
    # LEVEL 1: bottom middle villager
    (0, 0, 1, 0): [
        "Villager: LALALA!",
        "Villager: BLA BLA"
    ],
    # LEVEL 1: middle left villager
    (0, 1, 0, 0): [
        "Villager: STORY THINGS",
        "Villager: More story things"
    ],
    # LEVEL 1: bottom right villager
    (0, 0, 2, 0): [
        "Villager: Sebastian, do something",
        "Villager: I wanna go to sleep"
    ],
    #LEVEL 1: Top Middle Villager
    (0, 2, 1, 0): [
		"Villager: Amogh, HELP MEEEEEE",
		"Villager: Or maybe I'll go give this nice traveler the most, bestest, GREATEST weapon of all!"
		],

    # LEVEL 2: bottom right villagers
    (1, 0, 2, 0): [
        "Villager: I don't have a normal sleep schedule",
        "Villager: It's 4:12 am right now"
    ],
    (1, 0, 2, 1): [
        "Villager: I am hungry",
        "Villager: I need to get some food"
    ],
    (1, 0, 2, 2): [
        "Villager: AI is going to take my job",
        "Villlager: Im going to be jobless if I pick this as my job"
    ],

    # LEVEL 3: bottom middle villagers
    (2, 0, 1, 0): [
        "Villager: I have a headache",
        "Villager: I need water"
    ],
    (2, 0, 1, 1): [
        "Villager: Pokemon",
        "Villager: Knock, Knick. Whos there. IDK"
    ],
}

# Trade set up
tradeable_villagers = { # Which villager keys are tradeable
    (0, 0, 1, 0),  # Level 1 bottom middle
    (0, 2, 1, 0),  #LEVEL 1 Top Middle Viallager
    (1, 0, 2, 1),  # Level 2 bottom right (middle villager)
    (2, 0, 1, 0),  # Level 3 bottom middle (left villager)
}
trade_selection = 0
# (inventory key, price)
trade_items = [("Strength Potions", 30), ("Speed Potions", 15), ("Health Potions", 45)]

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

        # trim transparent padding so collider matches visible pixels only
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

    # Environment objects
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

    return None  # fallback

# DRAWING ROOMS
def draw_room(surface, level, row, col, c_Artifacts, c_Gold, c_Health_Potions):
    """Draws the current room based on the level, row, and column.  2
    Adds interactive and environmental objects to their respective lists."""

    global colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles

    # Draw background
    bg = pygame.image.load("crownfall_images/Level_bg_1.jpg").convert()
    bg = pygame.transform.scale(bg, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(bg, (0, 0))

    # Object containers for this room
    colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles = [], [], [], [], [], [], [], []

    def can_draw(anchor_x, anchor_y, sset):
        """checks if a collectable should be drawn on the screen"""
        return (level, row, col, anchor_x, anchor_y) not in sset

    # ───────── LEVEL 1 (level == 0)
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

    # ───────── LEVEL 2 (level == 1)
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

    # ───────── LEVEL 3 (level == 2)
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
        draw_objects(170, 170, "tree2", surface) # Tree 3
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
def draw_hud(surface, level, row, col):
    """Draws the player HUD (health + inventory) when visible."""
    if not hud_visible:
        return  # Don't draw anything if HUD is hidden

    # Health bar box (top-left)
    box_x, box_y = 15, 10
    box_width, box_height = 220, 70
    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

    label = font.render("Health", True, (255, 255, 255))
    surface.blit(label, (box_x + 70, box_y + 10))

    bar_x, bar_y = box_x + 10, box_y + 35
    bar_width, bar_height = 200, 25

    # Background
    pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * (health / max_health), bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    health_text = font.render(f"{int(health)} / {max_health}", True, (255, 255, 255))
    text_rect = health_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    surface.blit(font.render(f"{int(health)} / {max_health}", True, (0, 0, 0)), (text_rect.x + 1, text_rect.y + 1))
    surface.blit(health_text, text_rect)

    # Inventory box (auto-resizing)
    line_height = 30
    padding_top = 20
    padding_bottom = 10
    num_items = len(inventory)
    inventory_height = padding_top + num_items * line_height + padding_bottom

    inventory_rect = pygame.Rect(20, 90, 250, inventory_height)
    pygame.draw.rect(surface, (0, 0, 0), inventory_rect)
    pygame.draw.rect(surface, (255, 255, 255), inventory_rect, 2)

    y = inventory_rect.top + 15
    for item, count in inventory.items():
        txt = font.render(f"{item}: {count}", True, (255, 255, 255))
        surface.blit(txt, (40, y))
        y += line_height

    # Active effects display
    offset_y = inventory_rect.bottom + 10
    if speed_potion_duration > 0:
        effect_text = font.render(f"{speed_multiplier}x speed for: ({int(speed_potion_duration)}s)", True, (0, 255, 255))
        surface.blit(effect_text, (inventory_rect.left, offset_y))
        offset_y += 25
    if strength_potion_duration > 0:
        effect_text = font.render(f"{strength_multiplier}x damage for: ({int(strength_potion_duration)}s)", True, (255, 0, 0))
        surface.blit(effect_text, (inventory_rect.left, offset_y))
        offset_y += 25

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

    # Create a semi-transparent fullscreen overlay
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    # pygame.SRCALPHA = RGBA instead of just RGB
    overlay.fill((0, 0, 0, 180))  # Black with alpha 180 for semi-transparent effect
    surface.blit(overlay, (0, 0))

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
    shop_title_rect = shop_title.get_rect(topleft=(box_x + 20, box_y + 10))
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

    # Item selection
    y = shop_area_y + 34
    for idx, (Item_key, price) in enumerate(trade_items):
        # Use simple indented arrow marker
        sell_marker = "   ->" if idx == trade_selection else "      "
        
        # Render the item name and selection arrow
        # 'Item_key' is the item's name (e.g., "Health Potion")
        line = font.render(f"{sell_marker} {Item_key}", True, (255, 255, 255))

        # Render the item's price in gold (e.g., "30g")
        price_txt = font.render(f"{price}g", True, (255, 255, 255))

        # Render the quantity of this item currently in the player's inventory
        # inventory.get(Item_key, 0) → returns the number of that item, or 0 if not owned
        qty_txt = font.render(str(inventory.get(Item_key, 0)), True, (255, 255, 255))

        # Draw the item name + arrow to the screen at the shop column position
        surface.blit(line, (shop_area_x, y))
        # Draw the item's price text in the middle section of the shop box
        surface.blit(price_txt, (box_x + box_w // 2, y))
        # Draw the item quantity near the right edge of the shop box
        surface.blit(qty_txt, (box_x + box_w - 140, y))
        y += 40

    # Draw in-menu feedback (instead of global messages) just under the shop list
    feedback_y = y + 6
    if trade_feedback:
        fb_surf = font.render(trade_feedback, True, (255, 200, 0))
        fb_rect = fb_surf.get_rect(center=(box_x + box_w // 2, feedback_y))
        surface.blit(fb_surf, fb_rect)
    # reserve some spacing before inventory
    inventory_top = feedback_y + 32

    # INVENTORY title (below shop and feedback)
    inventory_title = title_font.render("INVENTORY", True, (255, 255, 255))
    inventory_title_rect = inventory_title.get_rect(topleft=(box_x + 20, inventory_top))
    surface.blit(inventory_title, inventory_title_rect)

    # Draw inventory items under the inventory title - left aligned, consistent style
    inventory_y = inventory_title_rect.bottom + 8
    inventory_x_left = box_x + 40
    line_h = 28
    keys_list = list(inventory.keys())
    for i, item in enumerate(keys_list):
        txt = font.render(f"{item}: {inventory.get(item,0)}", True, (180, 180, 180))
        surface.blit(txt, (inventory_x_left, inventory_y + i * line_h))

    # Bottom text
    help_txt = font.render("UP/DOWN to select item | B to buy | S to sell | ESC to exit", True, (180, 180, 180))
    help_rect = help_txt.get_rect(midbottom=(box_x + box_w // 2, box_y + box_h - 20))
    surface.blit(help_txt, help_rect)

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

    # simple word wrapping
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

# MAIN LOOP
running = True
while running:
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    # ─────────────── EVENT HANDLING ───────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        # ─── Home Screen Start ───
        if on_home and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            on_home = False
            player.x, player.y = 50, ROOM_HEIGHT - 100

        # ─── Toggles ───
        elif event.type == pygame.KEYDOWN and not on_home:
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
                    trade_feedback = ""  # Clear any prior feedback
                    trade_feedback_timer = 0.0 
                    continue
                elif event.key == pygame.K_n:
                    # Decline trading, close prompt
                    trading_prompt_active = False
                    trade_prompt_key = None
                    trade_pending_key = None  # clear any pending trade request
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

                # Buying selected item
                elif event.key == pygame.K_b:
                    # Item and price based on selection
                    Item_key, price = trade_items[trade_selection]
                    # If can buy, add item, remove gold, display feedback
                    if inventory.get("Gold", 0) >= price:
                        # Check inventory limits for item
                        max_limit = max(inventory_limits.values())
                        if inventory.get(Item_key, 0) < inventory_limits.get(Item_key, max_limit):
                            inventory["Gold"] -= price
                            inventory[Item_key] = inventory.get(Item_key, 0) + 1
                            trade_feedback = f"Bought 1 {Item_key}"
                            trade_feedback_timer = 2.5
                        else:
                            trade_feedback = f"{Item_key} inventory full!"
                            trade_feedback_timer = 2.5
                    # If not enough gold to buy the item
                    else:
                        trade_feedback = "Not enough gold!"
                        trade_feedback_timer = 2.5
                    continue

                # Selling selected item
                elif event.key == pygame.K_s:
                    # Item and price based on selection
                    Item_key, price = trade_items[trade_selection]
                    current_gold = inventory.get("Gold", 0)
                    gold_limit = inventory_limits.get("Gold", 150)

                    # If gold is full, block selling
                    if current_gold >= gold_limit:
                        trade_feedback = "Gold is full! Cannot sell."
                        trade_feedback_timer = 2.5
                    # If sale would exceed gold limit, block selling
                    elif current_gold + price > gold_limit:
                        trade_feedback = "Not enough space for more gold! Cannot sell."
                        trade_feedback_timer = 2.5
                    # If can sell, remove item, add gold, display feedback
                    elif inventory.get(Item_key, 0) > 0:
                        inventory[Item_key] -= 1
                        inventory["Gold"] = current_gold + price
                        trade_feedback = f"Sold 1 {Item_key}"
                        2.5
                    # If not enough to sell item
                    else:
                        trade_feedback = f"No {Item_key} to sell!"
                        trade_feedback_timer = 2.5
                    continue

                # Exit the trade menu and reset flags
                elif event.key == pygame.K_ESCAPE:
                    trade_menu_active = False
                    trade_prompt_key = None
                    trade_pending_key = None  # Clear any pending trade
                    trade_feedback = ""
                    trade_feedback_timer = 0.0
                    continue

            # While trading menu is active, block toggles for HUD/Map and potions
            # If not trading, allow toggles as before
            if not trade_menu_active:
                if event.key == pygame.K_e:
                    hud_visible = not hud_visible
                elif event.key == pygame.K_m:
                    map_visible = not map_visible

                # ─── Potions ───
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
                        # add the fixed constant duration
                        strength_potion_duration += 120
                        message, message_color, message_timer = f"Strength potion used! Duration: {int(strength_potion_duration)}s", (255, 0, 0), 0.75
                    else:
                        message, message_color, message_timer = "No Strength Potions left!", (255, 0, 0), 0.75

            # ─── Dialogue ───
            # Enter to start / advance dialogue. For tradeable villagers, dialogue runs first,
            # then the trade prompt is shown automatically after the last line.
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if dialogue_active:
                    # Player is currently in a conversation: advance
                    dialogue_index += 1
                    # If finished dialogue lines
                    if dialogue_index >= len(current_dialogue):
                        # If this conversation was marked to show trade after dialogue, do that
                        if trade_pending_key is not None and trade_prompt_key is None:
                            # Show the trading prompt immediately after dialogue finishes
                            trading_prompt_active = True
                            trade_prompt_key = trade_pending_key
                            trade_pending_key = None
                            # End dialogue state but keep info
                            dialogue_active = False
                            current_dialogue = []
                            dialogue_index = 0
                            active_villager_index = None
                        else:
                            # End conversation when out of lines
                            dialogue_active = False
                            current_dialogue = []
                            dialogue_index = 0
                            active_villager_index = None
                    # else still in middle of dialogue, do nothing else
                else:
                    # Try to start a conversation with any nearby villager
                    found = False
                    for i, vrect in enumerate(villager_tiles):
                        if vrect and player.colliderect(vrect.inflate(50, 50)):
                            level, row, col = current_room
                            key = (level, row, col, i)
                            # Start dialogue always
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
                            found = True
                            break
                    if not found:
                        # If no villager nearby
                        pass

    # ─────────────── HOME SCREEN ───────────────
    if on_home:
        screen.fill((173, 216, 230))

        # Title Box
        title_surf = title_font.render("Crownfall", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(ROOM_WIDTH // 2, 80))
        box_rect = pygame.Rect(
            title_rect.left - 30,
            title_rect.top - 15,
            title_rect.width + 60,
            title_rect.height + 30,
        )
        pygame.draw.rect(screen, (255, 255, 255), box_rect)
        pygame.draw.rect(screen, (0, 0, 0), box_rect, 5)
        screen.blit(title_surf, title_rect)

        # Start Prompt
        prompt_surf = font.render("Press SPACE to play", True, (0, 0, 0))
        prompt_rect = prompt_surf.get_rect(center=(ROOM_WIDTH // 2, ROOM_HEIGHT // 2 + 120))
        screen.blit(prompt_surf, prompt_rect)

        # Player Display
        home_player = player.copy()
        home_player.inflate_ip(175, 175)
        home_player.center = (ROOM_WIDTH // 2, ROOM_HEIGHT // 2 - 50)
        pygame.draw.rect(screen, (0, 0, 0), home_player)

        pygame.display.flip()
        continue

    # ─────────────── GAMEPLAY ───────────────
    mv_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    mv_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

    # Prevent movement input from affecting player when trade menu is active
    if trade_menu_active:
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

    # ─── Water Movement Check ───
    in_water = any(player.colliderect(wrect) for wrect in water_tiles)

    # ─── Effective Speed ───
    effective_speed = base_speed
    if speed_potion_duration > 0:
        effective_speed *= speed_multiplier
    if in_water:
        effective_speed *= 0.5

    # Movement + Collision
    dx, dy = mv_x * effective_speed, mv_y * effective_speed

    # Only apply movement and room transitions if trading menu is NOT active
    if not trade_menu_active:
        colllision_check(dx, dy, room_colliders.get(tuple(current_room), []))
        room_transition()
    else:
        # When trade menu is active, ensure we don't accidentally slide into walls etc.
        pass

    # ─── Pickups ───
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

    # Do not pick up items while trading (player shouldn't move or pick while trading)
    if not trade_menu_active:
        pickup(gold, "Gold", "Gold", 15, (255, 215, 0), "+15 gold")
        pickup(health_potions, "Health Potions", "Health Potions", 1, (0, 255, 0), "+1 health potion")
        pickup(speed_potions, "Speed Potions", "Speed Potions", 1, (173, 216, 230), "+1 speed potion")
        pickup(strength_potions, "Strength Potions", "Strength Potions", 1, (255, 69, 0), "+1 strength potion")
        pickup(artifacts, "Artifacts", "Artifacts", 1, (160, 32, 240), "+1 artifact")

    # ─── Player Drawing ───
    player_colors = {"up": (255, 255, 0), "down": (0, 255, 0), "left": (255, 0, 0), "right": (0, 0, 255)}
    pygame.draw.rect(screen, player_colors.get(facing, (255, 255, 255)), player)

    # ─── UI Elements ───
    draw_hud(screen, *current_room)
    draw_minimap(screen, *current_room)
    draw_message(screen, message, message_timer, message_color)
    draw_dialogue(screen)
    draw_trade_prompt(screen)
    draw_trade_menu(screen)

    # ─── Dialogue End Check ───
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

    # ─── Timers ───
    # Potion effect timer update
    if strength_potion_duration > 0:
        damage_multiplier = strength_multiplier
        strength_potion_duration = max(0, strength_potion_duration - dt / 1000.0)
    else:
        damage_multiplier = 1

    if speed_potion_duration > 0:
        speed_potion_duration = max(0, speed_potion_duration - dt / 1000.0)

    # Genral message timer update
    if message_timer > 0:
        message_timer -= dt / 1000.0
        if message_timer <= 0:
            message = ""
            message_timer = 0.0

    # Trade feedback timer update 
    if trade_feedback_timer > 0:
        trade_feedback_timer -= dt / 1000.0
        if trade_feedback_timer <= 0:
            trade_feedback = ""
            trade_feedback_timer = 0.0

    pygame.display.flip()

pygame.quit()
