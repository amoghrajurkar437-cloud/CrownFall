import pygame
import os

pygame.init()
os.chdir(os.path.dirname(__file__))  # make working dir = script folder

# CONSTANTS
ROOM_WIDTH = 800
ROOM_HEIGHT = 600
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
EDGE_BUFFER = 5

#Basic set up
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 80)  # big font for home screen title

# Player and Room setup
player = pygame.Rect(50, ROOM_HEIGHT - 100, 50, 50)
facing = "up" # Track direction player is facing
player_color = (255, 255, 0)
player_speed = 10
base_speed = 10
speed_potion_duration = 0  # seconds remaining on active potion
speed_multiplier = 2
current_room = [0, 0, 0]
room_colliders = {}

# Health set up
health = 80
max_health = 100

# Inventory set up
inventory = {"Gold": 0, "Artifacts": 0, "Health Potions": 0, "Speed Potions": 0}
inventory_limits = {"Gold": 150, "Artifacts": 7, "Health Potions": 3, "Speed Potions": 3}

# Collected sets
c_Artifacts = set()
c_Gold = set()
c_Health_Potions = set()
c_Speed_Potions = set ()

# Map and HUD setup
HUD_visible = False
Map_visible = False

# On-screen notifications
message = ""
message_color = (255, 255, 255)
message_timer = 0

# Home screen flag
on_home = True  # start on the home page

# Globals used by draw_objects (will be set per-room in draw_room)
colliders = []
artifacts = []
gold = []
health_potions = []
speed_potions = []

# DRAWING ELEMENTS
def draw_objects(x, y, obj_type, surface):
    """Draws an object on the game surface and adds its collider or collectible
    reference to the appropriate list based on object type."""
    global colliders, artifacts, gold, health_potions, speed_potions

    def load_img(name, w, h, offset=(0, 0)):
        """Loads, scales, trims transparent padding, draws the image and returns the rect."""
        img = pygame.image.load(f"crownfall_images/{name}.png").convert_alpha()

        # Scale up (if needed)
        w2, h2 = scale(name, w, h)
        w2, h2 = int(w2), int(h2)
        img = pygame.transform.scale(img, (w2, h2))

        # Draw to surface at anchor (x - offset[0], y - offset[1])
        draw_x = x - offset[0]
        draw_y = y - offset[1]
        surface.blit(img, (draw_x, draw_y))

        # trim transparent padding so collider matches visible pixels only
        trim_rect = img.get_bounding_rect()
        rect = pygame.Rect(draw_x + trim_rect.x,
                           draw_y + trim_rect.y,
                           trim_rect.width,
                           trim_rect.height)
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

    # Environment
    # Calls w and h close enough to their size to prevent lag
    if obj_type == "tree1":
        rect = load_img("Tree_1",200, 250)
        colliders.append(rect)
    elif obj_type == "tree2":
        rect = load_img("Tree_2", 150, 200)
        colliders.append(rect)
    elif obj_type == "rock1":
        rect = load_img("Rock_1", 100, 100)
        colliders.append(rect)
    elif obj_type == "rock2":
        rect = load_img("Rock_2", 50, 75)
        colliders.append(rect)
    elif obj_type == "house1":
        rect = load_img("House_1", 300, 300)
        colliders.append(rect)
    elif obj_type == "house2":
        rect = load_img("House_2", 500, 250)
        colliders.append(rect)
    elif obj_type == "villager":
        rect = load_img("Villager", 100, 200)
        colliders.append(rect)
    elif obj_type == "wall1":
        rect = load_img("Wall_1", 200, 150)
        colliders.append(rect)
    elif obj_type == "wall2":
        rect = load_img("Wall_2", 150, 200)
        colliders.append(rect)
    elif obj_type == "water":
        rect = load_img("Water", 400, 400)

    # Collectibles (append tuples: (rect, anchor_x, anchor_y))
    elif obj_type == "artifact":
        rect = load_img("Artifact", 40, 40)
        artifacts.append((rect, x, y))
    elif obj_type == "gold":
        rect = load_img("Gold", 50, 50)
        gold.append((rect, x, y))
    elif obj_type == "health_potion":
        rect = load_img("H_Potion", 40, 40)
        health_potions.append((rect, x, y))
    elif obj_type == "speed_potion":
        rect = load_img("S_Potion", 40, 40)
        speed_potions.append((rect, x, y))

# DRAWING ROOMS
def draw_room(surface, level, row, col, c_Artifacts, c_Gold, c_Health_Potions):
    """Draws the current room based on the level, row, and column.
    Adds interactive and environmental objects to their respective lists."""

    global colliders, artifacts, gold, health_potions, speed_potions

    # Draw background
    bg = pygame.image.load("crownfall_images/Level_bg_1.jpg").convert()
    bg = pygame.transform.scale(bg, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(bg, (0, 0))

    # Object containers for this room
    colliders, artifacts, gold, health_potions, speed_potions = [], [], [], [], []

    def _can_draw(anchor_x, anchor_y, list):
        """checks if a collectable should be drawn on the screen"""
        return (level, row, col, anchor_x, anchor_y) not in list

    # ──────────────── LEVEL 1 ────────────────
    if level == 0 and row == 0 and col == 0:
        # Level 1 - Bottom-left room
        draw_objects(400, 250, "house1", surface) # House 1
        draw_objects(245, 320, "tree1", surface) # Tree 1
        draw_objects(25, 50, "rock1", surface) # Rock 1
        draw_objects(175, 25, "rock2", surface) # Rock 2
        if _can_draw(600, 150, c_Artifacts):
            draw_objects(600, 150, "artifact", surface) # Artifact
    elif level == 0 and row == 0 and col == 1:
        # Level 1 - Bottom-middle room
        draw_objects(570, 320, "tree2", surface) # Tree 2
        draw_objects(350, 250, "rock2", surface) # Rock 2
        draw_objects(450, 100, "villager", surface) # Villager
        if _can_draw(400, 500, c_Gold):
            draw_objects(400, 500, "gold", surface) # Gold
        if _can_draw(150, 25, c_Speed_Potions):
            draw_objects(150, 25, "speed_potion", surface) #Speed Potion
    elif level == 0 and row == 0 and col == 2:
        # Level 1 - Bottom-right room
        draw_objects(350, 150, "house2", surface) # House 2
        draw_objects(120, 220, "tree1", surface) # Tree 1
        draw_objects(450, 500, "rock1", surface) # Rock 1
        draw_objects(600, 400, "villager", surface) # Villager
        if _can_draw(700, 100, c_Artifacts):
            draw_objects(700, 100, "artifact", surface) # Artifact
    elif level == 0 and row == 1 and col == 0:
        # Level 1 - Middle-left room
        draw_objects(245, 270, "tree1", surface) # Tree 1
        draw_objects(600, 350, "rock1", surface) # Rock 1
        draw_objects(25, 25, "villager", surface) # Villager
        if _can_draw(400, 150, c_Health_Potions):
            draw_objects(400, 150, "health_potion", surface) # Health Potion
        if _can_draw(700, 500, c_Gold):
            draw_objects(700, 500, "gold", surface) # Gold
    elif level == 0 and row == 1 and col == 1:
        # Level 1 - Center room
        draw_objects(400, 250, "house1", surface) # House 1
        draw_objects(150, 180, "tree1", surface) # Tree 1
        if _can_draw(600, 150, c_Gold):
            draw_objects(600, 150, "gold", surface) # Gold
        if _can_draw(700, 400, c_Artifacts):
            draw_objects(700, 400, "artifact", surface) # Artifact
        #weapon and enemy
    elif level == 0 and row == 1 and col == 2:
        # Level 1 - Middle-right room
        draw_objects(100, 200, "rock2", surface) # Rock 2
        if _can_draw(500, 250, c_Speed_Potions):
            draw_objects(500, 250, "speed_potion", surface) #Speed Potion
        #enemy and water
    elif level == 0 and row == 2 and col == 0:
        # Level 1 - Top-left room
        draw_objects(220, 245, "tree1", surface) # Tree 1
        draw_objects(400, 400, "rock1", surface) # Rock 1
        if _can_draw(200, 150, c_Gold):
            draw_objects(200, 150, "gold", surface) # Gold
    elif level == 0 and row == 2 and col == 1:
        # Level 1 - Top-middle room
        draw_objects(620, 170, "tree2", surface) # Tree 2
        draw_objects(200, 25, "house1", surface) # House 1
        if _can_draw(100, 200, c_Health_Potions):
            draw_objects(100, 200, "health_potion", surface) # Health Potion
        if _can_draw(50, 100, c_Gold):
            draw_objects(50, 100, "gold", surface) # Gold
        #enemy
    elif level == 0 and row == 2 and col == 2:
        # Level 1 - Top-right room
        if _can_draw(200, 150, c_Gold):
            draw_objects(200, 150, "gold", surface) # Gold
        #final boss
    else:
        pass

    # ──────────────── LEVEL 2 ────────────────
    if level == 1 and row == 0 and col == 0:
        # Level 2 - Bottom-left room
        draw_objects(620, 420, "tree2", surface) # Tree 2
        if _can_draw(100, 100, c_Gold):
            draw_objects(100, 100, "gold", surface) # Gold
        if _can_draw(500, 350, c_Health_Potions):
            draw_objects(500, 350, "health_potion", surface) # Health Potion
    elif level == 1 and row == 0 and col == 1:
        # Level 2 - Bottom-middle room
        draw_objects(400, 300, "rock2", surface) # Rock 2
        draw_objects(200, 170, "tree1", surface) # Tree 1
        #upgrade hut
    elif level == 1 and row == 0 and col == 2:
        # Level 2 - Bottom-right room
        draw_objects(-200, 200, "wall1", surface) # Wall 1
        draw_objects(0, 200, "wall1", surface) # Wall 1
        draw_objects(200, 200, "wall1", surface) # Wall 1
        draw_objects(600, 200, "wall1", surface) # Wall 1
        draw_objects(-130, 400, "wall2", surface) # Wall 2
        draw_objects(-130, 350, "wall2", surface) # Wall 2
        draw_objects(200, 400, "villager", surface) #Villager
        draw_objects(400, 350, "villager", surface) #Villager
        draw_objects(650, 400, "villager", surface) #Villager
    elif level == 1 and row == 1 and col == 0:
        # Level 2 - Middle-left room
        draw_objects(300, 250, "rock1", surface) # Rock 1
        draw_objects(520, 420, "tree2", surface) # Tree 2
        draw_objects(715, 0, "wall1", surface) # Wall 1
        draw_objects(600, -100, "wall2", surface) # Wall 2
        if _can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion
        if _can_draw(150, 300, c_Speed_Potions):
            draw_objects(150, 300, "speed_potion", surface) #Speed Potion
    elif level == 1 and row == 1 and col == 1:
        # Level 2 - Center room
        draw_objects(-100, 0, "wall1", surface) # Wall 1
        draw_objects(0, 0, "wall1", surface) # Wall 1
        draw_objects(200, 0, "wall1", surface) # Wall 1
        draw_objects(600, 0, "wall1", surface) # Wall 1
        if _can_draw(400, 400, c_Health_Potions):
            draw_objects(400, 400, "health_potion", surface) # Health Potion
        if _can_draw(700, 200, c_Gold):
            draw_objects(700, 200, "gold", surface) # Gold
    elif level == 1 and row == 1 and col == 2:
        # Level 2 - Middle-right room
        draw_objects(-100, 0, "wall1", surface) # Wall 1
        draw_objects(0, 0, "wall1", surface) # Wall 1
        draw_objects(200, 0, "wall1", surface) # Wall 1
        draw_objects(400, 0, "wall1", surface) # Wall 1
        draw_objects(600, 0, "wall1", surface) # Wall 1
        draw_objects(100, 350, "tree1", surface) # Tree 1
        if _can_draw(500, 300, c_Artifacts):
            draw_objects(500, 300, "artifact", surface)  # Artifact
    elif level == 1 and row == 2 and col == 0:
        # Level 2 - Top-left room
        draw_objects(600, -200, "wall2", surface) # Wall 2
        draw_objects(600, 0, "wall2", surface) # Wall 2
        draw_objects(600, 200, "wall2", surface) # Wall 2
        draw_objects(600, 400, "wall2", surface) # Wall 2
        draw_objects(400, 300, "rock1", surface) # Rock 1
        draw_objects(220, 220, "tree2", surface) # Tree 2
        if _can_draw(450, 100, c_Artifacts):
            draw_objects(450, 100, "artifact", surface)  # Artifact
    elif level == 1 and row == 2 and col == 1:
        # Level 2 - Top-middle room
        if _can_draw(300, 250, c_Health_Potions):
            draw_objects(300, 250, "health_potion", surface) # Potion
        if _can_draw(500, 350, c_Artifacts):
            draw_objects(500, 350, "artifact", surface) # Artifact
        if _can_draw(700, 150, c_Gold):
            draw_objects(700, 150, "gold", surface) # Gold
        if _can_draw(100, 450, c_Gold):
            draw_objects(100, 450, "gold", surface) # Gold
    elif level == 1 and row == 2 and col == 2:
        # Level 2 - Top-right room
        if _can_draw(400, 300, c_Gold):
            draw_objects(400, 300, "gold", surface) # Gold
        if _can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion
    else:
        pass

    # ──────────────── LEVEL 3 ────────────────
    if level == 2 and row == 0 and col == 0:
        # Level 3 - Bottom-left room
        draw_objects(400, 300, "tree1", surface)  # Tree 1
        #water
    elif level == 2 and row == 0 and col == 1:
        # Level 3 - Bottom-middle room
        draw_objects(100, 300, "villager", surface) # Villager 1
        draw_objects(500, 300, "villager", surface) # Villager 2
        draw_objects(620, 160, "tree1", surface)    # Tree 1
    elif level == 2 and row == 0 and col == 2:
        # Level 3 - Bottom-right room
        draw_objects(20, 170, "tree1", surface) # Tree 1
        if _can_draw(700, 25, c_Gold):
            draw_objects(700, 25, "gold", surface)  # Gold
        if _can_draw(700, 500, c_Health_Potions):
            draw_objects(700, 500, "health_potion", surface)  # Health Potion
        if _can_draw(500, 250, c_Speed_Potions):
            draw_objects(500, 250, "speed_potion", surface) #Speed Potion
        #water
    elif level == 2 and row == 1 and col == 0:
        # Level 3 - Middle-left room
        draw_objects(400, 300, "rock2", surface) # Rock 2
        draw_objects(170, 170, "tree2", surface) # Tree 2
        if _can_draw(350, 200, c_Health_Potions):
            draw_objects(350, 200, "health_potion", surface) # Health Potion
    elif level == 2 and row == 1 and col == 1:
        # Level 3 - Center room
        draw_objects(300, 100, "house2", surface) # House 2
        if _can_draw(700, 25, c_Gold):
            draw_objects(700, 25, "gold", surface) # Gold
    elif level == 2 and row == 1 and col == 2:
        # Level 3 - Middle-right room
        draw_objects(220, 320, "tree2", surface) # Tree 2
        if _can_draw(50, 100, c_Health_Potions):
            draw_objects(50, 100, "health_potion", surface) # Health Potion
        if _can_draw(500, 200, c_Gold):
            draw_objects(500, 200, "gold", surface) # Gold
        if _can_draw(400, 450, c_Speed_Potions):
            draw_objects(400, 450, "speed_potion", surface) #Speed Potion
    elif level == 2 and row == 2 and col == 0:
        # Level 3 - Top-left room
        draw_objects(270, 120, "tree1", surface) # Tree 1
        #ruin
    elif level == 2 and row == 2 and col == 1:
        # Level 3 - Top-middle room
        draw_objects(20, 170, "tree1", surface) # Tree 1
        draw_objects(420, 270, "tree2", surface) # Tree 2
        if _can_draw(500, 25, c_Gold):
            draw_objects(500, 25, "gold", surface) # Gold
        if _can_draw(400, 600, c_Gold):
            draw_objects(400, 600, "gold", surface) # Gold
    elif level == 2 and row == 2 and col == 2:
        # Level 3 - Top-right room
        if _can_draw(600, 250, c_Gold):
            draw_objects(600, 250, "gold", surface) # Gold
    else:
        pass

    return colliders, artifacts, gold, health_potions

# DRAWING HUD
def draw_hud(surface, level, row, col):
    """Draws the player HUD (health + inventory) when visible."""
    if not HUD_visible:
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
    inv_height = padding_top + num_items * line_height + padding_bottom

    inv_rect = pygame.Rect(20, 90, 250, inv_height)
    pygame.draw.rect(surface, (0, 0, 0), inv_rect)
    pygame.draw.rect(surface, (255, 255, 255), inv_rect, 2)

    y = inv_rect.top + 15
    for item, count in inventory.items():
        txt = font.render(f"{item}: {count}", True, (255, 255, 255))
        surface.blit(txt, (40, y))
        y += line_height
    
    # Active effects display
    if speed_potion_duration > 0:
        effect_text = font.render(f"{speed_multiplier}x speed for: ({int(speed_potion_duration)}s)", True, (0, 255, 255))
        surface.blit(effect_text, (inv_rect.left, inv_rect.bottom + 10))



# DRAWING MINIMAP
def draw_minimap(surface, level, row, col):
    """Draws a simple minimap for the current level under the level text."""
    if not Map_visible:
        return  # Don't draw anything if HUD is hidden

    map_size = 90  # total width/height of the map
    cell_size = map_size // GRID_WIDTH
    padding = 10

    # top-right corner under the level info
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

    #Level location 
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

# COLLISION
def colllision_check(dx, dy, colliders):
    """Moves the player while preventing overlap with collidable objects."""
    player.x += dx
    for c in colliders:
        if player.colliderect(c):
            if dx > 0:
                player.right = c.left
            elif dx < 0:
                player.left = c.right

    player.y += dy
    for c in colliders:
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
            current_room = [level - 1, GRID_HEIGHT - 1, GRID_WIDTH - 1]  # go to top-right of previous level
            player.x, player.y = ROOM_WIDTH - 150, 50
        else:
            player.bottom = ROOM_HEIGHT

# MAIN LOOP
running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    # ─────────────── EVENTS ───────────────
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        # Start game from home screen
        elif on_home and e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            on_home = False
            player.x, player.y = 50, ROOM_HEIGHT - 100

        # Toggle HUD visibility
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_e and not on_home:
            HUD_visible = not HUD_visible

        # Toggle map visibility
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_m and not on_home:
            Map_visible = not Map_visible

        # Speed Potion
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_1 and not on_home:
            if inventory.get("Speed Potions", 0) > 0:
                inventory["Speed Potions"] -= 1
                speed_potion_duration += 30  # +60 seconds per potion
                message =  f"Speed potion used! Duration: {round(speed_potion_duration)} seconds"
                message_color = (173, 216, 230)
                message_timer = 120
            else:
                message = "No Speed Potions left!"
                message_color = (173, 216, 230)
                message_timer = 60

        # Healing
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_2 and not on_home:
            if inventory["Health Potions"] > 0 and health < max_health:
                old_health = health
                heal_amount = 20
                health = min(health + heal_amount, max_health)
                actual_healed = health - old_health
                inventory["Health Potions"] -= 1
                message = f"+{actual_healed} Health"
                message_color = (0, 255, 0)
                message_timer = 60
            elif health >= max_health:
                message = "Your health is already full!"
                message_color = (0, 255, 0)
                message_timer = 60
            elif inventory["Health Potions"] <= 0:
                message = "You have no health potions!"
                message_color = (255, 0, 0)
                message_timer = 60

    # ─────────────── HOME SCREEN ───────────────
    if on_home:
        screen.fill((173, 216, 230))  # light blue background

        # Title
        title_surf = title_font.render("Crownfall", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(ROOM_WIDTH // 2, 80))
        box_rect = pygame.Rect(title_rect.left - 30, title_rect.top - 15,
                               title_rect.width + 60, title_rect.height + 30)
        pygame.draw.rect(screen, (255, 255, 255), box_rect)
        pygame.draw.rect(screen, (0, 0, 0), box_rect, 5)
        screen.blit(title_surf, title_rect)

        # Press space to start
        prompt_surf = font.render("Press SPACE to play", True, (0, 0, 0))
        prompt_rect = prompt_surf.get_rect(center=(ROOM_WIDTH // 2, ROOM_HEIGHT // 2 + 120))
        screen.blit(prompt_surf, prompt_rect)

        # Player display
        home_player = player.copy()
        home_player.inflate_ip(175, 175)
        home_player.center = (ROOM_WIDTH // 2, ROOM_HEIGHT // 2 - 50)
        pygame.draw.rect(screen, (0, 0, 0), home_player)

        pygame.display.flip()

    else:
        # ─────────────── GAMEPLAY LOGIC ───────────────
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= player_speed
            facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += player_speed
            facing = "right"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= player_speed
            facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += player_speed
            facing = "down"

        # tuple(current_room) converts [level, row, col] into an immutable (level, row, col)
        # so it can be used as a dictionary key in room_colliders
        colllision_check(dx, dy, room_colliders.get(tuple(current_room), []))
        room_transition()

        # ─────────────── DRAWING ───────────────
        colliders, artifacts, gold, health_potions = draw_room(
            screen, current_room[0], current_room[1], current_room[2],
            c_Artifacts, c_Gold, c_Health_Potions
        )

        # Store the current room's colliders — tuple(current_room) makes it hashable as a dict key
        room_colliders[tuple(current_room)] = colliders

        # ─────────────── PICKUP LOGIC ───────────────
        for rect, x, y in gold:
            if player.colliderect(rect):
                if inventory["Gold"] < inventory_limits["Gold"]:
                    inventory["Gold"] += 15
                    c_Gold.add((current_room[0], current_room[1], current_room[2], x, y))
                    message = "+15 gold"
                    message_color = (255, 215, 0)
                    message_timer = 30
                else:
                    message = "Inventory full of Gold"
                    message_timer = 60
                    message_color = (255, 0, 0)

        for rect, x, y in health_potions:
            if player.colliderect(rect):
                if inventory["Health Potions"] < inventory_limits["Health Potions"]:
                    inventory["Health Potions"] += 1
                    c_Health_Potions.add((current_room[0], current_room[1], current_room[2], x, y))
                    message = "+1 health potion"
                    message_color = (255, 182, 193)
                    message_timer = 30
                else:
                    message = "Inventory full of Health Potions"
                    message_timer = 60
                    message_color = (255, 0, 0)

        for rect, x, y in speed_potions:
            if player.colliderect(rect):
                if inventory["Speed Potions"] < inventory_limits["Speed Potions"]:
                    inventory["Speed Potions"] += 1
                    c_Speed_Potions.add((current_room[0], current_room[1], current_room[2], x, y))
                    message = "+1 speed potion"
                    message_color = (173, 216, 230)
                    message_timer = 30
                else:
                    message = "Inventory full of Speed Potions"
                    message_timer = 60
                    message_color = (255, 0, 0)

        for rect, x, y in artifacts:
            if player.colliderect(rect):
                if inventory["Artifacts"] < inventory_limits["Artifacts"]:
                    inventory["Artifacts"] += 1
                    c_Artifacts.add((current_room[0], current_room[1], current_room[2], x, y))
                    message = "+1 artifact"
                    message_color = (160, 32, 240)
                    message_timer = 30   
                else:
                    message = "Inventory full of Artifacts"
                    message_timer = 60
                    message_color = (255, 0, 0)

        # ─────────────── DRAW PLAYER + HUD ───────────────
        # Change player color based on facing direction
        if facing == "up":
            player_color = (255, 255, 0)
        elif facing == "down":
            player_color = (0, 255, 0)
        elif facing == "left":
            player_color = (255, 0, 0)
        elif facing == "right":
            player_color = (0, 0, 255)

        # Draw player with current color
        pygame.draw.rect(screen, player_color, player)
        draw_hud(screen, current_room[0], current_room[1], current_room[2])
        draw_minimap(screen, current_room[0], current_room[1], current_room[2])
        draw_message(screen, message, message_timer, message_color)

        # SPEED POTION TIMER
        if speed_potion_duration > 0:
            player_speed = base_speed * speed_multiplier
            speed_potion_duration -= clock.get_time() / 1000  # reduce by delta time (seconds)
        else:
            player_speed = base_speed
            speed_potion_duration = 0

        # MESSAGE TIMER
        if message_timer > 0:
            message_timer -= 1

        pygame.display.flip()
pygame.quit()
