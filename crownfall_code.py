import pygame
import os

from pygame import draw
pygame.init()
os.chdir(os.path.dirname(__file__))  # make working dir = script folder

# Constants
ROOM_WIDTH = 800
ROOM_HEIGHT = 600
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
EDGE_BUFFER = 5

# Setup
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
current_room = [0, 0, 0]
player = pygame.Rect(50, ROOM_HEIGHT - 100, 80, 80)
speed = 10

# Store collidable objects for each room
room_colliders = {}

# Functions to draw objects
def draw_objects(x, y, width, height, surface, colliders):
    """Draws an object (tree, rock, wall, house, etc) onto a given surface at position (x, y) with the specified dimensions (weight, height)
    Certain object types (tree, rock, wall, house) are added to the colliders list to create collision boundaries.
    Takes in: x, y, width, height, surface to draw on, list of colliders
    Does: Draw the object and add to colliders if necessary"""
    # Create rectangle for the object
    obj_rect = pygame.Rect(x, y, width, height)

    # Tree
    if width == 180 and height == 240:
        image = pygame.image.load("crownfall_images/Tree_1.png")
        image = pygame.transform.scale(image, (width + 50, height + 50))
        surface.blit(image, (x - 25, y - 25))
        colliders.append(obj_rect)
    # Tree 2
    elif width == 150 and height == 200:
        image = pygame.image.load("crownfall_images/Tree_2.png")
        image = pygame.transform.scale(image, (width + 50, height + 50))
        surface.blit(image, (x - 25, y - 25))
        colliders.append(obj_rect)
    # Rock
    elif width == 100 and height == 100:
        image = pygame.image.load("crownfall_images/Rock_1.png")
        image = pygame.transform.scale(image, (width + 100, height + 100))
        surface.blit(image, (x - 50, y - 50))
        colliders.append(obj_rect)
    # Rock 2
    elif width == 50 and height == 75:
        image = pygame.image.load("crownfall_images/Rock_2.png")
        image = pygame.transform.scale(image, (width + 100, height + 100))
        surface.blit(image, (x - 50, y - 50))
        colliders.append(obj_rect)
    # Wall
    elif width == 150 and height == 200:
        image = pygame.image.load("crownfall_images/Wall.png")
        image = pygame.transform.scale(image, (width + 100, height + 100))
        surface.blit(image, (x - 50, y - 50))
        colliders.append(obj_rect)
    # House
    elif width == 300 and height == 300:
        image = pygame.image.load("crownfall_images/House_1.png")
        image = pygame.transform.scale(image, (width + 100, height + 100))
        surface.blit(image, (x - 50, y - 50))
        colliders.append(obj_rect)
    # House 2
    elif width == 300 and height == 400:
        image = pygame.image.load("crownfall_images/House_2.png")
        image = pygame.transform.scale(image, (width + 100, height + 100))
        surface.blit(image, (x - 50, y - 50))
        colliders.append(obj_rect)
    # Villager
    elif width == 100 and height == 200:
        image = pygame.image.load("crownfall_images/Villager_1.png")
        image = pygame.transform.scale(image, (width + 20, height + 20))
        surface.blit(image, (x - 10, y - 10))
        colliders.append(obj_rect)
    # Gold -> (walkable)
    elif width == 50 and height == 50:
        image = pygame.image.load("crownfall_images/Gold.png")
        image = pygame.transform.scale(image, (width + 30, height + 30))
        surface.blit(image, (x - 15, y - 15))    
    # Artifact -> (walkable)
    elif width == 25 and height == 25:
        image = pygame.image.load("crownfall_images/Artifact.png")
        image = pygame.transform.scale(image, (width + 40, height + 40))
        surface.blit(image, (x - 20, y - 20))

def draw_current_room(surface, level, row, col):
    """Renders all visual elements (placeholders or objects) for the specified room in the grid.
    Automatically updates the room_colliders dictionary with collision rectangles for that room.
    Takes in: surface to draw on, level index, row index, column index
    Does: Draw the room and update colliders"""
    # Clear previous drawings
    image = pygame.image.load("crownfall_images/Level_bg_1.jpg")
    image = pygame.transform.scale(image, (ROOM_WIDTH, ROOM_HEIGHT))
    surface.blit(image, (0, 0))
    colliders = []
    
    #Tree: 180x240
    #Tree 2: 150x200
    #Rock: 100x100
    #Rock 2: 50x75
    #Wall: 150x200
    #House: 300x300
    #House 2: 300x400
    #Villager: 100x200
    #Gold: 50x50
    #Artifact: 25x25
    
    #draw_objects(x, y, width, height, surface, colliders)
    # ──────────────── LEVEL 1 ────────────────
    if level == 0 and row == 0 and col == 0:
        # Level 1 - Bottom-left room
        draw_objects(400, 250, 300, 300, surface, colliders) # House
        draw_objects(225, 300, 180, 240, surface, colliders) # Tree
        draw_objects(25, 50, 100, 100, surface, colliders)  # Rock
        draw_objects(175, 25, 50, 75, surface, colliders)  # Rock 2
        draw_objects(600, 150, 25, 25, surface, colliders)  # Artifact
    elif level == 0 and row == 0 and col == 1:
        # Level 1 - Bottom-middle room
        draw_objects(100, 100, 150, 200, surface, colliders)  # Tree 2
        draw_objects(350, 250, 50, 75, surface, colliders)  # Rock 2
        draw_objects(450, 100, 100, 200, surface, colliders)  # Villager
        draw_objects(600, 400, 50, 50, surface, colliders)  # Gold

    elif level == 0 and row == 0 and col == 2:
        # Level 1 - Bottom-right room (placeholder line)
        pygame.draw.line(surface, (0, 0, 255), (0, 0), (800, 600), 5)

    elif level == 0 and row == 1 and col == 0:
        # Level 1 - Middle-left room (ellipse placeholder)
        pygame.draw.ellipse(surface, (255, 255, 0), (300, 200, 200, 100))

    elif level == 0 and row == 1 and col == 1:
        # Level 1 - Center room (polygon placeholder)
        pygame.draw.polygon(surface, (255, 0, 255), [(400, 200), (500, 400), (300, 400)])

    elif level == 0 and row == 1 and col == 2:
        # Level 1 - Middle-right room (outlined rect placeholder)
        pygame.draw.rect(surface, (0, 255, 255), (100, 100, 600, 400), 10)

    elif level == 0 and row == 2 and col == 0:
        # Level 1 - Top-left room (line placeholder)
        pygame.draw.line(surface, (255, 255, 255), (0, 300), (800, 300), 3)

    elif level == 0 and row == 2 and col == 1:
        # Level 1 - Top-middle room (circle placeholder)
        pygame.draw.circle(surface, (128, 0, 128), (400, 300), 75, 5)

    elif level == 0 and row == 2 and col == 2:
        # Level 1 - Top-right room
        pygame.draw.rect(surface, (128, 128, 0), (200, 150, 400, 300))

    # ──────────────── LEVEL 2 ────────────────
    elif level == 1 and row == 0 and col == 0:
        # Level 2 - Bottom-left room
        pygame.draw.rect(surface, (100, 100, 255), (350, 250, 100, 100))

    elif level == 1 and row == 0 and col == 1:
        # Level 2 - Bottom-middle room
        pygame.draw.rect(surface, (255, 100, 100), (300, 200, 200, 200))

    elif level == 1 and row == 0 and col == 2:
        # Level 2 - Bottom-right room (diagonal line placeholder)
        pygame.draw.line(surface, (0, 255, 100), (0, 600), (800, 0), 5)

    elif level == 1 and row == 1 and col == 0:
        # Level 2 - Middle-left room (ellipse)
        pygame.draw.ellipse(surface, (100, 255, 255), (250, 250, 300, 150))

    elif level == 1 and row == 1 and col == 1:
        # Level 2 - Center room (polygon)
        pygame.draw.polygon(surface, (200, 200, 0), [(400, 100), (600, 500), (200, 500)])

    elif level == 1 and row == 1 and col == 2:
        # Level 2 - Middle-right room (outlined big rect)
        pygame.draw.rect(surface, (0, 100, 200), (150, 150, 500, 300), 8)

    elif level == 1 and row == 2 and col == 0:
        # Level 2 - Top-left room (small diagonal line)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (800, 600), 2)

    elif level == 1 and row == 2 and col == 1:
        # Level 2 - Top-middle room (circle)
        pygame.draw.circle(surface, (0, 255, 0), (400, 300), 60)

    elif level == 1 and row == 2 and col == 2:
        # Level 2 - Top-right room
        pygame.draw.rect(surface, (0, 0, 255), (250, 200, 300, 200))

    # ──────────────── LEVEL 3 ────────────────
    elif level == 2 and row == 0 and col == 0:
        # Level 3 - Bottom-left room (small circle placeholder)
        pygame.draw.circle(surface, (255, 255, 255), (400, 300), 30)

    elif level == 2 and row == 0 and col == 1:
        # Level 3 - Bottom-middle room
        pygame.draw.rect(surface, (200, 100, 50), (300, 250, 200, 100))

    elif level == 2 and row == 0 and col == 2:
        # Level 3 - Bottom-right room (line)
        pygame.draw.line(surface, (50, 200, 100), (0, 0), (800, 600), 4)

    elif level == 2 and row == 1 and col == 0:
        # Level 3 - Middle-left room (ellipse)
        pygame.draw.ellipse(surface, (100, 0, 200), (200, 200, 400, 150))

    elif level == 2 and row == 1 and col == 1:
        # Level 3 - Center room (polygon)
        pygame.draw.polygon(surface, (0, 200, 200), [(400, 150), (550, 450), (250, 450)])

    elif level == 2 and row == 1 and col == 2:
        # Level 3 - Middle-right room (big rect)
        pygame.draw.rect(surface, (255, 128, 0), (100, 100, 600, 400), 6)

    elif level == 2 and row == 2 and col == 0:
        # Level 3 - Top-left room (horizontal line)
        pygame.draw.line(surface, (128, 128, 128), (0, 300), (800, 300), 3)

    elif level == 2 and row == 2 and col == 1:
        # Level 3 - Top-middle room (large circle)
        pygame.draw.circle(surface, (0, 128, 128), (400, 300), 90, 3)

    elif level == 2 and row == 2 and col == 2:
        # Level 3 - Top-right room
        pygame.draw.rect(surface, (128, 0, 0), (200, 150, 400, 300))

    # Save room-specific colliders
    room_colliders[(level, row, col)] = colliders

# Movement and collision functions
def move_player_with_collision(dx, dy, colliders):
    """Moves the player rectangle based on input deltas (dx, dy) while preventing overlap with solid objects (colliders).
    Takes in: change in x (dx), change in y (dy), list of colliders
    Does: Move player with collision detection"""
    # Move horizontally with collision
    player.x += dx
    for collider in colliders:
        if player.colliderect(collider):
            if dx > 0:  # Moving right
                player.right = collider.left
            elif dx < 0:  # Moving left
                player.left = collider.right

    # Move vertically with collision
    player.y += dy
    for collider in colliders:
        if player.colliderect(collider):
            if dy > 0:  # Moving down
                player.bottom = collider.top
            elif dy < 0:  # Moving up
                player.top = collider.bottom

def handle_room_transition(colliders):
    """Handles movement between rooms (left, right, up, down) when the player reaches a screen edge.
    Prevents transitions if the player is blocked by nearby colliders.
    Also handles moving to the next level when the player exits the top-right corner of the top-right room.
    Takes in: list of colliders
    Does: Transition between rooms and levels"""
    # Set up for room transition
    global current_room
    level, row, col = current_room
    buffer = EDGE_BUFFER

    # If blocked by a wall/house/tree at the edge, do not transition
    left_edge = pygame.Rect(0, player.y, buffer, player.height)
    right_edge = pygame.Rect(ROOM_WIDTH - buffer, player.y, buffer, player.height)

    # Check for blockers
    blocked_left = any(left_edge.colliderect(c) for c in colliders)
    blocked_right = any(right_edge.colliderect(c) for c in colliders)

    # Move left
    if player.left < 0 and not blocked_left:
        if col > 0:
            current_room[2] -= 1
            player.right = ROOM_WIDTH
        else:
            player.left = 0
    elif player.left < 0:
        player.left = 0

    # Move right
    if player.right > ROOM_WIDTH and not blocked_right:
        if col < GRID_WIDTH - 1:
            current_room[2] += 1
            player.left = 0
        else:
            player.right = ROOM_WIDTH
    elif player.right > ROOM_WIDTH:
        player.right = ROOM_WIDTH

    # Move up
    if player.top < 0:
        if row < GRID_HEIGHT - 1:
            current_room[1] += 1
            player.bottom = ROOM_HEIGHT
        else:
            player.top = 0

    # Move down
    if player.bottom > ROOM_HEIGHT:
        if row > 0:
            current_room[1] -= 1
            player.top = 0
        else:
            player.bottom = ROOM_HEIGHT
    # Special case: go to next level when near top-right corner of top-right room
    if current_room[1] == GRID_HEIGHT - 1 and current_room[2] == GRID_WIDTH - 1:
       if player.top < 50 and player.right > ROOM_WIDTH - 50:  # more forgiving area
          if current_room[0] < LEVELS - 1:
             current_room[0] += 1  # Go to next level
             current_room[1] = 0   # Reset to bottom-left room
             current_room[2] = 0
             player.left = 50
             player.top = ROOM_HEIGHT - 100

#Mini map area name function
def get_area_name(row, col):
   """Generates a readable name for the area based on its row and column indices.
   Takes in: row index, column index
   Does: Return area name string"""
   # Define names for rows and columns
   row_names = ["Bottom", "Middle", "Top"]
   col_names = ["Left", "Middle", "Right"]
   return f"{row_names[row]} {col_names[col]}"

# Game loop
running = True
while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

    keys = pygame.key.get_pressed()
    move_left  = keys[pygame.K_a] or keys[pygame.K_LEFT]
    move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    move_up    = keys[pygame.K_w] or keys[pygame.K_UP]
    move_down  = keys[pygame.K_s] or keys[pygame.K_DOWN]
    dx = (move_right - move_left) * speed
    dy = (move_down - move_up) * speed


    level, row, col = current_room
    draw_current_room(screen, level, row, col)
    colliders = room_colliders.get((level, row, col), [])

    move_player_with_collision(dx, dy, colliders)
    handle_room_transition(colliders)

    pygame.draw.rect(screen, (0, 0, 0), player)

    area_text = f"Level {level + 1} - {get_area_name(row, col)}"
    text_surface = font.render(area_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(topright=(ROOM_WIDTH - 10, 10))
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()