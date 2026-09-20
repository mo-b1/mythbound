import pygame

# HUD for each round

class HUD:
    def __init__(self, sSize, assets, timer=90):
        self.font = assets.loadFont("PressStart2P.ttf", 32)
        #sets the timer for each round
        self.timer = timer

        self.pos1 = (sSize[0]/5, 0)
        #pos 2 is based on pos 1 for easy changes
        self.pos2 =  (sSize[0]- self.pos1[0], self.pos1[1])

        #initial healthbar sizes
        self.size = (sSize[0]/4, sSize[1]/64)
        
        #the bars that will hold the substance
        self.healthBar1 = pygame.Surface(self.size)
        self.healthBar1.fill((80, 10, 25))
        self.healthBar2 = pygame.Surface(self.size)
        self.healthBar2.fill((10, 25, 80))
        self.healthBar1R = self.healthBar1.get_frect(topleft = self.pos1)
        self.healthBar2R = self.healthBar2.get_frect(topright = self.pos2)

        #start time in seconds
        self.sTime = pygame.time.get_ticks()/1000
        self.sSize  = sSize
    
    def reset(self):
        self.sTime = pygame.time.get_ticks()/1000
    
    def update(self, ):
        #current time in seconds
        cTime = pygame.time.get_ticks()/1000

        #if round has ended, return True
        if cTime - self.sTime >= self.timer:
            return True
        else:
            return False  
    
    def drawTime(self, screen):
        #current time is difference between current and start
        CTIME = pygame.time.get_ticks()/1000 - self.sTime
        #text surface/rect
        cTime = self.font.render(str(int(CTIME)), True, (255,255,255))
        cTimeR = cTime.get_frect(midtop = (self.sSize[0]/2, 0))
        #draw text to screen
        screen.blit(cTime, cTimeR)

    def draw(self, screen, player1, player2):
        #Calculates ratio of health left
        health1Ratio = player1.health/player1.maxHealth
        health2Ratio = player2.health/player2.maxHealth

        #new sizes for the health
        size1 =  max([health1Ratio*self.healthBar1.get_width(), 1])
        size2 =  max([health2Ratio*self.healthBar2.get_width(), 1])

        #the health substance, starts at 100% size
        bar1 = pygame.Surface((size1, self.healthBar1.get_height()))
        bar1.fill((180, 20, 20))
        bar2 = pygame.Surface((size2, self.healthBar2.get_height()))
        bar2.fill((20, 80, 180))


        screen.blit(self.healthBar1, self.healthBar1R)
        screen.blit(self.healthBar2, self.healthBar2R)
        #inner bars
        screen.blit(bar1, bar1.get_frect(topleft = self.healthBar1R.topleft))
        #topright for p2 as that is on the right side of the screen
        screen.blit(bar2, bar2.get_frect(topright = self.healthBar2R.topright))
        
        self.drawTime(screen)
