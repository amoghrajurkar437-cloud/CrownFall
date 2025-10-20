import pygame
pygame.init()

# Constants
ROOM_WIDTH = 800
ROOM_HEIGHT = 600
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3

# Setup
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
clock = pygame.time.Clock()

# Initialize rooms and player
rooms = []  # This will hold all levels of rooms
for level in range(LEVELS):  # Loop through each level
   level_rooms = []  # List to hold all rows in this level
   for row in range(GRID_HEIGHT):  # Loop through each row in the level
      row_rooms = []  # List to hold all columns (rooms) in this row
      for col in range(GRID_WIDTH):  # Loop through each column in the row
         room_surface = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT))  # Create a blank room surface
         row_rooms.append(room_surface)  # Add the room surface to the current row
      level_rooms.append(row_rooms)  # Add the completed row to the current level
   rooms.append(level_rooms)  # Add the completed level to the main rooms list

current_room = [0, 0, 0]  # [level, row, column]
player = pygame.Rect(50, ROOM_HEIGHT - 100, 40, 40)
speed = 5

def handle_room_transition():
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
      else:
         player.top = 0

   # Move down
   elif player.bottom > ROOM_HEIGHT:
      if row > 0:
         current_room[1] -= 1
         player.top = 0
      else:
         player.bottom = ROOM_HEIGHT

   # Special case: top-right of top-right room
   if current_room[1] == GRID_HEIGHT - 1 and current_room[2] == GRID_WIDTH - 1:
      if player.top == 0 and player.right == ROOM_WIDTH:
         if current_room[0] < LEVELS - 1:
            current_room[0] += 1  # Go to next level
            current_room[1] = 0   # Reset to bottom-left room
            current_room[2] = 0
            player.left = 50
            player.top = ROOM_HEIGHT - 100



def draw_current_room(surface, level, row, col):
   # Base color for every room
   surface.fill((255, 255, 255))

    # ──────────────── LEVEL 1 ────────────────
   if level == 0 and row == 0 and col == 0:
      # Level 1 - Bottom-left room
      pygame.draw.circle(surface, (255, 0, 0), (400, 300), 50)
   elif level == 0 and row == 0 and col == 1:
      # Level 1 - Bottom-middle room
      pygame.draw.rect(surface, (0, 255, 0), (350, 250, 100, 100))
   elif level == 0 and row == 0 and col == 2:
      # Level 1 - Bottom-right room
      pygame.draw.line(surface, (0, 0, 255), (0, 0), (800, 600), 5)
   elif level == 0 and row == 1 and col == 0:
      # Level 1 - Middle-left room
      pygame.draw.ellipse(surface, (255, 255, 0), (300, 200, 200, 100))
   elif level == 0 and row == 1 and col == 1:
      # Level 1 - Center room
      pygame.draw.polygon(surface, (255, 0, 255), [(400, 200), (500, 400), (300, 400)])
   elif level == 0 and row == 1 and col == 2:
      # Level 1 - Middle-right room
      pygame.draw.rect(surface, (0, 255, 255), (100, 100, 600, 400), 10)
   elif level == 0 and row == 2 and col == 0:
      # Level 1 - Top-left room
      pygame.draw.line(surface, (255, 255, 255), (0, 300), (800, 300), 3)
   elif level == 0 and row == 2 and col == 1:
      # Level 1 - Top-middle room
      pygame.draw.circle(surface, (128, 0, 128), (400, 300), 75, 5)
   elif level == 0 and row == 2 and col == 2:
      # Level 1 - Top-right room
      pygame.draw.rect(surface, (128, 128, 0), (200, 150, 400, 300))

    # ──────────────── LEVEL 2 ────────────────
   if level == 1 and row == 0 and col == 0:
      # Level 2 - Bottom-left room
      pygame.draw.rect(surface, (100, 100, 255), (400, 300, -400, -300))
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
   if level == 2 and row == 0 and col == 0:
      # Level 3 - Bottom-left room
      pygame.draw.circle(surface, (255, 255, 255), (400, 300), 30)
   elif level == 2 and row == 0 and col == 1:
      # Level 3 - Bottom-middle room
      pygame.draw.rect(surface, (200, 100, 50), (300, 250, 200, 100))
   elif level == 2 and row == 0 and col == 2:
      # Level 3 - Bottom-right room
      pygame.draw.line(surface, (50, 200, 100), (0, 0), (800, 600), 4)
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

# Game loop
running = True
while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

   keys = pygame.key.get_pressed()
   if keys[pygame.K_a]: player.x -= speed      # Move left
   if keys[pygame.K_d]: player.x += speed      # Move right
   if keys[pygame.K_w]: player.y -= speed      # Move up
   if keys[pygame.K_s]: player.y += speed      # Move down

   handle_room_transition()
   level, row, col = current_room
   draw_current_room(screen, level, row, col)
   pygame.draw.rect(screen, (0, 255, 0), player)
   pygame.display.flip()
   clock.tick(60)

pygame.quit()







