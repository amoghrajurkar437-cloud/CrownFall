# Amogh R and Sebastian M || CROWNFALL
import pygame, os, math, random, json
pygame.init()
os.chdir(os.path.dirname(__file__))  # Make working dir = script folder

# SAVE/LOAD FUNCTIONALITY
SAVE_DIR = "crownfall_saves"
SAVE_FILES = [
    os.path.join(SAVE_DIR, "Save_1.txt"),
    os.path.join(SAVE_DIR, "Save_2.txt"),
    os.path.join(SAVE_DIR, "Save_3.txt"),
]
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

save_screen_active = False
load_screen_active = False
selected_slot = 0
save_btn_rect = None
load_btn_rect = None
slot_rects = []

# CONSTANTS
ROOM_WIDTH = 800
ROOM_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
MAX_UPGRADE_LEVEL = 5

# Basic set up
pygame.display.set_caption("CROWNFALL")
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("crownfall_fonts/MedievalSharp-Regular.ttf", 20)
title_font = pygame.font.Font("crownfall_fonts/MedievalSharp-Regular.ttf", 80)

# Player and Room setup
player = pygame.Rect(50, ROOM_HEIGHT - 100, 80, 80)
facing = "up"
current_room = [0, 0, 0]
room_colliders = {}

# Speed setup
base_speed = 5
speed_potion_duration = 0
speed_multiplier = 2

# Strength setup
damage_multiplier = 1
strength_multiplier = 2

# Inventory set up
inventory = {"Gold": 150, "Artifacts": 7, "Health Potions": 5, "Speed Potions": 5, "Strength Potions": 5, "Upgrade Tokens": 15, "Enemy Shards": 150}
inventory_limits = {"Gold": 150, "Artifacts": 7, "Health Potions": 5, "Speed Potions": 5, "Strength Potions": 5, "Upgrade Tokens": 15, "Enemy Shards": 150}

# Collected sets
c_Artifacts = set()
c_Gold = set()
c_Health_Potions = set()
c_Speed_Potions = set()
c_Strength_Potions = set()

# Minimap
visited_rooms = set() # Tracks rooms the player has visited
minimap_memory = {} # Keeps icons permanently once discovered

# On-screen notifications
message = ""
message_color = None
message_timer = 0.0
feedback = ""
feedback_timer = 0.0

# Flag variables
on_home = True # Player starts in home screen
hud_visible = False # HUD hidden by default
map_visible = False # Map hidden by default
dialogue_active = False # No dialogue active at start
trading_prompt_active = False # Trade prompt not showing
trade_menu_active = False # Trade menu closed
upgrade_menu_active = False # Uograde menu closed
instructions_active = False # Instructions screen flag
lore_screen_active = False # lore screen flag
combat_active = False # Combat flag
player_turn_done = False # Player has acted this turn
enemy_turn_pending = False # Enemy is waiting to take its turn
player_defending = False # Player is defending
enemy_defending = False # Enemy is defending
special_attack_used = False # Special attack used this turn
strength_active = False # Strength potion in combat
player_dead = False # Player death flag
end_screen_active = False # End screen flag
trade_prompt_key = None # Tracks which villager is offering trade
trade_pending_key = None # Marks villager to show trade prompt after dialogue
active_villager_index = None # Which villager for multiple in a room
dialogue_just_finished = False # To trigger trade prompt after dialogue
current_enemy_index = None # Which enemy for multiple in a room
previous_room = None # Tracks last room for enemy respawn logic
enemy_last_action = None # Tracks last action by enemy to not repeat

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
enemy_tiles = []
campfire_tiles = []

# Dialogue set up
dialogue_index = 0
last_dialogue_index = -1
current_dialogue = []

# Key format = (level, row, column, villager_index)
dialogues = {
#LEVEL 1: Bottom Left Villager
    (0, 0, 0, 0): [
        "Villager: The stranger at the edge of town has been brandishing his sword all day. I wonder how he keeps it so clean.",
        "You: I'll have to go check that out. I'll keep you posted.",
        "Villager: Thank you! If you manage to remove him from stoping our trade routes, I'll give you something in return."
    ],
    # LEVEL 1: bottom middle villager
    (0, 0, 1, 0): [
        "Villager: LALALA!",
        "Villager: What are you looking at?",
        "You: Nothing, but you're kinda deranged",
        "Villager: Well I can't help but go insane after this new king just stole all of our money!",
        "Villager: I'M GOING TO GO BROKE!!",
        "You: ...",
        "Villager: BLA BLA"
    ],
    # LEVEL 1: middle left villager
    (0, 1, 0, 0): [
        "Villager: There is a strange looking guy at the edge of the town, he seems like hes a part of the new clan.",
        "Villager: He's stopping all of us from leaving to other towns! :("
    ],
    # LEVEL 1: bottom right villager
    (0, 0, 2, 0): [
        "Villager: Sebastian, DO SOMETHING!!",
        "You: Who is Sebastian?",
        "Villager: I wanna go to sleep :("
    ],
    #LEVEL 1: Top Middle Villager
    (0, 2, 1, 0): [
        "Villager: Amogh, HELP MEEEEEE",
        "Villager: Or maybe I'll go give this nice traveler the most, bestest, GREATEST weapon of all!"
    ],
    #LEVEL 1: Middle Right Villager
    (0, 1, 2, 0): [
        "Villager: Help, I'm under the water. Please help me.",
        "Villager: But if you give me some money, I could save myself."
    ],
    #LEVEL 1: Middle Middle Villager
    (0, 1, 1, 0): [
        "Villager: The Grand Tree. It's been here since I was a kid, my dad was a kid, my grandfather. I think it's been here forever honestly.",
        "You: Yah...I'm not so sure. Seems like it just grew overnight. The bark doesn't look old enough.",
        "Villager: YOU DON'T KNOW  WHAT I KNOW!"
    ],

    # LEVEL 2: bottom right villagers
    (1, 0, 2, 0): [
        "Villager: I don't have a normal sleep schedule",
        "Villager: It's 4:12 am right now",
        "Villager: Through the window, through the wall, till the sweat runs down my skull",
        "Villager: 'till all these screeches crawl"
    ],
    (1, 0, 2, 1): [
        "Villager: I am hungry",
        "You: I have some food, you want it?",
        "Villager: I don't want your food, it could have... poison...",
        "Villager: I'm going to the tavern later to get some food, but thanks"
    ],
    (1, 0, 2, 2): [
        "Villager: The gaurds are going to take my job",
        "Villlager: Im going to be jobless soon enough, I already lost my children and my wife",
        "Villager: When she left that day, to be with the drowibng guy, it hurt my soul"
        "You: Well nothing can take your job of beating Helldivers"
        "Villager: True"
    ],

    # LEVEL 3: bottom middle villagers
    (2, 0, 1, 0): [
        "Villager: I have a headache",
        "Villager: I need water",
        "You: You should go to the other town, this guy was just drowing in the water, heh...heh...",
    ],
    (2, 0, 1, 1): [
        "Villager: Pokemon, got to catch 'em all!",
        "You: What?",
        "Villager: Knock, Knick. Whos there. IDK",
        "You: Weirdo"
    ],
}

# Trade set up
tradeable_villagers = { # Which villager keys are tradeable
    (0, 0, 1, 0),  # Level 1 bottom middle
    (0, 2, 1, 0),  # Level 1 Top Middle Villager
    (0, 1, 2, 0),  #Level 1 Middle Right Villager
    (1, 0, 2, 1),  # Level 2 bottom right (middle villager)
    (2, 0, 1, 0),  # Level 3 bottom middle (left villager)
}
trade_selection = 0
# (inventory key, price)
trade_items = [("Health Potions", 30), ("Speed Potions", 10), ("Strength Potions", 20), ("Upgrade Tokens", 20)]

# Upgrade cost level tables
upgrade_costs_gold = [10, 20, 30, 40, 50] # Gold cost per level
upgrade_costs_tokens = [1, 2, 3, 4, 5] # Token cost per level

# Combat set up
enemy_health = []
enemy_max_health = []
enemy_rects = []
enemy_turn_delay = 0
enemy_delay_frames = 120
dead_enemies = set()
enemy_spawn_points = []
battle_tips = [
    "Defend to reduce incoming damage!",
    "Strength potions increase your attack!",
    "Watch enemy HP—some enemies heal at low health.",
    "Special Attack deals triple damage",
    "Special Attack can be used only once per battle.",
    "You can Run if the fight looks bad!",
    "Use Health Potions to heal mid-battle!",
    "Defeating enemies gives Enemy Shards!",
]
tip_index = 0
tip_timer = 0
# Track which bosses have been defeated
# The [False] * LEVELS creates a list with one False per level
boss_defeated = [False] * LEVELS
boss_phase = [1] * LEVELS # Track which phase each boss is currently in
boss_max_phases = 2 # Every boss has 2 phases
level_passed = [False, False]

# Health set up
max_health = 100 + armor_level * 100  # Base 100 + 100 per armor level
health = max_health

# Boss dialogue setup
# Key = (level, boss_type)
boss_dialogues = {
    (0, "boss1"): [
        "Knight: You think you can do anything, I'm not even the begining.",
        "Knight: You can crush a 1000 more of me but you can't beat him.",
        "You: Your king? I crush him too.",
        "Knight: No, not my king, it's something else."
    ],

    (1, "boss2"): [
        "King: AHHAHAHAHHHAAAHHA.",
        "King: Wait, I'm free now, YES. I'm not being controlled anymore.",
        "You: ???.",
        "You: Who was controlling you?",
        "King: Don't even try kid, he's a literal god, get out of here",
        "King: I'm leaving town, after I gain my trust back, you leave too."
    ],
}
boss_dialogue_played = [False] * LEVELS
current_boss_dialogue = []
enemy_roles = []

# ─── PLAYER ANIMATIONS ───
last_facing = "up"
anim_index = 0
anim_timer = 0
ANIM_SPEED = 9  # Lower is faster
player_images = {
    "up": [],
    "down": [],
    "left": [],
    "right": []
}

for direction in player_images:
    for i in range(1, 7):
        img = pygame.image.load(
            f"crownfall_images/{direction.capitalize()}/{direction.capitalize()}_{i}.png"
        ).convert_alpha()
        img = pygame.transform.scale(img, (80, 80))
        player_images[direction].append(img)

# Music setup
battle_music_timer = 0.0
intro_played = False
main_music_active = False
victory_music_played = False
running_sound_playing = False
is_moving = False
home_music_active = False
death_music_played = False
was_in_lore = False
was_on_home = False
current_music = None  # "home", "main", "intro", "death", "victory"
# Mute toggle
is_muted = False
# Store volumes so unmute restores correctly
MUSIC_VOLUME = 0.5
SFX_VOLUME_PICKUP = 0.5
SFX_VOLUME_RUN = 0.6
INTRO_MUSIC = "crownfall_sounds/intro.mp3"
MAIN_MUSIC = "crownfall_sounds/main_loop.mp3"
BATTLE_INTRO_MUSIC = "crownfall_sounds/battle_intro.mp3"
BATTLE_MUSIC = "crownfall_sounds/battle_main.mp3"
VICTORY_MUSIC = "crownfall_sounds/victory.mp3"
DEATH_MUSIC = "crownfall_sounds/death.mp3"
HOME_MUSIC = "crownfall_sounds/home.mp3"
pickup_sound = pygame.mixer.Sound("crownfall_sounds/pick_up.mp3")
run_sound = pygame.mixer.Sound("crownfall_sounds/run.wav")
pygame.mixer.music.set_volume(MUSIC_VOLUME)
pickup_sound.set_volume(SFX_VOLUME_PICKUP)
run_sound.set_volume(SFX_VOLUME_RUN)

# DRAWING ELEMENTS
def draw_objects(x, y, obj_type, surface):
    """Draws an object on the game surface and adds its collider or collectible
    reference to the appropriate list based on object type."""
    global colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles, enemy_tiles

    def load_img(name, w, h, offset=(0, 0)):
        """Loads, scales, trims transparent padding, draws the image and returns the rect."""
        img = pygame.image.load(f"crownfall_images/{name}.png").convert_alpha()

        # Scale up or down
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
        scale_up_list = {"Rock_1", "Rock_2", "Wall_1", "Wall_2", "boss3"}
        scale_down_list = {"Villager", "Gold"}
        if name in scale_up_list:
            return w * 1.5, h * 1.5
        elif name in scale_down_list:
            return w * .75, h * .75
        elif name == "campfire":
            return w * 5, h * 5
        else:
            return w, h

    # environment objects
    if obj_type == "castle_floor":
        rect = load_img("Castle_floor_bg", 800, 800)
        return rect
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
    elif obj_type == "path":
        rect = load_img("Path", 100, 100)
        return rect

    #Enemies
    elif obj_type == "boss1":
        rect = load_img("Lvl_1_Boss", 524, 800)
        colliders.append(rect)
        enemy_tiles.append(rect)
        enemy_rects.append(rect)
        enemy_spawn_points.append((x, y))
        enemy_health.append(150)
        enemy_max_health.append(150)
        enemy_roles.append(None)  # Bosses have no role
        return rect 
    elif obj_type == "boss2":
        rect = load_img("Lvl_2_Boss", 350, 500)
        colliders.append(rect)
        enemy_tiles.append(rect)
        enemy_rects.append(rect)
        enemy_spawn_points.append((x, y))
        enemy_health.append(200)
        enemy_max_health.append(200)
        enemy_roles.append(None)  # Bosses have no role
        return rect
    elif obj_type == "boss3":
        rect = load_img("Lvl_3_Boss", 400, 504)
        colliders.append(rect)
        enemy_tiles.append(rect)
        enemy_rects.append(rect)
        enemy_spawn_points.append((x, y))
        enemy_health.append(250)
        enemy_max_health.append(250)
        enemy_roles.append(None)  # Bosses have no role
        return rect
    elif obj_type == "enemy":
        rect = load_img("Enemy", 100, 100)
        colliders.append(rect)
        enemy_tiles.append((rect))
        enemy_rects.append((rect))
        enemy_spawn_points.append((x, y))
        base_hp = 100 + (current_room[0] * 50) # Base HP increases with level
        enemy_health.append(base_hp)
        enemy_max_health.append(base_hp)
        # ---- ROLE ASSIGNMENT ----
        role = random.choice(["beserk", "guardian", "assassin", "tank"])
        enemy_roles.append(role)
        # ---- ROLE HP MODIFIERS ----
        if role == "guardian":
            enemy_health[-1] = int(enemy_health[-1] * 1.2)
        elif role == "tank":
            enemy_health[-1] = int(enemy_health[-1] * 1.4)
        elif role == "assassin":
            enemy_health[-1] = int(enemy_health[-1] * 0.8)
        elif role == "beserk":
            enemy_health[-1] = int(enemy_health[-1] * 1.0)
        enemy_max_health[-1] = enemy_health[-1]
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
    elif obj_type == "campfire":
        rect = load_img("Campfire", 200, 200)
        colliders.append(rect)
        campfire_tiles.append(rect)
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
    """Draws the current room based on the level, row, and column.
    Adds interactive and environmental objects to their respective lists."""

    global colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles, upgrade_hut_tiles, enemy_tiles, enemy_health, enemy_max_health, enemy_rects, previous_room

    # Draw background
    bg = pygame.image.load("crownfall_images/Level_bg_1.jpg").convert()
    bg = pygame.transform.scale(bg, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(bg, (0, 0))

    # Object containers for this room
    colliders, artifacts, gold, health_potions, speed_potions, strength_potions, water_tiles, villager_tiles, upgrade_hut_tiles, enemy_tiles = [], [], [], [], [], [], [], [], [], []

    current = (level, row, col)
    # Only clear if we enetered a different room and we're not already in combat
    if not combat_active and current != previous_room:
        enemy_rects.clear()
        enemy_health.clear()
        enemy_max_health.clear()
        enemy_spawn_points.clear()
        enemy_roles.clear()

    # Update room tracking
    previous_room = current
    visited_rooms.add((level, row, col))

    def can_draw(anchor_x, anchor_y, sset):
        """checks if a collectable should be drawn on the screen"""
        # Return True or False based on whether the item has been collected
        return (level, row, col, anchor_x, anchor_y) not in sset

    # ───────── LEVEL 1 ─────────
    # Level 1 Bottom Left
    if level == 0 and row == 0 and col == 0:
        for x in [130, 230, 330, 430, 530]:
            draw_objects(x, 625, "path", surface) # Path
        for x in [530, 630, 730]:
            draw_objects(x, 525, "path", surface) # Path
        draw_objects(400, 250, "house1", surface) # House 1
        draw_objects(245, 320, "tree1", surface) # Tree 1
        draw_objects(25, 50, "rock1", surface) # Rock 1
        draw_objects(175, 25, "rock2", surface) # Rock 2
        if can_draw(600, 150, c_Artifacts):
            draw_objects(600, 150, "artifact", surface)  # Artifact
        draw_objects(675, 380, "villager", surface) #Villager

    # Level 1: Bottom Middle
    elif level == 0 and row == 0 and col == 1:
        for x in [0,100,200,300,400]:
            draw_objects(x, 525, "path", surface) # Path
        # vertical column of paths at x=400
        for y in [525,425,325,225,125,25,0]:
            draw_objects(400, y, "path", surface) # Path
        for x in [500,600,700]:
            draw_objects(x, 525, "path", surface) # Path
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
        for x in [0,100,200,300]:
            draw_objects(x, 525, "path", surface) # Path
        draw_objects(400, 500, "path", surface) # Path
        draw_objects(500, 475, "path", surface) # Path
        draw_objects(600, 450, "path", surface) # Path
        draw_objects(350, 150, "house2", surface)  # House 2
        draw_objects(120, 220, "tree1", surface)   # Tree 1
        draw_objects(450, 500, "rock1", surface)   # Rock 1
        draw_objects(600, 400, "villager", surface)  # Villager
        if can_draw(700, 100, c_Artifacts):
            draw_objects(700, 100, "artifact", surface)  # Artifact

    # Level 1: Middle Left
    elif level == 0 and row == 1 and col == 0:
        for x in [700,600,500]:
            draw_objects(x, 525, "path", surface) # Path
        draw_objects(245, 270, "tree1", surface)  # Tree 1
        draw_objects(600, 350, "rock1", surface)  # Rock 1
        draw_objects(25, 25, "villager", surface)  # Villager
        if can_draw(400, 150, c_Health_Potions):
            draw_objects(400, 150, "health_potion", surface)  # Health Potion
        if can_draw(700, 500, c_Gold):
            draw_objects(700, 500, "gold", surface)  # Gold

    # Level 1: Middle
    elif level == 0 and row == 1 and col == 1:
        for x in [0,100,200,300,400,500,600,700]:
            draw_objects(x, 525, "path", surface) # Path
        for y in [425,325,225,125,25,0]:
            draw_objects(100, y, "path", surface) # Path
        if can_draw(200, 450, dead_enemies):
            draw_objects(200, 450, "enemy", surface) # Enemy
        draw_objects(400, 700, "path", surface) # Path
        draw_objects(400, 600, "path", surface) # Path
        draw_objects(400, 250, "house1", surface)  # House 1
        draw_objects(150, 180, "tree1", surface)   # Tree 1
        if can_draw(600, 150, c_Gold):
            draw_objects(600, 150, "gold", surface)  # Gold
        if can_draw(700, 400, c_Artifacts):
            draw_objects(700, 400, "artifact", surface)  # Artifact
        draw_objects(325, 350, "villager", surface) #Villager

    # Level 1: Middle Right
    elif level == 0 and row == 1 and col == 2:
        for x in [0,100,200,300]:
            draw_objects(x, 525, "path", surface) # Path
        for y in [425,325]:
            draw_objects(300, y, "path", surface) # Path
        if can_draw(450, 200, dead_enemies):
            draw_objects(450, 200, "enemy", surface) # Enemy
        draw_objects(100, 200, "rock2", surface)  # Rock 2
        if can_draw(500, 250, c_Speed_Potions):
            draw_objects(500, 250, "speed_potion", surface)  # Speed Potion
        draw_objects(400, 400, "water", surface)  # Water
        draw_objects(550, 375, "villager", surface) #villager

    # Level 1: Top Left
    elif level == 0 and row == 2 and col == 0:
        for x in [700,600,500,450]:
            draw_objects(x, 300, "path", surface) # Path
        draw_objects(220, 245, "tree1", surface)  # Tree 1
        draw_objects(400, 400, "rock1", surface)  # Rock 1
        draw_objects(400, 50, "upgrade_hut", surface) # Upgrade Hut
        if can_draw(200, 150, c_Gold):
            draw_objects(200, 150, "gold", surface)  # Gold

    # Level 1: Top Middle
    elif level == 0 and row == 2 and col == 1:
        for y in [700,600,500,400,300]:
            draw_objects(100, y, "path", surface) # Path
        for x in [200,300,400,500,0]:
            draw_objects(x, 300, "path", surface) # Path
        if can_draw(600, 400, dead_enemies):
            draw_objects(600, 400, "enemy", surface) # Enemy
        if can_draw(150, 350, dead_enemies):
            draw_objects(150, 350, "enemy", surface) # Enemy
        draw_objects(620, 170, "tree2", surface)  # Tree 2
        draw_objects(200, 25, "house1", surface)  # House 1
        if can_draw(100, 200, c_Health_Potions):
            draw_objects(100, 200, "health_potion", surface)  # Health Potion
        if can_draw(50, 100, c_Gold):
            draw_objects(50, 100, "gold", surface)  # Gold
        draw_objects(500, 150, "villager", surface) #Villager

    # Level 1: Top Right
    elif level == 0 and row == 2 and col == 2:
        for x in [498, 499, 500, 501, 502, 503, 504, 505, 506]:
            if can_draw(x, 150, c_Gold):   
                draw_objects(x, 150, "gold", surface)   #Gold
        for y in [150, 151, 152, 153, 154, 155, 156, 157, 158]:
            if can_draw(500, y, c_Gold):    
                draw_objects(500, y, "gold", surface)   #Gold
        if can_draw(189, -100, dead_enemies):
            draw_objects(189, -100, "boss1", surface) #Boss

    # ───────── LEVEL 2 ─────────
    # Level 2: Bottom Left
    if level == 1 and row == 0 and col == 0:
        for x in [500,600,700]:
            draw_objects(x, 600, "path", surface) # Path
        if can_draw(300, 300, dead_enemies):
            draw_objects(300, 300, "enemy", surface) # Enemy
        draw_objects(620, 420, "tree2", surface)  # Tree 2
        if can_draw(100, 100, c_Gold):
            draw_objects(100, 100, "gold", surface)  # Gold
        if can_draw(500, 350, c_Health_Potions):
            draw_objects(500, 350, "health_potion", surface)  # Health potion

    # Level 2: Bottom Middle
    elif level == 1 and row == 0 and col == 1:
        for x in [0,100,200,300,400,500]:
            draw_objects(x, 600, "path", surface) # Path
        for y in [500,400,300,200,100,0]:
            draw_objects(500, y, "path", surface) # Path
        for x in [600,700]:
            draw_objects(x, 200, "path", surface) # Path
        for y in [325, 500, 700]:
            draw_objects(650, y, "wall2", surface) # Wall 2
        if can_draw(600, 500, dead_enemies):
            draw_objects(600, 500, "enemy", surface) # Enemy
        draw_objects(400, 300, "rock2", surface)  # Rock 2
        draw_objects(200, 170, "tree1", surface)  # Tree 1

    # Level 2: Bottom Right
    elif level == 1 and row == 0 and col == 2:
        for x in [0,100,200]:
            draw_objects(x, 200, "path", surface) # Path
        for x in [-200,0,200,600]:
            draw_objects(x, 200, "wall1", surface) # Wall 1
        for y in [500,450,400,350]:
            draw_objects(-130, y, "wall2", surface) # Wall 2
        if can_draw(500, 300, dead_enemies):
            draw_objects(500, 300, "enemy", surface) # Enemy
        draw_objects(200, 400, "villager", surface) # Villager
        draw_objects(400, 350, "villager", surface) # Villager
        draw_objects(650, 400, "villager", surface) # Villager

    # Level 2: Middle Left
    elif level == 1 and row == 1 and col == 0:
        draw_objects(780, -625, "castle_floor", surface) # Castle floor
        for x in [700,600]:
            draw_objects(x, 300, "path", surface) # Path
        draw_objects(400, 100, "upgrade_hut", surface) # Upgrade
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
        draw_objects(0, -625, "castle_floor", surface) # Castle floor
        for y in [700,600,500,400,300,200]:
            draw_objects(500, y, "path", surface) # Path
        for x in [0,100,200,300,400]:
            draw_objects(x, 300, "path", surface) # Path
        for x in [-100,0,200,600]:
            draw_objects(x, 0, "wall1", surface) # Wall 1
        if can_draw(150, 250, dead_enemies):
            draw_objects(150, 250, "enemy", surface) # Enemy
        if can_draw(400, 400, c_Health_Potions):
            draw_objects(400, 400, "health_potion", surface) # Health Potion
        if can_draw(700, 200, c_Gold):
            draw_objects(700, 200, "gold", surface) # Gold

    # Level 2: Middle Right
    elif level == 1 and row == 1 and col == 2:
        draw_objects(0, -625, "castle_floor", surface) # Castle floor
        for x in [-100,0,200,400,600]:
            draw_objects(x, 0, "wall1", surface) # Wall 1
        draw_objects(100, 350, "tree1", surface) # Tree 1
        draw_objects(300, 250, "campfire", surface) # Campfire
        if can_draw(500, 300, c_Artifacts):
            draw_objects(500, 300, "artifact", surface) # Artifact

    # Level 2: Top Left
    elif level == 1 and row == 2 and col == 0:
        draw_objects(750, 0, "castle_floor", surface) # Castle floor
        for y in [-200,0,200,400, 600]:
            draw_objects(600, y, "wall2", surface) # Wall 2
        if can_draw(200, 400, dead_enemies):
            draw_objects(200, 400, "enemy", surface) # Enemy
        if can_draw(100, 200, dead_enemies):
            draw_objects(100, 200, "enemy", surface) # Enemy
        draw_objects(400, 300, "rock1", surface) # Rock 1
        draw_objects(220, 220, "tree2", surface) # Tree 2
        if can_draw(450, 100, c_Artifacts):
            draw_objects(450, 100, "artifact", surface) # Artifact

    # Level 2: Top Middle
    elif level == 1 and row == 2 and col == 1:
        draw_objects(0, 0, "castle_floor", surface) # Castle floor
        if can_draw(600, 150, dead_enemies):
            draw_objects(600, 150, "enemy", surface) # Enemy
        if can_draw(300, 250, c_Health_Potions):
            draw_objects(300, 250, "health_potion", surface) # Health Potion
        if can_draw(500, 350, c_Artifacts):
            draw_objects(500, 350, "artifact", surface) # Artifact
        if can_draw(150, 150, dead_enemies):
            draw_objects(150, 150, "enemy", surface) # Enemy
        if can_draw(700, 150, c_Gold):
            draw_objects(700, 150, "gold", surface) # Gold
        if can_draw(100, 450, c_Gold):
            draw_objects(100, 450, "gold", surface) # Gold

    # Level 2: Top Right
    elif level == 1 and row == 2 and col == 2:
        draw_objects(0, 0, "castle_floor", surface) # Castle floor
        if can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion
        for x in [300, 301, 302, 303, 304, 305, 306]:
            if can_draw(x, 200, c_Gold):
                draw_objects(x, 200, "gold", surface) # Gold
        if can_draw(290, 200, c_Health_Potions):
            draw_objects(290, 200, "health_potion", surface) # Health potion
        if can_draw(290, 400, c_Speed_Potions):
            draw_objects(290, 400, "speed_potion", surface) # Speed potion
        for x in [300, 301]:
            if can_draw(x, 300, c_Strength_Potions):
                draw_objects(x, 300, "strength_potion", surface) # Strength potion
        if can_draw(150, 100, c_Artifacts):
            draw_objects(150, 100, "artifact", surface) # Artifact
        if can_draw(200, 50, dead_enemies):
            draw_objects(200, 50, "boss2", surface) # Boss

    # ───────── LEVEL 3 ─────────
    # Level 3: Bottom Left
    if level == 2 and row == 0 and col == 0:
        if can_draw(300, 200, dead_enemies):
            draw_objects(300, 200, "enemy", surface) # Enemy
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
        if can_draw(150, 400, dead_enemies):
            draw_objects(150, 400, "enemy", surface) # Enemy
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
        if can_draw(350, 250, dead_enemies):
            draw_objects(350, 250, "enemy", surface) # Enemy
        draw_objects(400, 300, "rock2", surface) # Rock 2
        draw_objects(170, 170, "tree2", surface) # Tree 3
        if can_draw(350, 200, c_Health_Potions):
            draw_objects(350, 200, "health_potion", surface) # Health Potion

    # Level 3: Middle
    elif level == 2 and row == 1 and col == 1:
        draw_objects(300, 100, "house2", surface) # House 2
        if can_draw(200, 300, c_Health_Potions):
            draw_objects(200, 300, "health_potion", surface) # Health Potion
        if can_draw(600, 550, dead_enemies):
            draw_objects(600, 550, "enemy", surface) # Enemy
        if can_draw(700, 25, c_Gold):
            draw_objects(700, 25, "gold", surface) # Gold

    # Level 3: Middle Right
    elif level == 2 and row == 1 and col == 2:
        draw_objects(220, 320, "tree2", surface) # Tree
        if can_draw(400, 300, dead_enemies):
            draw_objects(400, 300, "enemy", surface) # Enemy
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
        if can_draw(500, 450, dead_enemies):
            draw_objects(500, 450, "enemy", surface) # Enemy
        draw_objects(270, 120, "tree1", surface) # Tree 1

    # Level 3: Top Middle
    elif level == 2 and row == 2 and col == 1:
        draw_objects(20, 170, "tree1", surface) # Tree 1
        draw_objects(420, 270, "tree2", surface) # Tree 2
        if can_draw(200, 250, dead_enemies):
            draw_objects(200, 250, "enemy", surface) # Enemy
        if can_draw(100, 25, dead_enemies):
            draw_objects(100, 25, "enemy", surface) # Enemy
        if can_draw(500, 25, c_Gold):
            draw_objects(500, 25, "gold", surface) # Gold
        if can_draw(400, 600, c_Gold):
            draw_objects(400, 600, "gold", surface) # Gold

    # Level 3: Top Right
    elif level == 2 and row == 2 and col == 2:
        if can_draw(600, 250, c_Gold):
            draw_objects(600, 250, "gold", surface) # Gold
        if can_draw(200, 150, dead_enemies):
            draw_objects(200, 150, "boss3", surface) # Boss

    # Save minimap data for the 
    # Tuple = (level, row, col)
    room_id = tuple(current_room)
    minimap_memory[room_id] = {
        "villagers": [(v.x, v.y) for v in villager_tiles],
        "enemies": [(e.x, e.y) for e in enemy_tiles],
        "huts": [(h.x, h.y) for h in upgrade_hut_tiles]
    }

# DRAWING HUD
def draw_hud(surface):
    """Draws the player HUD (health + inventory) when visible."""
    if not hud_visible:
        return  # Don't draw anything if HUD is hidden

    global map_visible, trading_prompt_active

    # Close map or trading prompt if HUD is opened
    if map_visible:
        map_visible = not map_visible
    elif trading_prompt_active:
        trading_prompt_active = not trading_prompt_active

    level, row, col = current_room  # Unpack current room
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

    # --- Upgrades and gold-per-pickup ---
    aw_box_w = 520
    aw_box_h = 80
    aw_box_x = (ROOM_WIDTH - aw_box_w) // 2
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

    # --- Gold per pickup box ---
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
    map_size = 180
    cell_size = map_size // GRID_WIDTH
    map_x = ROOM_WIDTH // 2 - map_size // 2
    map_y = pickup_box_y + pickup_box_h + 20

    # background box
    pygame.draw.rect(surface, (100, 100, 100), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    pygame.draw.rect(surface, (255, 255, 255), (map_x - 5, map_y - 5, map_size + 10, map_size + 10), 2)

    # draw all rooms (visited light, unvisited dark)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            x = map_x + c * cell_size
            y = map_y + (GRID_HEIGHT - 1 - r) * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)

            room_id = (level, r, c)

            if room_id not in visited_rooms:
                pygame.draw.rect(surface, (0, 0, 0), rect)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

    # draw icons for every visited room (villagers, enemies, huts)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            room_id = (level, r, c)
            if room_id in visited_rooms:
                draw_minimap_icons(surface, map_x, map_y, map_size, ROOM_WIDTH, ROOM_HEIGHT, room_id)

    # draw player icon
    _, room_r, room_c = tuple(current_room)
    cell_w = map_size // GRID_WIDTH
    cell_h = map_size // GRID_HEIGHT
    room_origin_x = map_x + room_c * cell_w
    room_origin_y = map_y + (GRID_HEIGHT - 1 - room_r) * cell_h
    sx = cell_w / ROOM_WIDTH
    sy = cell_h / ROOM_HEIGHT
    px = room_origin_x + player.x * sx
    py = room_origin_y + player.y * sy
    pygame.draw.rect(surface, (0, 255, 0), (px, py, 5, 5))

    # Level location label
    # Picking from lists to convert row/col to text
    text = f"Level {level + 1} - {['Bottom','Middle','Top'][row]} {['Left','Middle','Right'][col]}"
    info = font.render(text, True, (255, 255, 255))
    info_rect = info.get_rect(center=(ROOM_WIDTH // 2, map_y + 200))

    pygame.draw.rect(surface, (0, 0, 0), (info_rect.left - 10, info_rect.top - 5, info_rect.width + 20, info_rect.height + 10))
    pygame.draw.rect(surface, (255, 255, 255), (info_rect.left - 10, info_rect.top - 5, info_rect.width + 20, info_rect.height + 10), 2)
    surface.blit(info, info_rect)

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

    y = effect_box_y + 46
    if speed_potion_duration > 0:
        spd = font.render(f"Speed x{speed_multiplier} ({int(speed_potion_duration)}s)", True, (255, 255, 255))
        surface.blit(spd, (effect_box_x + effect_box_w // 2, y))
        y += 28

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
    txt = font.render("Would you like to trade? (Y/N)", True, (255, 255, 255))
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
    feedback_y = y + 5
    if feedback:
        fb_surf = font.render(feedback, True, (255, 255, 255))
        fb_rect = fb_surf.get_rect(center=(box_x + box_w // 2, feedback_y))
        surface.blit(fb_surf, fb_rect)
    inventory_top = feedback_y + 50

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
    # Draw nothing if upgrade menu is not active
    if not upgrade_menu_active:
        return

    global gold_per_pickup

    draw_overlay(surface)
    # Content box area (centered panel)
    box_w, box_h = 700, 520
    box_x = (ROOM_WIDTH - box_w) // 2
    box_y = (ROOM_HEIGHT - box_h) // 2

    # Draw an inner panel to place text on
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
        # Don't go past max level
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
        benefit_desc = f"+100 Max Health per level"
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
        max_health += 100
        health = min(max_health, health + 100)
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
                pass
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
    hdr = title_font.render("CONTROLS", True, (255, 255, 255))
    surface.blit(hdr, hdr.get_rect(center=(x + w//2, y + 40)))

    # Controls text
    lines = [
        "Movement:  WASD  or  Arrow Keys",
        "Use Speed Potion:  1",
        "Use Health Potion: 2",
        "Toggle HUD:  E",
        "Toggle Map:  M",
        "Interact / Talk:  Right-Click",
        "Close Menus: ESC",
        "Back to Home: Hold CRTL + 9",
        "Wipe Saves: HolD CTRL + 0",
        "Save Progress: Hold CTRL + S",
        "Load Progress: Hold CTRL + L",
        ""
    ]

    # Draw each line
    start_y = y + 100
    for i, line in enumerate(lines):
        txt = font.render(line, True, (255, 255, 255))
        surface.blit(txt, (x + 36, start_y + i * 30))

    # Closing hint / buttons
    hint = font.render("Press ESC to return", True, (180, 180, 180))
    surface.blit(hint, hint.get_rect(center=(x + w//2, y + h - 36)))

# DRAWING Loading SCREEN
def draw_lore_screen(surface):
    """lore screen with lore + waits for SPACE to continue."""

    draw_overlay(surface)

    # panel
    w, h = 720, 520
    x = (ROOM_WIDTH - w) // 2
    y = (ROOM_HEIGHT - h) // 2
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((12, 12, 18, 240))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 3)

    title = title_font.render("LOADING...", True, (255, 255, 255))
    surface.blit(title, title.get_rect(center=(x + w//2, y + 60)))

    lore = [
        "The kingdom has collapsed under the rule of a corrupt king.",
        "Villages have been drained of resources. Trade has been blocked.",
        "Travelers vanish. Rumors spread of strange forces rising.",
        "",
        "Your mission:",
        "- Explore the 3 regions",
        "- Gather gold, artifacts, and potions",
        "- Upgrade your gear",
        "- Restore balance to the land",
        "",
        "Press SPACE to begin..."
    ]

    start_y = y + 150
    for i, line in enumerate(lore):
        txt = font.render(line, True, (255, 255, 255))
        surface.blit(txt, (x + 40, start_y + i * 32))

# DRAWING COMBAT SCREEN
def draw_combat_screen(surface):
    """Draws the combat screen overlay with health bars, buttons, and turn info."""
    draw_overlay(surface)

    # Centered panel
    w, h = 700, 520
    x = (ROOM_WIDTH - w) // 2
    y = (ROOM_HEIGHT - h) // 2

    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 240))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 3)

    # ----- HEALTH BARS -----

    # Player health bar
    p_bar_w = 220
    p_bar_h = 20
    px = x + w - p_bar_w - 40
    py = y + 30
    pygame.draw.rect(surface, (0,0,0), (px, py, p_bar_w, p_bar_h))
    pygame.draw.rect(surface, (255,255,255), (px, py, p_bar_w, p_bar_h), 2)
    pygame.draw.rect(surface, (255,0,0), (px, py, p_bar_w, p_bar_h))
    p_pct = max(0, health / max_health)
    pygame.draw.rect(surface, (0,255,0), (px, py, p_bar_w * p_pct, p_bar_h))
    p_label = font.render("PLAYER", True, (255,255,255))
    p_label_x = px + (p_bar_w // 2) - (p_label.get_width() // 2)
    p_label_y = py - p_label.get_height() - 4
    surface.blit(p_label, (p_label_x, p_label_y))
    p_hp_text = font.render(f"{int(health)}/{max_health}", True, (255,255,255))
    surface.blit(p_hp_text, (px + p_bar_w//2 - p_hp_text.get_width()//2, py + p_bar_h + 5))

    # Enemy health bar
    if current_enemy_index is not None:
        e_bar_w = 220
        e_bar_h = 20
        ex = x + 40
        ey = y + 30
        pygame.draw.rect(surface, (0,0,0), (ex, ey, e_bar_w, e_bar_h))
        pygame.draw.rect(surface, (255,255,255), (ex, ey, e_bar_w, e_bar_h), 2)
        pygame.draw.rect(surface, (255,0,0), (ex, ey, e_bar_w, e_bar_h))
        e_pct = max(0, enemy_health[current_enemy_index] / enemy_max_health[current_enemy_index])
        role = enemy_roles[current_enemy_index]
        pygame.draw.rect(surface, (0,255,0), (ex, ey, e_bar_w * e_pct, e_bar_h))
    e_label = font.render("ENEMY", True, (255,255,255))
    e_label_x = ex + (e_bar_w // 2) - (e_label.get_width() // 2)
    e_label_y = ey - e_label.get_height() - 4
    surface.blit(e_label, (e_label_x, e_label_y))
    e_cur = enemy_health[current_enemy_index]
    e_max = enemy_max_health[current_enemy_index]
    e_hp_text = font.render(f"{int(e_cur)}/{e_max}", True, (255,255,255))
    surface.blit(e_hp_text, (ex + e_bar_w//2 - e_hp_text.get_width()//2, ey + e_bar_h + 5))
    # --- Enemy Role Display ---
    if combat_active and current_enemy_index is not None:
        role = enemy_roles[current_enemy_index]
        if role is not None: # Boss safety
            role_text = font.render("", True, (255, 200, 50))
            if role == "tank":
                role_text = font.render(f"{role.upper()} / MORE HEALTH", True, (255, 200, 50))
            elif role == "beserk":
                role_text = font.render(f"{role.upper()} / MORE OFFENSE", True, (255, 80, 150))
            elif role == "guardian":
                role_text = font.render(f"{role.upper()} / MORE DEFENSE", True, (100, 200, 100))
            elif role == "assassin":
                role_text = font.render(f"{role.upper()} / MORE DAMAGE & LESS HEALTH", True, (255, 50, 50))
            else:
                pass
            role_rect = role_text.get_rect(center=(ROOM_WIDTH // 2, 240))

            # Clear background behind text (prevents stacking artifacts)
            bg = pygame.Surface((role_rect.width + 20, role_rect.height + 10))
            bg.fill((0, 0, 0))
            screen.blit(bg, (role_rect.x - 10, role_rect.y - 5))

            screen.blit(role_text, role_rect)

    # Loads the enemy in the battle
    l, r, c = current_room
    if l == 0 and r == 2 and c == 2:
        image = pygame.image.load("crownfall_images/Lvl_1_Boss.png").convert_alpha()
        scaled_image = pygame.transform.scale(image, (242, 375))
        surface.blit(scaled_image, (75, 170))
    elif l == 1 and r == 2 and c == 2:
        image = pygame.image.load("crownfall_images/Lvl_2_Boss.png").convert_alpha()
        surface.blit(image, (75, 260))
    elif l == 2 and r == 2 and c == 2:
        image = pygame.image.load("crownfall_images/Lvl_3_Boss.png").convert_alpha()
        scaled_image = pygame.transform.scale(image, (160, 290))
        surface.blit(scaled_image, (100, 215))
    else:
        image = pygame.image.load("crownfall_images/Enemy.png").convert_alpha()
        surface.blit(image, (80, 275))

    # Six buttons
    btn_names = ["Health Potion", "Strength Potion", "Special Attack", "Attack", "Defend", "Run"]
    btn_rects = []

    btn_w, btn_h = 180, 50
    spacing = 10
    start_x = x + (w - (btn_w * 3 + spacing * 2)) // 2
    start_y = y + h - 150

    idx = 0
    for row in range(2):
        for col in range(3):
            bx = start_x + col * (btn_w + spacing)
            by = start_y + row * (btn_h + spacing)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            pygame.draw.rect(surface, (12, 12, 18), rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)

            text = font.render(btn_names[idx], True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

            btn_rects.append((rect, btn_names[idx]))
            idx += 1

            # --- POTION HOVER TOOLTIP ---
            mouse_x, mouse_y = pygame.mouse.get_pos()
            item_info_text = None
            if rect.collidepoint(mouse_x, mouse_y):
                if btn_names[idx-1] == "Health Potion":
                    count = inventory.get("Health Potions", 0)
                    item_info_text = f"{count} left (Heals 25 HP)"
                elif btn_names[idx-1] == "Strength Potion":
                    count = inventory.get("Strength Potions", 0)
                    item_info_text = f"{count} left (Double Damage on all attacks)"
                elif btn_names[idx-1] == "Special Attack":
                    item_info_text = "Triple damage for 1 turn" 
                else:
                    item_info_text = None

                if item_info_text:
                    tip_surf = font.render(item_info_text, True, (255, 255, 255))

                    # tooltip background
                    pad = 6
                    box_w = tip_surf.get_width() + pad * 2
                    box_h = tip_surf.get_height() + pad * 2
                    box_x = rect.centerx - box_w // 2
                    box_y = rect.top - box_h - 8  # Above the button

                    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_w, box_h))
                    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)
                    surface.blit(tip_surf, (box_x + pad, box_y + pad))

    # Turn counter
    turn_text = "PLAYER TURN" if not enemy_turn_pending else "ENEMY TURN"
    color = (0,255,0) if turn_text == "PLAYER TURN" else (255,100,100)
    turn_surf = font.render(turn_text, True, color)
    turn_rect = turn_surf.get_rect(center=(x + w//2, y + 25))
    surface.blit(turn_surf, turn_rect)

    # --- Cinematic Bars ---
    bar_h = 40
    # Top bar
    pygame.draw.rect(surface, (0, 0, 0), (0, 0, ROOM_WIDTH, bar_h))
    # Bottom bar
    pygame.draw.rect(surface, (0, 0, 0), (0, ROOM_HEIGHT - bar_h, ROOM_WIDTH, bar_h))

    # Title text in the top bar
    title_text = title_font.render("CROWNFALL", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(ROOM_WIDTH // 2, bar_h // 2 + 50))
    surface.blit(title_text, title_rect)

    # --- Rotating Battle Tips Box ---
    global tip_index, tip_timer

    tip_box_w = w - 80
    tip_box_h = 50
    tip_box_x = x + 40
    tip_box_y = y + h

    # Box
    pygame.draw.rect(surface, (20, 20, 20), (tip_box_x, tip_box_y, tip_box_w, tip_box_h))
    pygame.draw.rect(surface, (255, 255, 255), (tip_box_x, tip_box_y, tip_box_w, tip_box_h), 2)
    # Timer — change tip every 4 seconds
    tip_timer += 1
    if tip_timer >= 240:  # 60 FPS × 4 seconds
        tip_index = (tip_index + 1) % len(battle_tips)
        tip_timer = 0
    # Draw tip text
    tip_surf = font.render(battle_tips[tip_index], True, (200, 200, 200))
    tip_rect = tip_surf.get_rect(center=(tip_box_x + tip_box_w // 2, tip_box_y + tip_box_h // 2))
    surface.blit(tip_surf, tip_rect)

    # On screen feedback
    if feedback and feedback_timer > 0:
        fb_surf = font.render(feedback, True, (255,255,255))
        fb_rect = fb_surf.get_rect(center=(x + w//2, start_y - 75))
        surface.blit(fb_surf, fb_rect)
    return btn_rects

# ENEMY TURN AI
def run_enemy_turn():
    """Smarter enemy AI with action memory, roles, and contextual behavior."""
    global health, enemy_turn_pending, player_defending, enemy_defending
    global enemy_heals_used, player_dead, combat_active, feedback, feedback_timer
    global enemy_last_action

    enemy_hp = enemy_health[current_enemy_index]
    enemy_max = enemy_max_health[current_enemy_index]

    # --- Context checks ---
    low_hp = enemy_hp < enemy_max * 0.35

    lvl_idx, r_idx, c_idx = current_room
    is_boss = (r_idx == GRID_HEIGHT - 1 and c_idx == GRID_WIDTH - 1)
    boss_phase_num = boss_phase[lvl_idx] if is_boss else None

    # --- Role (bosses have None) ---
    role = enemy_roles[current_enemy_index] if not is_boss else None
    if role is None:
        role = "normal"

    # --- Base weights ---
    weights = {
        "attack": 40,
        "defend": 25,
        "heal": 20
    }

    # ROLE-BASED MODIFIERS
    if role == "berserk":
        weights["attack"] += 25
        weights["defend"] -= 10

    elif role == "guardian":
        weights["defend"] += 10
        if low_hp:
            weights["defend"] += 20
        weights["attack"] -= 5

    elif role == "assassin":
        weights["attack"] += 15
        weights["defend"] -= 10

    # --- Player defending → enemy more aggressive ---
    if player_defending:
        weights["defend"] -= 15
        weights["attack"] += 10

    # --- Avoid repeating last action ---
    if enemy_last_action:
        weights[enemy_last_action] *= 0.3

    # --- Healing rules ---
    can_heal = (
        enemy_heals_used < 5
        and enemy_hp < enemy_max
        and (enemy_max - enemy_hp) >= 20
    )

    if not can_heal:
        weights["heal"] = 0

    # --- Boss Phase 1 behavior ---
    if is_boss and boss_phase_num == 1:
        weights["heal"] = 0
        weights["attack"] += 20
        weights["defend"] -= 10

    # --- Low HP behavior ---
    if low_hp:
        weights["defend"] += 10
        if can_heal:
            weights["heal"] += 15

    # --- Clamp weights ---
    for k in weights:
        weights[k] = max(0, int(weights[k]))

    # --- Weighted choice ---
    actions = []
    for action, weight in weights.items():
        actions.extend([action] * weight)

    enemy_choice = random.choice(actions) if actions else "attack"
    enemy_last_action = enemy_choice

    # EXECUTE ACTION
    if enemy_choice == "attack":
        # --- Damage ---
        if is_boss:
            if boss_phase_num == 1:
                dmg = random.randint(15, 20)
            elif boss_phase_num == 2:
                dmg = random.randint(20, 25)
            else:
                dmg = random.randint(15, 20)
        else:
            dmg = random.randint(8, 15)

        if player_defending:
            roll = random.random()
            if roll < 0.25:
                final_dmg = dmg
                feedback = f"Enemy hits you for {final_dmg} damage!"
            elif roll < 0.75:
                final_dmg = dmg // 2
                feedback = f"Enemy partially hits you for {final_dmg} damage!"
            else:
                final_dmg = 0
                feedback = "Enemy attack MISSES!"
        else:
            final_dmg = dmg
            feedback = f"Enemy hits you for {final_dmg} damage!"

        health = max(0, health - final_dmg)
        feedback_timer = 2.0
        player_defending = False

        if health <= 0:
            combat_active = False
            player_dead = True
            boss_phase[lvl_idx] = 1
            enemy_turn_pending = False
            return

    elif enemy_choice == "defend":
        enemy_defending = True
        feedback, feedback_timer = "Enemy defends!", 2.0

    elif enemy_choice == "heal":
        heal_amount = 20
        enemy_health[current_enemy_index] = min(enemy_max, enemy_hp + heal_amount)
        enemy_heals_used += 1
        feedback, feedback_timer = f"Enemy heals for {heal_amount} HP!", 2.0

    # --- End enemy turn ---
    enemy_turn_pending = False

# Boss Dialogue
def start_boss_dialogue(level, boss_type):
    global dialogue_active, current_dialogue, dialogue_index, current_boss_dialogue

    current_boss_dialogue = boss_dialogues.get((level, boss_type), [])
    if not current_boss_dialogue:
        return

    current_dialogue = current_boss_dialogue
    dialogue_index = 0
    dialogue_active = True

# DRAWING DEATH SCREEN
def draw_death_screen(surface):
    global death_home_btn, death_load_btn

    # --- FULLSCREEN BACKGROUND PANEL (same size as combat area) ---
    # dark red transparent overlay
    fullscreen_panel = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    fullscreen_panel.fill((120, 0, 0, 180))  # R, G, B, A
    surface.blit(fullscreen_panel, (0, 0))

    # --- CENTER PANEL (different color) ---
    w, h = 600, 300
    x = (ROOM_WIDTH - w) // 2
    y = (ROOM_HEIGHT - h) // 2

    center_panel = pygame.Surface((w, h), pygame.SRCALPHA)
    center_panel.fill((0, 0, 0, 240))
    surface.blit(center_panel, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 4)

    # --- TITLE TEXT ---
    title = title_font.render("YOU HAVE DIED", True, (255, 80, 80))
    surface.blit(title, title.get_rect(center=(x + w//2, y + 70)))

    # --- HOME BUTTON ---
    death_home_btn = pygame.Rect(x + 70, y + h - 120, 200, 70)
    pygame.draw.rect(surface, (200, 160, 40) , death_home_btn)
    pygame.draw.rect(surface, (255, 255, 255), death_home_btn, 3)

    home_text = font.render("HOME", True, (255, 255, 255))
    surface.blit(home_text, home_text.get_rect(center=death_home_btn.center))

    # --- LOAD BUTTON ---
    death_load_btn = pygame.Rect(x + w - 270, y + h - 120, 200, 70)
    pygame.draw.rect(surface, (80, 200, 110), death_load_btn)
    pygame.draw.rect(surface, (255, 255, 255), death_load_btn, 3)

    load_text = font.render("LOAD", True, (255, 255, 255))
    surface.blit(load_text, load_text.get_rect(center=death_load_btn.center))
    return death_home_btn

# DRAWING END SCREEN
def draw_end_screen(surface):
    global end_home_btn, end_return_btn

    # Background overlay
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    # Center panel
    w, h = 700, 400
    x = (ROOM_WIDTH - w) // 2
    y = (ROOM_HEIGHT - h) // 2
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((15, 15, 25, 240))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 3)

    # Title
    title = title_font.render("VICTORY!", True, (255, 220, 80))
    surface.blit(title, title.get_rect(center=(x + w//2, y + 80)))

    # Under-text
    msg = font.render("All 3 bosses have been defeated.", True, (255, 255, 255))
    surface.blit(msg, msg.get_rect(center=(x + w//2, y + 150)))

    # HOME button
    end_home_btn = pygame.Rect(x + 70, y + h - 120, 240, 70)
    pygame.draw.rect(surface, (80, 180, 250), end_home_btn)
    pygame.draw.rect(surface, (255, 255, 255), end_home_btn, 3)
    home_text = font.render("HOME", True, (255, 255, 255))
    surface.blit(home_text, home_text.get_rect(center=end_home_btn.center))

    # RETURN button
    end_return_btn = pygame.Rect(x + w - 310, y + h - 120, 240, 70)
    pygame.draw.rect(surface, (80, 200, 120), end_return_btn)
    pygame.draw.rect(surface, (255, 255, 255), end_return_btn, 3)
    return_text = font.render("RETURN", True, (255, 255, 255))
    surface.blit(return_text, return_text.get_rect(center=end_return_btn.center))

# DRAWING MINIMAP
def draw_minimap(surface, level, row, col):
    """Draw the whole minimap and icons for all visited rooms (not just the current room)."""
    if not map_visible:
        return

    map_size = 200
    cell_size = map_size // GRID_WIDTH
    map_x = ROOM_WIDTH - map_size - 20
    map_y = 60

    # background
    pygame.draw.rect(surface, (100, 100, 100), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    pygame.draw.rect(surface, (255, 255, 255), (map_x - 5, map_y - 5, map_size + 10, map_size + 10), 2)

    # draw grid cells (dark for not visited)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            x = map_x + c * cell_size
            y = map_y + (GRID_HEIGHT - 1 - r) * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            room_id = (level, r, c)
            if room_id not in visited_rooms:
                pygame.draw.rect(surface, (0, 0, 0), rect)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

    # draw icons for all visited rooms using stored memory
    for room_id in list(visited_rooms):
        lvl, rr, cc = room_id
        if lvl != level:
            continue  # only show rooms for current level
        draw_minimap_icons(surface, map_x, map_y, map_size, ROOM_WIDTH, ROOM_HEIGHT, room_id)

    # draw player icon on the current room (so player marker is always accurate)
    # compute current room origin and draw player
    _, room_r, room_c = tuple(current_room)
    cell_w = map_size // GRID_WIDTH
    cell_h = map_size // GRID_HEIGHT
    room_origin_x = map_x + room_c * cell_w
    room_origin_y = map_y + (GRID_HEIGHT - 1 - room_r) * cell_h
    sx = cell_w / ROOM_WIDTH
    sy = cell_h / ROOM_HEIGHT
    px = room_origin_x + player.x * sx
    py = room_origin_y + player.y * sy
    pygame.draw.rect(surface, (0, 255, 0), (px, py, 5, 5))

    # Level location text (keep your existing rendering)
    text = f"Level {level + 1} - {['Bottom','Middle','Top'][row]} {['Left','Middle','Right'][col]}"
    info = font.render(text, True, (255, 255, 255))
    rect = info.get_rect(topright=(ROOM_WIDTH - 20, 20))
    pygame.draw.rect(surface, (0, 0, 0), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10))
    pygame.draw.rect(surface, (255, 255, 255), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10), 2)
    surface.blit(info, rect)

# DRAW MINIMAP ICONS 
def draw_minimap_icons(surface, map_x, map_y, map_size, room_w, room_h, room_id):
    """Draw icons for a specific room_id using minimap_memory[room_id]."""
    level, room_r, room_c = room_id

    cell_w = map_size // GRID_WIDTH
    cell_h = map_size // GRID_HEIGHT
    room_origin_x = map_x + room_c * cell_w
    room_origin_y = map_y + (GRID_HEIGHT - 1 - room_r) * cell_h

    sx = cell_w / room_w
    sy = cell_h / room_h

    # pull stored data (empty lists if nothing saved)
    data = minimap_memory.get(room_id, {})
    villagers = data.get("villagers", [])
    enemies = data.get("enemies", [])
    huts = data.get("huts", [])

    # draw villagers
    for x, y in villagers:
        pygame.draw.rect(surface, (0, 0, 255), (room_origin_x + x * sx, room_origin_y + y * sy, 5, 5))
    # draw huts
    for x, y in huts:
        pygame.draw.rect(surface, (255, 255, 0), (room_origin_x + x * sx, room_origin_y + y * sy, 5, 5))
    # draw enemies
    for x, y in enemies:
        pygame.draw.rect(surface, (255, 0, 0), (room_origin_x + x * sx, room_origin_y + y * sy, 5, 5))

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

# DRAWING SAVE SCREEN
def draw_save_screen(surface):
    global save_btn_rect, slot_rects

    draw_overlay(surface)
    slot_rects = []

    title = title_font.render("SAVE GAME", True, (255, 255, 255))
    surface.blit(title, title.get_rect(center=(ROOM_WIDTH//2, 100)))

    for i in range(3):
        x = ROOM_WIDTH//2 + (i - 1) * 220
        y = ROOM_HEIGHT//2

        rect = pygame.Rect(x - 80, y - 60, 160, 120)
        slot_rects.append(rect)

        color = (200, 200, 50) if i == selected_slot else (50, 50, 50)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (255,255,255), rect, 3)

        label = f"SLOT {i+1}"
        status = "EMPTY" if slot_is_empty(i) else "OVERWRITE"

        surface.blit(font.render(label, True, (0,0,0)), (rect.x+30, rect.y+20))
        surface.blit(font.render(status, True, (0,0,0)), (rect.x+25, rect.y+60))

    save_btn_rect = pygame.Rect(ROOM_WIDTH//2 - 100, ROOM_HEIGHT - 120, 200, 60)
    pygame.draw.rect(surface, (0,150,0), save_btn_rect)
    pygame.draw.rect(surface, (255,255,255), save_btn_rect, 2)
    surface.blit(font.render("SAVE", True, (255,255,255)), save_btn_rect.move(70,15))

# DRAWING LOAD SCREEN
def draw_load_screen(surface):
    global load_btn_rect, slot_rects

    draw_overlay(surface)
    slot_rects = []

    title = title_font.render("LOAD GAME", True, (255, 255, 255))
    surface.blit(title, title.get_rect(center=(ROOM_WIDTH//2, 100)))

    for i in range(3):
        x = ROOM_WIDTH//2 + (i - 1) * 220
        y = ROOM_HEIGHT//2

        rect = pygame.Rect(x - 80, y - 60, 160, 120)
        slot_rects.append(rect)

        color = (200, 200, 50) if i == selected_slot else (50, 50, 50)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (255,255,255), rect, 3)

        label = f"SLOT {i+1}"
        status = "EMPTY" if slot_is_empty(i) else "LOAD"

        surface.blit(font.render(label, True, (0,0,0)), (rect.x+30, rect.y+20))
        surface.blit(font.render(status, True, (0,0,0)), (rect.x+40, rect.y+60))

    load_btn_rect = pygame.Rect(ROOM_WIDTH//2 - 100, ROOM_HEIGHT - 120, 200, 60)
    pygame.draw.rect(surface, (0,100,200), load_btn_rect)
    pygame.draw.rect(surface, (255,255,255), load_btn_rect, 2)
    surface.blit(font.render("LOAD", True, (255,255,255)), load_btn_rect.move(70,15))

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
    global current_room, feedback, feedback_timer
    """Handles player movement between rooms and levels based on position."""
    level, row, col = current_room

    # --- NORMAL ROOM TRANSITIONS ---
    # These run ONLY if NOT at a level-transition corner

    at_top    = player.top <= 0
    at_bottom = player.bottom >= ROOM_HEIGHT
    at_left   = player.left <= 0
    at_right  = player.right >= ROOM_WIDTH

    # top-right of top-right room
    at_level_up_corner = (level < LEVELS - 1 and row == GRID_HEIGHT - 1 and col == GRID_WIDTH - 1 and at_top and at_right)

    # bottom-left of bottom-left room
    at_level_down_corner = (level > 0 and row == 0 and col == 0 and at_bottom and at_left)

    # If NOT at a level-transition corner, allow normal room movement
    if not at_level_up_corner and not at_level_down_corner:

        # LEFT movement
        if at_left:
            if col > 0:
                current_room[2] -= 1
                player.right = ROOM_WIDTH
                visited_rooms.add(tuple(current_room))
            else:
                player.left = 0

        # RIGHT movement
        if at_right:
            if col < GRID_WIDTH - 1:
                current_room[2] += 1
                player.left = 0
                visited_rooms.add(tuple(current_room))
            else:
                player.right = ROOM_WIDTH

        # UP movement
        if at_top:
            if row < GRID_HEIGHT - 1:
                current_room[1] += 1
                player.bottom = ROOM_HEIGHT
                visited_rooms.add(tuple(current_room))
            else:
                player.top = 0

        # DOWN movement
        if at_bottom:
            if row > 0:
                current_room[1] -= 1
                player.top = 0
                visited_rooms.add(tuple(current_room))
            else:
                player.bottom = ROOM_HEIGHT

    # --- LEVEL TRANSITIONS ---

    # Next Level
    if at_level_up_corner:
        # Boss must be defeated
        if not boss_defeated[level]:
            draw_message(screen, "You must defeat the boss before advancing!", 2.0, (255, 0, 0))
            player.top = 0
            player.right = ROOM_WIDTH
            return

        # Check artifact requirements
        if level == 0 and not level_passed[0]:
            if inventory.get("Artifacts", 0) < 3:
                draw_message(screen, "You need 3 Artifacts to pass Level 1!", 2.0, (255, 0, 0))
                player.top = 0
                player.right = ROOM_WIDTH
                return
            else:
                level_passed[0] = True

        if level == 1 and not level_passed[1]:
            if inventory.get("Artifacts", 0) < 7:
                draw_message(screen, "You need 7 Artifacts to pass Level 2!", 2.0, (255, 0, 0))
                player.top = 0
                player.right = ROOM_WIDTH
                return
            else:
                level_passed[1] = True

        # All requirements met → go to next level
        current_room = [level + 1, 0, 0]
        player.x = 50
        player.y = ROOM_HEIGHT - 100
        visited_rooms.add(tuple(current_room))
        return

    # Previous Level
    if at_level_down_corner:
        current_room = [level - 1, GRID_HEIGHT - 1, GRID_WIDTH - 1]  # go to top-right of previous level
        player.x = ROOM_WIDTH - player.width - 50
        player.y = 50
        visited_rooms.add(tuple(current_room))
        return

# Helper to draw dark overlay
def draw_overlay(surface):
    """Draws a semi-transparent dark overlay over the entire surface."""
    # Create a semi-transparent fullscreen overlay
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    # Pygame.SRCALPHA = RGBA instead of just RGB
    overlay.fill((0, 0, 0, 180))  # Black with alpha 180 for semi-transparent effect
    surface.blit(overlay, (0, 0))

# Helper to draw home bg
def draw_home_background(surface):
    """Draws the home screen background with subtle texture and vignette effect."""
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

# Helper to compute shards required for boss fight
def shards_required_for_level(level_index):
    """Returns the number of Enemy Shards required to unlock the boss fight for the given level index."""
    return 30 + level_index * 60

# Resetting the game state
def reset_game():
    """Resets all game state variables to their initial values for a new game."""
    global health, max_health, inventory, player, current_room, player_dead
    global visited_rooms, minimap_memory, combat_active
    global trade_menu_active, trading_prompt_active, dialogue_active
    global lore_screen_active, instructions_active, hud_visible, map_visible, speed_potion_duration
    global boss_phase, armor_level, weapon_level
    global inventory_level, gold_pickup_level

    health = 100
    max_health = 100
    player.x, player.y = 50, ROOM_HEIGHT - 100
    current_room[:] = [0, 0, 0]
    armor_level = 0
    weapon_level = 0
    inventory_level = 0
    gold_pickup_level = 0

    inventory = {"Gold": 0, "Artifacts": 0, "Health Potions": 0, "Speed Potions": 0, "Strength Potions": 0, "Upgrade Tokens": 0, "Enemy Shards": 0}

    visited_rooms.clear()
    minimap_memory.clear()

    combat_active = False
    player_dead = False
    trade_menu_active = False
    trading_prompt_active = False
    dialogue_active = False
    lore_screen_active = False
    instructions_active = False
    hud_visible = False
    map_visible = False
    speed_potion_duration = 0
    boss_phase[current_room[0]] = 1

# Check if slot is empty
def slot_is_empty(slot_index):
    return not os.path.exists(SAVE_FILES[slot_index]) or os.path.getsize(SAVE_FILES[slot_index]) == 0

# Saving Game
def save_game(slot):
    """ Writing to the file and saveing the game"""
    # Finding the current file selected
    path = SAVE_FILES[slot]

    # Data getting saved
    data = {
        # Player
        "player_pos": [player.x, player.y],
        "current_room": current_room,
        "previous_room": previous_room,

        # Health & stats
        "health": health,
        "max_health": max_health,

        # Inventory
        "inventory": inventory,
        "inventory_limits": inventory_limits,

        # Upgrades
        "armor_level": armor_level,
        "weapon_level": weapon_level,
        "inventory_level": inventory_level,
        "gold_pickup_level": gold_pickup_level,
        "weapon_base_multiplier": weapon_base_multiplier,
        "gold_per_pickup": gold_per_pickup,

        # Effects
        "speed_potion_duration": speed_potion_duration,
        "strength_active": strength_active,

        # World state
        "visited_rooms": list(visited_rooms),
        "minimap_memory": { f"{k[0]},{k[1]}": v for k, v in minimap_memory.items() },

        # Collectibles
        "c_Artifacts": list(c_Artifacts),
        "c_Gold": list(c_Gold),
        "c_Health_Potions": list(c_Health_Potions),
        "c_Speed_Potions": list(c_Speed_Potions),
        "c_Strength_Potions": list(c_Strength_Potions),

        # Enemies & bosses
        "dead_enemies": list(dead_enemies),
        "boss_defeated": boss_defeated,
        "boss_phase": boss_phase,
        "level_passed": level_passed,
    }

    # Writing to the file to save
    with open(path, "w") as f:
        # .dump overwrites the file
        json.dump(data, f)

# Loading Game
def load_game(slot):
    """Reading the file and loading the game data"""
    global health, max_health, inventory, visited_rooms, minimap_memory
    global dead_enemies, boss_defeated, boss_phase, level_passed
    global armor_level, weapon_level, inventory_level, gold_pickup_level
    global weapon_base_multiplier, gold_per_pickup
    global speed_potion_duration, strength_active
    global previous_room, boss_dialogue_played

    # Current selected file
    path = SAVE_FILES[slot]
    if not os.path.exists(path):
        return

    # Open the file and read it
    with open(path, "r") as f:
        data = json.load(f)

    # Set the game data to the save game data
    # Player
    player.x, player.y = data["player_pos"]
    current_room[:] = data["current_room"]
    previous_room = data["previous_room"]

    # Health & stats
    health = data["health"]
    max_health = data["max_health"]

    # Inventory
    inventory.clear()
    inventory.update(data["inventory"])
    inventory_limits.clear()
    inventory_limits.update(data["inventory_limits"])

    # Upgrades
    armor_level = data["armor_level"]
    weapon_level = data["weapon_level"]
    inventory_level = data["inventory_level"]
    gold_pickup_level = data["gold_pickup_level"]
    weapon_base_multiplier = data["weapon_base_multiplier"]
    gold_per_pickup = data["gold_per_pickup"]

    # Effects
    speed_potion_duration = data["speed_potion_duration"]
    strength_active = data["strength_active"]

    # World state
    visited_rooms.clear()
    visited_rooms.update(tuple(r) for r in data["visited_rooms"])
    minimap_memory.clear()
    for k, v in data["minimap_memory"].items():
        x, y = map(int, k.split(","))
        minimap_memory[(x, y)] = v

    # Collectibles
    c_Artifacts.clear()
    c_Artifacts.update(tuple(v) for v in data["c_Artifacts"])
    c_Gold.clear()
    c_Gold.update(tuple(v) for v in data["c_Gold"])
    c_Health_Potions.clear()
    c_Health_Potions.update(tuple(v) for v in data["c_Health_Potions"])
    c_Speed_Potions.clear()
    c_Speed_Potions.update(tuple(v) for v in data["c_Speed_Potions"])
    c_Strength_Potions.clear()
    c_Strength_Potions.update(tuple(v) for v in data["c_Strength_Potions"])

    # Music state
    intro_played = True
    main_music_active = True
    pygame.mixer.music.load(MAIN_MUSIC)
    pygame.mixer.music.play(-1)

    # Enemies & bosses
    dead_enemies.clear()
    dead_enemies.update(tuple(v) for v in data["dead_enemies"])
    boss_defeated[:] = data["boss_defeated"]
    boss_phase[:] = data["boss_phase"]
    level_passed[:] = data["level_passed"]
    boss_dialogue_played = [False] * LEVELS


# Music management
def update_music():
    global was_in_lore, current_music

    # --- LORE LOCK ---
    if lore_screen_active:
        if current_music != "intro":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(INTRO_MUSIC)
            pygame.mixer.music.play(0)
            current_music = "intro"
            was_in_lore = True
        return

    # --- EXITING LORE -> GAMEPLAY ---
    if was_in_lore and not lore_screen_active:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(MAIN_MUSIC)
        pygame.mixer.music.play(-1)
        current_music = "main"
        was_in_lore = False
        return

    # --- HOME + INSTRUCTIONSdd ---
    if on_home or instructions_active:
        if current_music != "home":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(HOME_MUSIC)
            pygame.mixer.music.play(-1)
            current_music = "home"
        return

    # --- DEATH SCREEN ---
    if player_dead:
        if current_music != "death":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(DEATH_MUSIC)
            pygame.mixer.music.play(0)
            current_music = "death"
        return

    # --- VICTORY SCREEN ---
    if end_screen_active:
        if current_music != "victory":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(VICTORY_MUSIC)
            pygame.mixer.music.play(0)
            current_music = "victory"
        return

    # --- SAVE / LOAD (PAUSE) ---
    if save_screen_active or load_screen_active:
        pygame.mixer.music.pause()
        return

    # --- COMBAT ---
    if combat_active:
        if current_music != "combat":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(BATTLE_INTRO_MUSIC)
            pygame.mixer.music.play(0)
            current_music = "combat"
            # Start battle music timer
            battle_music_timer = 11.9  # seconds

        if current_music == "combat" and not pygame.mixer.music.get_busy():
            # Switch to looping battle music after intro
            pygame.mixer.music.load(BATTLE_MUSIC)
            pygame.mixer.music.play(-1)
        return

    # --- GAMEPLAY (RESUME MAIN LOOP) ---
    if current_music == "main":
        pygame.mixer.music.unpause()
        return

    # --- GAMEPLAY FALLBACK (START MAIN LOOP) ---
    pygame.mixer.music.stop()
    pygame.mixer.music.load(MAIN_MUSIC)
    pygame.mixer.music.play(-1)
    current_music = "main"

# Sound effects
def update_running_sound(is_moving):
    global is_running_sound_playing

    # Don't play running sound on non-gameplay screens
    if on_home or combat_active or player_dead or end_screen_active or lore_screen_active or instructions_active or save_screen_active or load_screen_active or dialogue_active:
        run_sound.stop()
        is_running_sound_playing = False
        return

    if is_moving:
        if not is_running_sound_playing:
            run_sound.play(-1)
            is_running_sound_playing = True
    else:
        if is_running_sound_playing:
            run_sound.stop()
            is_running_sound_playing = False

# Mute toggle
def toggle_mute():
    global is_muted
    if is_muted:
        # Mute everything
        pygame.mixer.music.set_volume(0)
        pickup_sound.set_volume(0)
        run_sound.set_volume(0)
    else:
        # Restore volumes
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pickup_sound.set_volume(SFX_VOLUME_PICKUP)
        run_sound.set_volume(SFX_VOLUME_RUN)

# MAIN LOOP
running = True
while running:
    dt = clock.tick(60)
    # ---------- EVENT HANDLING ----------
    for event in pygame.event.get():
        # --- INSTA-KILL BUTTON (K) ---
        if combat_active and event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            # Instantly kill the enemy
            enemy_health[current_enemy_index] = 0
            combat_active = False
            enemy_turn_pending = False
            strength_active = False

            # Determine room position
            try:
                lvl_idx = current_room[0]
                r_idx = current_room[1]
                c_idx = current_room[2]
            except Exception:
                lvl_idx, r_idx, c_idx = 0, 0, 0

            # Determine enemy spawn point for removal tracking
            rect = enemy_rects[current_enemy_index]
            ax, ay = enemy_spawn_points[current_enemy_index]
            dead_enemies.add((*current_room, ax, ay))

            # Award shards OR handle boss phases
            if r_idx == GRID_HEIGHT - 1 and c_idx == GRID_WIDTH - 1:  
                # --- BOSS ROOM ---
                # If boss still has another phase
                if boss_phase[lvl_idx] < boss_max_phases:
                    boss_phase[lvl_idx] += 1
                    feedback, feedback_timer = (f"The boss transforms into Phase {boss_phase[lvl_idx]}!", 3.0)
                    # Restore boss HP for new phase (use 80% of previous max)
                    new_hp = int(enemy_max_health[current_enemy_index] * 2)
                    enemy_health[current_enemy_index] = new_hp
                    enemy_max_health[current_enemy_index] = new_hp
                    # Reset combat state for new phase
                    player_turn_done = False
                    combat_active = True
                    continue  

                # -------- FINAL PHASE DEFEATED --------
                boss_defeated[lvl_idx] = True
                if not boss_dialogue_played[lvl_idx]:
                    current_dialogue = boss_dialogues[(lvl_idx, f"boss{lvl_idx + 1}")]
                    dialogue_index = 0
                    dialogue_active = True
                    boss_dialogue_played[lvl_idx] = True
                if all(boss_defeated):
                    end_screen_active = True
                dead_enemies.add((*current_room, ax, ay))
                # Remove boss from all enemy lists
                enemy_health.pop(current_enemy_index)
                enemy_max_health.pop(current_enemy_index)
                enemy_rects.pop(current_enemy_index)
                enemy_tiles.pop(current_enemy_index)
                enemy_spawn_points.pop(current_enemy_index)
                enemy_roles.pop(current_enemy_index)
                continue

            else:
                # --- NORMAL ENEMY ---
                inventory["Enemy Shards"] = inventory.get("Enemy Shards", 0) + 10
                dead_enemies.add((*current_room, ax, ay))
                # Remove enemy normally
                enemy_health.pop(current_enemy_index)
                enemy_max_health.pop(current_enemy_index)
                enemy_rects.pop(current_enemy_index)
                enemy_tiles.pop(current_enemy_index)
                enemy_spawn_points.pop(current_enemy_index)
                enemy_roles.pop(current_enemy_index)
                continue

        # --- DELETE ALL SAVES ---
        if event.type == pygame.KEYDOWN and event.key == pygame.K_0 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            for path in SAVE_FILES:
                if os.path.exists(path):
                    open(path, "w").close()  # wipe contents

        # --- QUIT EVENT ---
        if event.type == pygame.QUIT:
            running = False
            break

        # --- HOME SCREEN EVENT HANDLING ---
        if on_home and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            on_home = False
            lore_screen_active = True
            continue

        # --- GO TO HOME SCREEN FROM GAME ---
        if not on_home and event.type == pygame.KEYDOWN and event.key == pygame.K_9 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            on_home = True
            lore_screen_active = False
            instructions_active = False
            continue

        # --- GO TO LOADING SCREEN FROM GAME ---
        if not on_home and event.type == pygame.KEYDOWN and event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
            load_screen_active = True
            on_home = False
            continue

        # --- EXIT INSTRUCTIONS SCREEN ---
        if instructions_active and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            instructions_active = False
            on_home = True
            continue

        # --- LORE SCREEN EVENT HANDLING ---
        if lore_screen_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                lore_screen_active = False
                on_home = False
                player.x, player.y = 50, ROOM_HEIGHT - 100
            continue

        # --- CAMPFIRE HEALING ---
        if campfire_tiles and player.colliderect(campfire_tiles[0].inflate(60, 60)):
            healing_at_campfire = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                if health >= max_health:
                    message, message_timer, message_color = "Health already full!", 1.0, (255, 255, 0)
                healing_at_campfire = True
                if healing_at_campfire:
                    health = min(max_health, health + 0.1 * dt)
                    if health == max_health:
                        message, message_timer, message_color = "Health fully restored!", 1.0, (0, 255, 0)
                        healing_at_campfire = False
                    else:
                        message, message_timer, message_color = f"Healing... Health: {int(health)}", 0.5, (0, 255, 0)
                    continue

        # --- SAVE/LOAD SCREEN NAVIGATION ---
        if save_screen_active or load_screen_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_slot = (selected_slot - 1) % 3
                elif event.key == pygame.K_RIGHT:
                    selected_slot = (selected_slot + 1) % 3
                elif event.key == pygame.K_ESCAPE:
                    on_home = True
                    save_screen_active = False
                    load_screen_active = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Click slot
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos):
                        selected_slot = i

                # Click SAVE
                if save_screen_active and save_btn_rect and save_btn_rect.collidepoint(event.pos):
                    save_game(selected_slot)
                    save_screen_active = False

                # Click LOAD
                if load_screen_active and load_btn_rect and load_btn_rect.collidepoint(event.pos):
                    if not slot_is_empty(selected_slot):
                        load_game(selected_slot)
                        load_screen_active = False
            continue

        # ----- Mouse interactions -----
        if event.type == pygame.MOUSEBUTTONDOWN and not on_home:
            if event.button == 3:
                # Dialogue advancement
                if dialogue_active:
                    # Only advance if NOT last line
                    if dialogue_index < len(current_dialogue) - 1:
                        dialogue_index += 1
                    else:
                        # Last click ends dialogue
                        dialogue_active = False
                        dialogue_index = 0
                        # Trigger trade ONCE
                        if trade_pending_key:
                            trading_prompt_active = True
                            trade_prompt_key = trade_pending_key
                            trade_pending_key = None
                    continue

                # If right-click and dialogue active -> advance dialogue 
                if trading_prompt_active or trade_menu_active:
                    continue

                # If not currently in dialogue, right-click should attempt to start dialogue with nearby villager
                found_villager = False
                for i, vrect in enumerate(villager_tiles):
                    if vrect and player.colliderect(vrect.inflate(50, 50)):
                        # Start dialogue always
                        level, row, col = current_room
                        key = (level, row, col, i)
                        current_dialogue = list(dialogues.get(key, ["Villager: Hello there!", "Villager: Sorry, I don't have much to say."]))
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

                # --- Enemy Interaction --- 
                for idx, e_rect in enumerate(enemy_tiles):
                    if e_rect and player.colliderect(e_rect.inflate(50, 50)):
                        # Block boss fight if not enough shards
                        try:
                            lvl_idx = current_room[0]
                            r_idx = current_room[1]
                            c_idx = current_room[2]
                        except Exception:
                            lvl_idx, r_idx, c_idx = 0, 0, 0

                        if r_idx == GRID_HEIGHT - 1 and c_idx == GRID_WIDTH - 1:
                            required = shards_required_for_level(lvl_idx)
                            if inventory.get("Enemy Shards", 0) < required:
                                draw_message(screen, f"You need at least {required} Enemy Shards to challenge the boss!", 2.0, (255, 0, 0))
                                continue  # Blocks boss fight

                        # Start combat
                        combat_active = True
                        current_enemy_index = idx
                        special_attack_used = False
                        enemy_turn_pending = False
                        player_turn_done = False
                        player_defending = False
                        strength_active = False
                        break
                continue

            # Handle left click for load and save buttons when load and save menus
            if event.button == 1:
                # SAVE CONFIRM
                if save_screen_active and save_btn_rect.collidepoint(event.pos):
                    save_game(selected_slot)
                    save_screen_active = False

                # LOAD CONFIRM
                if load_screen_active and load_btn_rect.collidepoint(event.pos):
                    if not slot_is_empty(selected_slot):
                        load_game(selected_slot)
                        load_screen_active = False
                        on_home = False
                        player_dead = False
                        hud_visible = True

                # ---------- PLAYER CLICK IN TRADE MENU ----------
                if trade_menu_active:
                    # Remake the trade menu button rect exactly as in draw_trade_menu
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
                
                # ---------- PLAYER CLICK IN COMBAT ----------
                if combat_active and not enemy_turn_pending:
                    for rect, name in combat_buttons:
                        if rect.collidepoint(event.pos):
                            # Track heals used
                            global enemy_heals_used
                            if "enemy_heals_used" not in globals():
                                enemy_heals_used = 0
                            damage = 0

                            # ---------- PLAYER ACTIONS ----------
                            if name == "Attack":
                                weapon_scale = 1.0 + 0.2 * weapon_level
                                if strength_active:
                                    damage_multiplier = strength_multiplier * weapon_scale
                                else:
                                    damage_multiplier = weapon_base_multiplier * weapon_scale
                                damage = int(random.randint(10, 14) * damage_multiplier)

                                # Enemy defending logic (25% full hit, 50% half, 25% miss)
                                if enemy_defending:
                                    roll = random.random()
                                    if roll < 0.25:
                                        # 25% full hit
                                        final_damage = damage
                                    elif roll < 0.75 and roll >= 0.25:
                                        # 50% half hit
                                        final_damage = damage // 2
                                    else:
                                        # 25% miss
                                        final_damage = 0
                                    enemy_defending = False  # defense lasts only one turn
                                else:
                                    final_damage = damage
                                enemy_health[current_enemy_index] -= final_damage
                                feedback, feedback_timer = f"You attacked for {final_damage} damage!", 2.0
                                enemy_turn_pending = True
                                enemy_turn_delay = enemy_delay_frames
                                if enemy_health[current_enemy_index] <= 0:
                                    # Get room & enemy location
                                    rect = enemy_rects[current_enemy_index]
                                    ax, ay = enemy_spawn_points[current_enemy_index]

                                    # Award shards for normal enemy or mark boss defeated
                                    try:
                                        lvl_idx = current_room[0]
                                        r_idx = current_room[1]
                                        c_idx = current_room[2]
                                    except Exception:
                                        lvl_idx, r_idx, c_idx = 0, 0, 0

                                    if r_idx == GRID_HEIGHT - 1 and c_idx == GRID_WIDTH - 1:
                                        # If boss still has phases left
                                        if boss_phase[lvl_idx] < boss_max_phases:
                                            boss_phase[lvl_idx] += 1
                                            feedback, feedback_timer = f"The boss transforms into Phase {boss_phase[lvl_idx]}!", 3.0

                                            # Give new boss HP (use 80% of previous max)
                                            new_hp = int(enemy_max_health[current_enemy_index] * 2)
                                            enemy_health[current_enemy_index] = new_hp
                                            enemy_max_health[current_enemy_index] = new_hp
                                            # Reset combat state
                                            player_turn_done = False
                                            combat_active = True
                                            continue  # DO NOT fall into the enemy-removal code
                                        else:
                                            # Final phase defeated
                                            combat_active = False
                                            strength_active = False
                                            boss_defeated[lvl_idx] = True
                                            if not boss_dialogue_played[lvl_idx]:
                                                current_dialogue = boss_dialogues[(lvl_idx, f"boss{lvl_idx + 1}")]
                                                dialogue_index = 0
                                                dialogue_active = True
                                                boss_dialogue_played[lvl_idx] = True
                                            if all(boss_defeated):
                                                on_end_screen = True
                                            dead_enemies.add((*current_room, ax, ay))
                                    else:
                                        strength_active = False
                                        combat_active = False
                                        inventory["Enemy Shards"] = inventory.get("Enemy Shards", 0) + 10
                                        draw_message(screen, "Gained 10 Enemy Shards!", 2.0, (0, 255, 0))
                                        dead_enemies.add((*current_room, ax, ay))
                                    # Remove dead enemy entries from all lists so indexes stay correct
                                    enemy_health.pop(current_enemy_index)
                                    enemy_max_health.pop(current_enemy_index)
                                    enemy_rects.pop(current_enemy_index)
                                    enemy_tiles.pop(current_enemy_index)
                                    enemy_spawn_points.pop(current_enemy_index)
                                    enemy_roles.pop(current_enemy_index)

                            elif name == "Special Attack":
                                if special_attack_used:
                                    feedback, feedback_timer = "You already used Special Attack!", 2.0
                                    continue
                                weapon_scale = 1.0 + 0.2 * weapon_level
                                if strength_active:
                                    damage_multiplier = strength_multiplier * weapon_scale
                                else:
                                    damage_multiplier = weapon_base_multiplier * weapon_scale
                                damage = int(30 * damage_multiplier)

                                # Enemy defending logic (25% full hit, 50% half, 25% miss)
                                if enemy_defending:
                                    roll = random.random()
                                    if roll < 0.25:
                                        # 25% full hit
                                        final_damage = damage
                                    elif roll < 0.75 and roll >= 0.25:
                                        # 50% half hit
                                        final_damage = damage // 2
                                    else:
                                        # 25% miss
                                        final_damage = 0
                                    enemy_defending = False  # defense lasts only one turn
                                else:
                                    final_damage = damage

                                enemy_health[current_enemy_index] -= final_damage
                                special_attack_used = True
                                feedback, feedback_timer = f"You used SPECIAL ATTACK for {final_damage} damage!", 2.0
                                enemy_turn_pending = True
                                enemy_turn_delay = enemy_delay_frames
                                if enemy_health[current_enemy_index] <= 0:
                                    # Get room & enemy location
                                    rect = enemy_rects[current_enemy_index]
                                    ax, ay = enemy_spawn_points[current_enemy_index]

                                    # Award shards for normal enemy or mark boss defeated
                                    try:
                                        lvl_idx = current_room[0]
                                        r_idx = current_room[1]
                                        c_idx = current_room[2]
                                    except Exception:
                                        lvl_idx, r_idx, c_idx = 0, 0, 0

                                    if r_idx == GRID_HEIGHT - 1 and c_idx == GRID_WIDTH - 1:
                                        # If boss still has phases left
                                        if boss_phase[lvl_idx] < boss_max_phases:
                                            boss_phase[lvl_idx] += 1
                                            feedback, feedback_timer = f"The boss transforms into Phase {boss_phase[lvl_idx]}!", 3.0

                                            # Give new boss HP (use 80% of previous max)
                                            new_hp = int(enemy_max_health[current_enemy_index] * 2)
                                            enemy_health[current_enemy_index] = new_hp
                                            enemy_max_health[current_enemy_index] = new_hp

                                            # Reset combat state
                                            player_turn_done = False
                                            combat_active = True
                                            continue  # DO NOT fall into the enemy-removal code
                                        else:
                                            # Final phase defeated
                                            strength_active = False
                                            combat_active = False
                                            boss_defeated[lvl_idx] = True
                                            if not boss_dialogue_played[lvl_idx]:
                                                current_dialogue = boss_dialogues[(lvl_idx, f"boss{lvl_idx + 1}")]
                                                dialogue_index = 0
                                                dialogue_active = True
                                                boss_dialogue_played[lvl_idx] = True
                                            if all(boss_defeated):
                                                on_end_screen = True
                                            dead_enemies.add((*current_room, ax, ay))
                                    else:
                                        strength_active = False
                                        combat_active = False
                                        inventory["Enemy Shards"] = inventory.get("Enemy Shards", 0) + 10
                                        draw_message(screen, "Gained 10 Enemy Shards!", 2.0, (0, 255, 0))
                                        # Mark enemy as dead
                                        dead_enemies.add((*current_room, ax, ay))
                                        strength_active = False
                                    # Remove dead enemy entries from all lists so indexes stay correct
                                    enemy_health.pop(current_enemy_index)
                                    enemy_max_health.pop(current_enemy_index)
                                    enemy_rects.pop(current_enemy_index)
                                    enemy_tiles.pop(current_enemy_index)
                                    enemy_spawn_points.pop(current_enemy_index)
                                    enemy_roles.pop(current_enemy_index)

                            elif name == "Defend":
                                player_defending = True
                                feedback, feedback_timer = "You brace yourself!", 2.0
                                enemy_turn_pending = True
                                enemy_turn_delay = enemy_delay_frames

                            elif name == "Strength Potion":
                                if strength_active:
                                    feedback, feedback_timer = "You are already strong!", 2.0
                                    continue
                                if inventory["Strength Potions"] > 0:
                                    inventory["Strength Potions"] -= 1
                                    strength_active = True
                                    feedback, feedback_timer = "You used a Strength Potion!", 2.0
                                    enemy_turn_pending = True
                                    enemy_turn_delay = enemy_delay_frames
                                else:
                                    feedback, feedback_timer = "No Strength Potions!", 2.0
                                    continue

                            elif name == "Health Potion":
                                if inventory["Health Potions"] > 0:
                                    heal_amount = 25
                                    health = min(max_health, health + heal_amount)
                                    inventory["Health Potions"] -= 1
                                    feedback, feedback_timer = f"You healed for {heal_amount} HP!", 2.0
                                    enemy_turn_pending = True
                                    enemy_turn_delay = enemy_delay_frames
                                else:
                                    feedback, feedback_timer = "No Health Potions!", 2.0
                                    continue

                            elif name == "Run":
                                # 50/50 escape chance
                                if random.random() < 0.5:
                                    combat_active = False
                                    strength_active = False
                                else:
                                    feedback, feedback_timer = "Failed to escape!", 2.0
                                    enemy_turn_pending = True
                                    enemy_turn_delay = enemy_delay_frames
                                continue

                            # ----- BEGIN ENEMY TURN DELAY -----
                            player_turn_done = True
                            enemy_turn_pending = True
                            enemy_turn_delay = enemy_delay_frames
                            break

                # Handles the upgrade button in the upgrade menu
                if upgrade_menu_active:
                    # Remake the upgrade menu button rect exactly as in draw_upgrade_menu
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
            # --- MUTE TOGGLE ---
            if event.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_LALT == 0:
                is_muted = not is_muted
                toggle_mute()

            # --- SAVE GAME ---
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if not combat_active and not player_dead and not on_home:
                    save_screen_active = True
                    load_screen_active = False

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

    # ----- MAIN GAME LOOP -----
    update_music()
    update_running_sound(is_moving)

    # ---------- HOME SCREEN ----------
    if on_home:
        draw_home_background(screen)

        # --- Title ---
        title_text = "Crownfall"

        # Fonts
        home_title_font = pygame.font.Font("crownfall_fonts/MedievalSharp-Regular.ttf", 135)

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
            glow_font = pygame.font.Font("crownfall_fonts/MedievalSharp-Regular.ttf", 120 + expand)
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

        halo_radius = 180
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
        menu_font = pygame.font.Font("crownfall_fonts/MedievalSharp-Regular.ttf", 55)

        option_color = (180, 210, 255)
        option_shadow = (70, 90, 130)

        options = ["PLAY", "CONTROLS", "LOAD GAME", "QUIT"]
        option_rects = []
        start_y = ROOM_HEIGHT // 2 - 80

        for i, opt in enumerate(options):
            shadow = menu_font.render(opt, True, option_shadow)
            shadow_rect = shadow.get_rect(center=(ROOM_WIDTH // 2 + 2, start_y + i * 70 - 20))
            screen.blit(shadow, shadow_rect)

            surf = menu_font.render(opt, True, option_color)
            rect = surf.get_rect(center=(ROOM_WIDTH // 2, start_y + i * 70 - 25))
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
                lore_screen_active = True

            # How to Play
            elif option_rects[1].collidepoint(pos):
                on_home = False
                instructions_active = True

            # Load
            elif option_rects[2].collidepoint(pos):
                on_home = False
                load_screen_active = True
                save_screen_active = False

            # Quit
            elif option_rects[3].collidepoint(pos):
                running = False
        pygame.display.flip()
        continue

    if instructions_active:
        draw_instructions(screen)
        pygame.display.flip()
        continue

    if lore_screen_active:
        screen.fill((0,0,0))
        draw_lore_screen(screen)
        pygame.display.flip()
        continue

    if combat_active:
        # Enemy delayed turn logic still runs:
        if enemy_turn_pending:
            if enemy_turn_delay > 0:
                enemy_turn_delay -= 1
            else:
                run_enemy_turn()
                enemy_turn_delay = False
        combat_buttons = draw_combat_screen(screen)
        pygame.display.flip()
        continue  # <-- THIS MUST BE HERE to stop overworld from drawing

    # Death screen click handling
    if player_dead and event.type == pygame.MOUSEBUTTONDOWN:
        if death_home_btn.collidepoint(event.pos):
            reset_game()
            on_home = True
            player_dead = False
            continue

        if death_load_btn.collidepoint(event.pos):
            load_screen_active = True
            on_home = False
            player_dead = False
            continue

    if player_dead:
        draw_death_screen(screen)
        pygame.display.flip()
        continue

    if end_screen_active:
        draw_end_screen(screen)
        pygame.display.flip()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Go to Home Screen
            if end_home_btn.collidepoint(event.pos):
                reset_game()
                on_home = True
                end_screen_active = False
                continue

            # Return to game
            if end_return_btn.collidepoint(event.pos):
                end_screen_active = False
                continue
        continue

    if save_screen_active:
        draw_save_screen(screen)
        pygame.display.flip()
        continue

    if load_screen_active:
        draw_load_screen(screen)
        pygame.display.flip()
        continue

    # ---------- GAMEPLAY ----------
    keys = pygame.key.get_pressed()
    moving = False
    dx = dy = 0

    if dialogue_active or combat_active or player_dead or trading_prompt_active:
        dx = dy = 0
    else:
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -base_speed
            facing = "left"
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = base_speed
            facing = "right"
            moving = True
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -base_speed
            facing = "up"
            moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = base_speed
            facing = "down"
            moving = True

    # ----- Water Movement Check -----
    in_water = any(player.colliderect(wrect) for wrect in water_tiles)
    if in_water:
        ANIM_SPEED = 12
        dx *= 0.5
        dy *= 0.5
    # ----- Speed Potion Effect -----
    current_speed = base_speed
    if speed_potion_duration > 0:
        ANIM_SPEED = 4
        current_speed *= speed_multiplier

    player.x += dx * (current_speed / base_speed)
    player.y += dy * (current_speed / base_speed)

    is_moving = keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] \
            or keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_RIGHT]

    update_running_sound(is_moving)
    if moving:
        anim_timer += 1
        if anim_timer >= ANIM_SPEED:
            anim_timer = 0
            anim_index = (anim_index + 1) % 6
        last_facing = facing
    else:
        # Idle frame rules you requested
        if last_facing == "down":
            anim_index = 5   # Down_6
        elif last_facing == "left":
            anim_index = 5   # Left_6
        elif last_facing == "right":
            anim_index = 2   # Right_3
        elif last_facing == "up":
            anim_index = 2   # Up_3

    # Draw Room + Update Globals
    draw_room(screen, *current_room, c_Artifacts, c_Gold, c_Health_Potions)
    room_colliders[tuple(current_room)] = colliders

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
                    pickup_sound.play()
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
    current_player_img = player_images[last_facing][anim_index]
    screen.blit(current_player_img, player.topleft)

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
        if not vrect or not player.colliderect(vrect.inflate(100, 100)):
            # If player moves away while dialogue pending trade, clear pending trade
            dialogue_active, current_dialogue, dialogue_index, active_villager_index = False, [], 0, None

    # If trading prompt is active, close it if player moves away from villager
    if trading_prompt_active and trade_prompt_key is not None:
        # Find the villager rectangle by index; if not near, close prompt
        level, row, col, idx = trade_prompt_key
        if idx < 0 or idx >= len(villager_tiles):
            trading_prompt_active = False
            trade_prompt_key = None
        else:
            vrect = villager_tiles[idx]
            if not player.colliderect(vrect.inflate(100, 100)):
                trading_prompt_active = False
                trade_prompt_key = None

    weapon_scale = 1.0 + 0.2 * weapon_level
    # Strength potion stays active entire fight using your flag
    if strength_active:  
        damage_multiplier = strength_multiplier * weapon_scale
    else:
        damage_multiplier = weapon_base_multiplier * weapon_scale

    # ----- Timers -----
    # Potion effect timer update
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
    
    if battle_music_timer > 0:
        battle_music_timer = max(0, battle_music_timer - dt / 1000.0)
        if battle_music_timer == 0:
            # Switch to combat loop music
            pygame.mixer.music.stop()
            pygame.mixer.music.load(BATTLE_MUSIC)
            pygame.mixer.music.play(-1)
            current_music = "combat_loop"
    pygame.display.flip()
pygame.quit()
