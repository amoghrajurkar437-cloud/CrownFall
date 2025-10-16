#Basic setup 
import pygame, sys
pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode([800,400])

running = True
while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         pygame.quit()
         sys.exit()   
   
   pygame.display.flip()
   clock.tick(60)
   
