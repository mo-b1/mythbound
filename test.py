import pygame
from assets import assets

#Initilize pygame
pygame.init()

#Sets screen size, caption and creates a clock  object
pygame.display.set_caption("Mythbound")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

assets = assets((1280,720), (96,96))
assets.load()
animations = assets.getAnimations("knight")

type = 0
frame = 0

def type_changer(keys_j):
    global type
    global frame
    match type:
        case 0 :
            t = "idle"
        case 1:
            t = "run"
        case 2:
            t = "jump"
        case 3:
            t = "attack1"
        case 4:
            t  = "attack2"

    if keys_j[pygame.K_e]:
        type +=1
        frame = 0 
        if type == 5:
            type = 0
    if keys_j[pygame.K_q]:
        frame = (frame+1)%len(animations[t])

    

    screen.blit(animations[t][frame], animations[t][frame].get_frect(center=(1280/2, 720/2)))
    mask = pygame.mask.from_surface(animations[t][frame])
    maskI = mask.to_surface()
    screen.blit(maskI, (0,0))
    print(animations[t][frame].get_size())
    

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    #Retrieves all events for scene manager to handle
    
    screen.fill((0,0,0))

    keys_j = pygame.key.get_just_pressed()

    type_changer(keys_j)

    #Updates display
    pygame.display.flip()

pygame.quit()



