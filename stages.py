import pygame

class stage:
    def __init__(self, name, assets):
        #Name/assets needed for retrieval of background/platforms
        self.name = name
        self.assets = assets
        
        #Each stage has a background
        self.background = self.assets.getBackground(self.name)
        self.backgroundR = self.background.get_frect(topleft = (0,0))
        
        #Each stage has platforms which are contained in a list for easy access
        self.platforms = self.assets.getPlatforms(self.name)
        #Rect for each of platforms, position determined in children classes
        self.platformsR = [x.get_frect() for x in self.platforms]

        self.platformsCol = [rect.copy() for rect in self.platformsR]
    
    def draw(self, screen):
        screen.blit(self.background, self.backgroundR)
        #Draws all platforms in the list
        #Assumes platforms and the list of rects hve same length
        for i in range(len(self.platforms)):
            screen.blit(self.platforms[i], self.platformsR[i])
    
    def getPlatforms(self):
        return self.platformsR
    
    #for player collisions
    def getHitboxes(self):
        return self.platformsCol
    
def StageFactory(name, assets, sSize):
    match name:
        case "volcano_valley":
            return VolcanoValley(assets, sSize)
        case "celestial_ruins":
            return CelestialRuins(assets,sSize)
        case "arctic_fracture":
            return ArcticFracture(assets, sSize)

class VolcanoValley(stage):
    def __init__(self, assets, sSize):
        super().__init__("volcano_valley", assets)
        self.platformsR[0].midbottom = (sSize[0]/2, sSize[1])
        self.platformsCol[0].center = self.platformsR[0].center

        #Sets the spawn points for volcano valley
        mainPlatSize = self.platformsCol[0].size
        width = mainPlatSize[0]
        height = mainPlatSize[1]
        self.spawnPoint1 = (self.platformsCol[0].centerx-width/4, self.platformsCol[0].top)
        self.spawnPoint2 = (self.platformsCol[0].centerx+width/4, self.platformsCol[0].top)
    
    def getSpawnPoint(self, n):
        if n == 1:
            return self.spawnPoint1
        elif n ==2:
            return self.spawnPoint2
        
        
class CelestialRuins(stage):
    def __init__(self, assets, sSize):
        super().__init__("celestial_ruins", assets)
        self.platformsR[0].center = (sSize[0]/2, sSize[1]/1.75)

        self.platformsCol[0].h = self.platformsCol[0].h/3
        self.platformsCol[0].center = self.platformsR[0].center

        #overlay to reduce noise
        self.overlay= pygame.Surface(sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #Sets the spawn points 
        mainPlatSize = self.platformsCol[0].size
        width = mainPlatSize[0]
        height = mainPlatSize[1]
        self.spawnPoint1 = (self.platformsCol[0].centerx-width/4, self.platformsCol[0].top)
        self.spawnPoint2 = (self.platformsCol[0].centerx+width/4, self.platformsCol[0].top)
    
    def draw(self, screen):
        screen.blit(self.background, self.backgroundR)
        screen.blit(self.overlay, self.overlayR)
        #Draws all platforms in the list
        #Assumes platforms and the list of rects hve same length
        for i in range(len(self.platforms)):
            screen.blit(self.platforms[i], self.platformsR[i])


    def getSpawnPoint(self, n):
        if n == 1:
            return self.spawnPoint1
        elif n ==2:
            return self.spawnPoint2


class ArcticFracture(stage):
    def __init__(self, assets, sSize):
        super().__init__("arctic_fracture", assets)
        self.platformsR[0].center = (sSize[0]/2, sSize[1]/1.75)

        self.platformsCol[0].h = self.platformsCol[0].h/3
        self.platformsCol[0].center = self.platformsR[0].center

        #overlay to reduce noise
        self.overlay= pygame.Surface(sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #Sets the spawn points 
        mainPlatSize = self.platformsCol[0].size
        width = mainPlatSize[0]
        height = mainPlatSize[1]
        self.spawnPoint1 = (self.platformsCol[0].centerx-width/4, self.platformsCol[0].top)
        self.spawnPoint2 = (self.platformsCol[0].centerx+width/4, self.platformsCol[0].top)
    
    def draw(self, screen):
        screen.blit(self.background, self.backgroundR)
        screen.blit(self.overlay, self.overlayR)
        #Draws all platforms in the list
        #Assumes platforms and the list of rects hve same length
        for i in range(len(self.platforms)):
            screen.blit(self.platforms[i], self.platformsR[i])


    def getSpawnPoint(self, n):
        if n == 1:
            return self.spawnPoint1
        elif n ==2:
            return self.spawnPoint2



