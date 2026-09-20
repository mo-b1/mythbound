import pygame
from scene import SceneManager
from networking import server, network

#Initilize pygame
pygame.init()

#Essential program data 
PROGRAM_DATA = {
    "width": 1280,
    "height": 720,
    "dt": 0,
    "controls": {
        "P1 Right" : pygame.K_d,
        "P1 Left" : pygame.K_a,
        "P1 Jump" : pygame.K_w,
        "P1 Light Attack" : pygame.K_p,
        "P1 Heavy Attack" : pygame.K_l,
        "P2 Right" : pygame.K_RIGHT,
        "P2 Left" : pygame.K_LEFT,
        "P2 Jump" : pygame.K_UP,
        "P2 Light Attack" : pygame.K_m,
        "P2 Heavy Attack" : pygame.K_n,
    },
}

#Sets screen size, caption and creates a clock  object
pygame.display.set_caption("Mythbound")
screen = pygame.display.set_mode((PROGRAM_DATA["width"], PROGRAM_DATA["height"]))
clock = pygame.time.Clock()


#creates server, network, assets and SceneManager objects
s = server()
n = network()
SM = SceneManager(network=n, server=s, 
                sWidth=PROGRAM_DATA["width"], sHeight=PROGRAM_DATA["height"],
                controls=PROGRAM_DATA["controls"]
                )

running = True
while running:
    #Retrieves all events for scene manager to handle
    events = pygame.event.get()
    screen.fill((0,0,0))

    #Retrieves mouse position, buttons pressed, state of all keys
    mpos = pygame.mouse.get_pos()
    mbut = pygame.mouse.get_pressed()
    mbut_j = pygame.mouse.get_just_pressed()
    keys = pygame.key.get_pressed()
    keys_j = pygame.key.get_just_pressed()

    #Scene manager takes care of handling events, logic and drawing sprites to the screen
    SM.handle_events(events)
    SM.update(PROGRAM_DATA["dt"], mpos, mbut,mbut_j, keys, keys_j)
    SM.draw(screen)

    #time elapsed since last frame (used for fair movement speeds)
    #capped as moving the window causes the time to accumulate
    PROGRAM_DATA["dt"] = min(clock.tick(60)/1000, 0.1) 

    #Updates display
    pygame.display.flip()

pygame.quit()




