#Make sure that the folder name is Crownfall

import pygame
import os

pygame.init()
os.chdir(os.path.dirname(__file__))  # make working dir = script folder

# CONSTANTS & SETUP
ROOM_WIDTH = 800
ROOM_HEIGHT = 600
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
EDGE_BUFFER = 5

screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Player setup
player = pygame.Rect(50, ROOM_HEIGHT - 100, 80, 80)
speed = 20

# Room system
current_room = [0, 0, 0]
room_colliders = {}

# PLAYER HEALTH & INVENTORY
health = 100
max_health = 100
inventory_visible = False
inventory = {"Gold": 0, "Artifacts": 0, "Potions": 0}
inventory_limit = 10
collected_artifacts = set()
collected_gold = set()
collected_potions = set()

# OBJECT DRAW FUNCTION
def draw_objects(x, y, obj_type, surface, colliders, artifacts, gold, potions):
    """Draws an object on the game surface and adds its collider or collectible
    reference to the appropriate list based on object type."""

    def load_img(name, w, h, offset=(0, 0)):
        """Loads, scales, and draws an image, returning its rectangle."""
        # Load and scale image
        img = pygame.image.load(f"crownfall_images/{name}.png")
        img = pygame.transform.scale(img, (w, h))
        surface.blit(img, (x - offset[0], y - offset[1]))
        return pygame.Rect(x, y, w, h)

    # Environment
    if obj_type == "tree1":
        rect = load_img("Tree_1", 180, 240)
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
        rect = load_img("Villager_1", 100, 200)
        colliders.append(rect)

    # Collectibles
    elif obj_type == "artifact":
        rect = load_img("Artifact", 40, 40)
        artifacts.append(rect)
    elif obj_type == "gold":
        rect = load_img("Gold", 50, 50)
        gold.append(rect)
    elif obj_type == "potion":
        rect = load_img("Potion", 40, 40)
        potions.append(rect)

# ROOM DRAW FUNCTION
def draw_current_room(surface, level, row, col, collected_artifacts, collected_gold, collected_potions):
    """Draws the current room based on the level, row, and column.
    Adds interactive and environmental objects to their respective lists."""

    # Draw background
    bg = pygame.image.load("crownfall_images/Level_bg_1.jpg")
    bg = pygame.transform.scale(bg, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(bg, (0, 0))

    # Object containers for this room
    colliders, artifacts, gold, potions = [], [], [], []

    # ──────────────── LEVEL 1 ────────────────
    if level == 0 and row == 0 and col == 0:
        # Level 1 - Bottom-left room
        draw_objects(400, 250, "house1", surface, colliders, artifacts, gold, potions) # House
        draw_objects(225, 300, "tree1", surface, colliders, artifacts, gold, potions) # Tree
        draw_objects(25, 50, "rock1", surface, colliders, artifacts, gold, potions)  # Rock
        draw_objects(175, 25, "rock2", surface, colliders, artifacts, gold, potions)  # Rock 2
        if can_draw(600, 150, collected_artifacts):
            draw_objects(600, 150, "artifact", surface, colliders, artifacts, gold, potions)  # Artifact

    elif level == 0 and row == 0 and col == 1:
        # Level 1 - Bottom-middle room
        draw_objects(550, 300, "tree2", surface, colliders, artifacts, gold, potions)  # Tree
        draw_objects(350, 250, "rock2", surface, colliders, artifacts, gold, potions)  # Rock 2
        draw_objects(450, 100, "villager", surface, colliders, artifacts, gold, potions)  # Villager
        if can_draw(400, 500, collected_gold):
            draw_objects(400, 500, "gold", surface, colliders, artifacts, gold, potions)  # Gold

    elif level == 0 and row == 0 and col == 2:
        # Level 1 - Bottom-right room
        draw_objects(350, 150, "house2", surface, colliders, artifacts, gold, potions)  # Big House
        draw_objects(100, 200, "tree1", surface, colliders, artifacts, gold, potions)  # Tree
        draw_objects(450, 500, "rock1", surface, colliders, artifacts, gold, potions)  # Rock
        draw_objects(600, 400, "villager", surface, colliders, artifacts, gold, potions)  # Villager
        if can_draw(700, 100, collected_artifacts):
            draw_objects(700, 100, "artifact", surface, colliders, artifacts, gold, potions)  # Artifact

    elif level == 0 and row == 1 and col == 0:
        # Level 1 - Middle-left room
        draw_objects(225, 250, "tree1", surface, colliders, artifacts, gold, potions)  # Tree
        draw_objects(600, 350, "rock1", surface, colliders, artifacts, gold, potions)  # Rock
        draw_objects(25, 25, "villager", surface, colliders, artifacts, gold, potions)  # Villager
        if can_draw(400, 150, collected_potions):
            draw_objects(400, 150, "potion", surface, colliders, artifacts, gold, potions)  # Potion
        if can_draw(700, 500, collected_gold):
            draw_objects(700, 500, "gold", surface, colliders, artifacts, gold, potions)  # Gold

    elif level == 0 and row == 1 and col == 1:
        # Level 1 - Center room
        draw_objects(400, 250, "house1", surface, colliders, artifacts, gold, potions)  # House
        draw_objects(150, 350, "tree1", surface, colliders, artifacts, gold, potions)  # Tree
        if can_draw(600, 150, collected_gold):
            draw_objects(600, 150, "gold", surface, colliders, artifacts, gold, potions)  # Gold
        if can_draw(700, 400, collected_artifacts):
            draw_objects(700, 400, "artifact", surface, colliders, artifacts, gold, potions)  # Artifact
        #weapon and enemy

    elif level == 0 and row == 1 and col == 2:
        # Level 1 - Middle-right room
        draw_objects(100, 200, "rock2", surface, colliders, artifacts, gold, potions)  # Rock 2
        #enemy and water

    elif level == 0 and row == 2 and col == 0:
        # Level 1 - Top-left room
        draw_objects(200, 225, "tree1", surface, colliders, artifacts, gold, potions)  # Tree
        draw_objects(400, 400, "rock1", surface, colliders, artifacts, gold, potions)  # Rock
        if can_draw(200, 150, collected_gold):
            draw_objects(200, 150, "gold", surface, colliders, artifacts, gold, potions)  # Gold

    elif level == 0 and row == 2 and col == 1:
        # Level 1 - Top-middle room
        draw_objects(600, 300, "tree1", surface, colliders, artifacts, gold, potions)  # Tree
        draw_objects(200, 25, "house1", surface, colliders, artifacts, gold, potions)  # House
        if can_draw(50, 100, collected_gold):
            draw_objects(50, 100, "gold", surface, colliders, artifacts, gold, potions)  # Gold
        #enemy

    elif level == 0 and row == 2 and col == 2:
        # Level 1 - Top-right room
        if can_draw(200, 150, collected_gold):
            draw_objects(200, 150, "gold", surface, colliders, artifacts, gold, potions)  # Gold
        #final boss

    # ──────────────── LEVEL 2 ────────────────
    elif level == 1 and row == 0 and col == 0:
        # Level 2 - Bottom-left room
        pygame.draw.rect(surface, (100, 100, 255), (350, 250, 100, 100))

    elif level == 1 and row == 0 and col == 1:
        # Level 2 - Bottom-middle room
        pygame.draw.rect(surface, (255, 100, 100), (300, 200, 200, 200))

    elif level == 1 and row == 0 and col == 2:
        # Level 2 - Bottom-right room
        pygame.draw.line(surface, (0, 255, 100), (0, 600), (800, 0), 5)

    elif level == 1 and row == 1 and col == 0:
        # Level 2 - Middle-left room
        pygame.draw.ellipse(surface, (100, 255, 255), (250, 250, 300, 150))

    elif level == 1 and row == 1 and col == 1:
        # Level 2 - Center room 
        pygame.draw.polygon(surface, (200, 200, 0), [(400, 100), (600, 500), (200, 500)])

    elif level == 1 and row == 1 and col == 2:
        # Level 2 - Middle-right room
        pygame.draw.rect(surface, (0, 100, 200), (150, 150, 500, 300), 8)

    elif level == 1 and row == 2 and col == 0:
        # Level 2 - Top-left room
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (800, 600), 2)

    elif level == 1 and row == 2 and col == 1:
        # Level 2 - Top-middle room
        pygame.draw.circle(surface, (0, 255, 0), (400, 300), 60)

    elif level == 1 and row == 2 and col == 2:
        # Level 2 - Top-right room
        pygame.draw.rect(surface, (0, 0, 255), (250, 200, 300, 200))

    # ──────────────── LEVEL 3 ────────────────
    elif level == 2 and row == 0 and col == 0:
        # Level 3 - Bottom-left room
        draw_objects(400, 300, "tree1", surface, colliders, artifacts, gold, potions)
        #water

    elif level == 2 and row == 0 and col == 1:
        # Level 3 - Bottom-middle room
        draw_objects(100, 300, "villager", surface, colliders, artifacts, gold, potions)
        draw_objects(500, 300, "villager", surface, colliders, artifacts, gold, potions)
        draw_objects(600, 140, "tree1", surface, colliders, artifacts, gold, potions)

    elif level == 2 and row == 0 and col == 2:
        # Level 3 - Bottom-right room
        draw_objects(0, 150, "tree1", surface, colliders, artifacts, gold, potions)
        if can_draw(700, 25, collected_gold):
            draw_objects(700, 25, "gold", surface, colliders, artifacts, gold, potions)
        if can_draw(700, 500, collected_potions):
            draw_objects(700, 500, "potion", surface, colliders, artifacts, gold, potions)  
        #water

    elif level == 2 and row == 1 and col == 0:
        # Level 3 - Middle-left room
        pygame.draw.ellipse(surface, (100, 0, 200), (200, 200, 400, 150))

    elif level == 2 and row == 1 and col == 1:
        # Level 3 - Center room
        pygame.draw.polygon(surface, (0, 200, 200), [(400, 150), (550, 450), (250, 450)])

    elif level == 2 and row == 1 and col == 2:
        # Level 3 - Middle-right room
        pygame.draw.rect(surface, (255, 128, 0), (100, 100, 600, 400), 6)

    elif level == 2 and row == 2 and col == 0:
        # Level 3 - Top-left room
        pygame.draw.line(surface, (128, 128, 128), (0, 300), (800, 300), 3)

    elif level == 2 and row == 2 and col == 1:
        # Level 3 - Top-middle room
        pygame.draw.circle(surface, (0, 128, 128), (400, 300), 90, 3)

    elif level == 2 and row == 2 and col == 2:
        # Level 3 - Top-right room
        pygame.draw.rect(surface, (128, 0, 0), (200, 150, 400, 300))

    return colliders, artifacts, gold, potions

# HUD DRAW
def draw_hud(surface, level, row, col):
    """Draws the player HUD, including the health bar, room info, and inventory display."""
    # Health bar box (top-left)
    box_x, box_y = 15, 10  # overall position
    box_width, box_height = 220, 70
    pygame.draw.rect(surface, (0, 0, 0), (box_x, box_y, box_width, box_height))  # outer black box
    pygame.draw.rect(surface, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)  # white outline

    # Health label text
    label = font.render("Health", True, (255, 255, 255))
    surface.blit(label, (box_x + 70, box_y + 10))  # centered horizontally above bar

    # Health bar
    bar_x, bar_y = box_x + 10, box_y + 35
    bar_width, bar_height = 200, 25
    pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # red background
    pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * (health / max_health), bar_height))  # green fill
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)  # white outline

    # Room info box (top-right)
    text = f"Level {level + 1} - {['Bottom','Middle','Top'][row]} {['Left','Middle','Right'][col]}"
    info = font.render(text, True, (255, 255, 255))
    rect = info.get_rect(topright=(ROOM_WIDTH - 20, 20))
    pygame.draw.rect(surface, (0, 0, 0), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10))
    pygame.draw.rect(surface, (255, 255, 255), (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10), 2)
    surface.blit(info, rect)

    # Inventory
    if inventory_visible:
        inv_rect = pygame.Rect(20, 90, 250, 120)
        pygame.draw.rect(surface, (0, 0, 0), inv_rect)
        pygame.draw.rect(surface, (255, 255, 255), inv_rect, 2)
        y = 110
        for item, count in inventory.items():
            txt = font.render(f"{item}: {count}", True, (255, 255, 255))
            surface.blit(txt, (40, y))
            y += 30

# COLLISION & MOVEMENT
def move_player_with_collision(dx, dy, colliders):
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

def handle_room_transition():
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
        # Transition to next level from top-right
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
        else:
            player.bottom = ROOM_HEIGHT

# Helper functions
def not_collected(x, y, s):
    """Checks if an item at (x, y) in the current room hasn't been collected."""
    return (level, row, col, x, y) not in s
def can_draw(x, y, s):
    """Returns True if an item should be drawn (not already collected)."""
    return (level, row, col, x, y) not in s

# MAIN LOOP
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_e:
                inventory_visible = not inventory_visible

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    dx *= speed
    dy *= speed

    level, row, col = current_room

    # Clear screen before drawing anything
    screen.fill((0, 0, 0))

    # Draw the current room
    colliders, artifacts, gold, potions = draw_current_room(screen, level, row, col, collected_artifacts, collected_gold, collected_potions)

    # Player movement & transitions
    move_player_with_collision(dx, dy, colliders)
    handle_room_transition()

    # ─────────────── Artifact Pickup ───────────────
    for artifact in artifacts[:]:  # make a copy to modify safely
        if player.colliderect(artifact):
            collected_artifacts.add((level, row, col, artifact.x, artifact.y))
            artifacts.remove(artifact)
            inventory["Artifacts"] += 1
    # ─────────────── Gold Pickup ───────────────
    for g in gold[:]:
        if player.colliderect(g):
            collected_gold.add((level, row, col, g.x, g.y))
            gold.remove(g)
            inventory["Gold"] += 20
    # ─────────────── Potion Pickup ───────────────
    for p in potions[:]:
        if player.colliderect(p):
            collected_potions.add((level, row, col, p.x, p.y))
            potions.remove(p)
            inventory["Potions"] += 1

    pygame.draw.rect(screen, (0, 0, 0), player)  # player
    draw_hud(screen, level, row, col)  # HUD

    pygame.display.flip()
    clock.tick(60)

