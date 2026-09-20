import pygame
from assets import assets
import threading
from networking import server, network
from stages import StageFactory
from characters import CharacterFactory
from HUD import HUD
import time

class scene:
    def __init__(self, manager, assets, sSize):
        self.manager = manager
        self.assets = assets 
        self.sSize = sSize 

    def handle_events(self, events):
        #Basic inherited function for all scenes to check whether user closes the window
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


class SceneManager:
    def __init__(self, network, server, sWidth, sHeight, controls):
        self.network = network
        self.server = server
        self.assets = assets((sWidth, sHeight), 0.08)
        self.controls = controls
       

        #Screen dimensions needed for relative sprite placement
        self.sDimensions = (sWidth, sHeight)

        #Sets loading scene as first menu to load assets
        self.current_scene = LoadingScene(self, self.assets, self.sDimensions)

    def change_scene(self, new_scene, *args):
        self.current_scene = new_scene(*args)

    def handle_events(self, events):
        #Each scene will have the parent handle events function, that can be modified
        self.current_scene.handle_events(events)

    def update(self,dt, mpos, mbut,mbut_j, keys, keys_j):
        #Each scene may need keys and mouse buttons pressed for logic
        self.current_scene.update(dt, mpos, mbut,mbut_j, keys, keys_j)

    def draw(self, screen):
        #Calls draw function of current scene
        self.current_scene.draw(screen)

    def quit(self):
        pygame.quit()
        quit()

class LoadingScene(scene):
    def __init__(self, manager, assets, sSize):
        super().__init__(manager, assets,sSize)
        #retrieves loading screen assets
        sf = self.assets.SF
        self.LoadingScreen, self.LoadingBar, self.bar_image = self.assets.getLoadingScreen()

        self.LoadingScreenRect = self.LoadingScreen.get_frect(topleft = (0,0))

        self.LoadingBar = pygame.transform.smoothscale_by(self.LoadingBar, 0.25/1.2*sf)
        self.LoadingBarRect = self.LoadingBar.get_frect(center = (self.sSize[0]/2,self.sSize[1]/2))

        #Bar is scaled to fit within loading bar, max width stored
        self.bar_image = pygame.transform.smoothscale_by(self.bar_image, (0.16/1.2*sf, 0.05/1.2*sf))
        self.BAR_MAXWIDTH = self.bar_image.get_width() #constant
        self.bar_width = self.BAR_MAXWIDTH
        self.barRect = self.bar_image.get_frect(center=(self.sSize[0]/2, self.sSize[1]/2+4)) #slight offset

        #Loading needs to be completed in a seperate thread to avoid freezing
        self.thread = threading.Thread(target= self.assets.load, daemon=True)
        self.thread.start()


    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        #If assets are loaded, scene is changed to main menu
        if self.assets.status() == True:
            self.manager.change_scene(MenuScene, self.manager, self.assets, self.sSize)

        #Multiplies max bar width by ratio of assets loaded 
        ratio = self.assets.ratio()
        self.bar_width = ratio*self.BAR_MAXWIDTH
        

    def draw(self, screen):
        screen.blit(self.LoadingScreen, self.LoadingScreenRect)
        screen.blit(self.LoadingBar, self.LoadingBarRect)
        #Third parameter specfies the area of the rect to be drawn
        #Start at (0,0) topleft and go across to (bar_width, 0) and down to (bar_width, bar_height)
        screen.blit(self.bar_image, self.barRect, (0,0, self.bar_width, self.bar_image.get_height()))


class Button:
    def __init__(self, image, imageG, function, **rect_kwargs):
        #Sets function attribute to the action, called on press
        self.function = function

        #Sets button/glow button 
        self.image = image
        self.imageG = imageG

        #Passes the arguements to create a rect object, more accurate button placing
        self.rect = self.image.get_frect(**rect_kwargs)
        self.rectG = self.imageG.get_frect(**rect_kwargs)

        #Current image (either gold or normal) for when mouse is hovering over it
        self.currentI = self.image
        self.currentR = self.rect

    def update(self, mpos, mbut_j):
        #Checks if mouse is hovering over it
        if self.rectG.collidepoint(mpos):
            #Sets image to gold, if hover
            self.currentI = self.imageG
            self.currentR = self.rectG
            #If mouse press, button function is called
            if mbut_j[0]:
                self.function()
        else:
            #Sets image to normal, if not hover
            self.currentI = self.image
            self.currentR = self.rect

    def draw(self,screen):
        #Draws current button image to screen
        screen.blit(self.currentI, self.currentR)       

class MenuScene(scene):
    def __init__(self, manager, assets, sSize):
        super().__init__(manager, assets, sSize)

        #Sets menu background
        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Creates all the main menu buttons
        #Retrieves button images from assets
        play, playG = self.assets.getButton("play")
        settings, settingsG = self.assets.getButton("settings")
        quit, quitG = self.assets.getButton("quit") 
        self.playButton = Button(play, playG, 
                                 lambda: self.manager.change_scene(PlayMenuScene,self.manager,self.assets, self.sSize), 
                                 center=(self.sSize[0]/2, self.sSize[1]*3/8))
        
        self.settingsButton = Button(settings, settingsG,
                                     lambda: self.manager.change_scene(SettingsScene,self.manager,self.assets, self.sSize), 
                                     center=(self.sSize[0]/2, self.sSize[1]*4/8))
        
        self.quitButton = Button(quit, quitG,
                                 self.manager.quit, 
                                 center=(self.sSize[0]/2, self.sSize[1]*5/8))


    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        #Checks button press/hover
        self.playButton.update(mpos, mbut_j)
        self.settingsButton.update(mpos, mbut_j)
        self.quitButton.update(mpos, mbut_j)

    def draw(self, screen):
        #Draws background and buttons
        screen.blit(self.background, self.backgroundRect)
        self.playButton.draw(screen)
        self.settingsButton.draw(screen)
        self.quitButton.draw(screen)

class PlayMenuScene(scene):
    def __init__(self, manager, assets, sSize):
        super().__init__(manager, assets,sSize)

        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        practise, practiseG = self.assets.getButton("practise")
        local, localG = self.assets.getButton("local")
        join,joinG = self.assets.getButton("join")
        host,hostG = self.assets.getButton("host")
        back,backG = self.assets.getButton("back")
        self.practiseButton = Button(practise,practiseG, lambda: 
                                     self.manager.change_scene(StageSelectScene, self.manager, self.assets, self.sSize, "practise"),
                                      center=(self.sSize[0]/2, self.sSize[1]*2.5/8))
        self.localButton = Button(local, localG, lambda:
                                  self.manager.change_scene(StageSelectScene, self.manager, self.assets, self.sSize, "local")
                                  , center=(self.sSize[0]/2, self.sSize[1]*3.5/8))
        self.joinButton = Button(join, joinG, lambda:
                                  self.manager.change_scene(JoiningScene, self.manager, self.assets, self.sSize),
                                    center=(self.sSize[0]/2, self.sSize[1]*4.5/8))
        self.hostButton = Button(host, hostG, lambda:
                                  self.manager.change_scene(StageSelectScene, self.manager, self.assets, self.sSize, "host"),
                                    center=(self.sSize[0]/2, self.sSize[1]*5.5/8))
        self.backButton = Button(back, backG, lambda: self.manager.change_scene(MenuScene, self.manager, self.assets, self.sSize), 
                                 center=(self.sSize[0]/2, self.sSize[1]*7/8))


    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        self.practiseButton.update(mpos, mbut_j)
        self.localButton.update(mpos, mbut_j)
        self.joinButton.update(mpos, mbut_j)
        self.hostButton.update(mpos, mbut_j)
        self.backButton.update(mpos,mbut_j)

    def draw(self, screen):
        screen.blit(self.background, self.backgroundRect)
        self.practiseButton.draw(screen)
        self.localButton.draw(screen)
        self.joinButton.draw(screen)
        self.hostButton.draw(screen)
        self.backButton.draw(screen)
        
class LocalModeScene(scene):
    def __init__(self, manager, assets, sSize, stage, c1, c2):
        super().__init__(manager, assets, sSize)
        #stage and player's creation
        self.stage = StageFactory(stage, self.assets, sSize)
        #different spawn points and player numbers
        self.player1 = CharacterFactory(c1, self.assets, self.manager.controls, self.stage.getSpawnPoint(1), 1)
        self.player2 = CharacterFactory(c2, self.assets, self.manager.controls, self.stage.getSpawnPoint(2), 2)
        #stores number of wins for each player
        #index 0 is player 1 and index 1 is player 2 
        self.wins = [0,0]
        self.characters = [c1, c2]
        self.hud = HUD(self.sSize, self.assets)
    
    def checkRound(self):
        #resets both players if one player is defeated
        #if player 1 is defeated 
        if self.player1.health <=0:
            #player 2 wins incremented
            self.wins[1] +=1
            self.player1.reset()
            self.player2.reset()
            self.hud.reset()
        #if player 2 is defeated
        elif self.player2.health <= 0:
            #player 1 wins are incremented
            self.wins[0] +=1
            self.player1.reset()
            self.player2.reset()
            self.hud.reset()
        elif self.hud.update():
            #player with the lowest health loses
            if self.player1.health > self.player2.health:
                self.wins[0] +=1
                self.player1.reset()
                self.player2.reset()
            elif self.player2.health > self.player1.health:
                self.wins[1] +=1
                self.player1.reset()
                self.player2.reset()
            #if healths are equal then no wins to either
            #round is restarted
            else:
                self.player1.reset()
                self.player2.reset()
            self.hud.reset()
                
        #best of 3 system
        #if one player wins twice, they win
        if 2 in self.wins:
            #ending banner should be switched to here
            index = self.wins.index(2) 
            self.manager.change_scene(EndingBannerScene, self.manager, self.assets, self.sSize, self.stage.name, index+1, self.characters[index])

    def DeathFall(self):
        #Checks whether player is out of screen
        if self.player1.rect.bottom > self.sSize[1]:
            self.player1.health = 0
        if self.player2.rect.bottom > self.sSize[1]:
            self.player2.health = 0

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        self.player1.update(self.stage.getHitboxes(), dt, mpos, mbut, mbut_j, keys, keys_j)
        self.player2.update(self.stage.getHitboxes(), dt, mpos, mbut, mbut_j, keys, keys_j)
        #take damage functions to check for attacks
        self.player1.take_damage(self.player2)
        self.player2.take_damage(self.player1)
        #check rounds on each update
        self.checkRound()
        self.DeathFall()

    def draw(self, screen):
        self.stage.draw(screen)
        self.player1.draw(screen)
        self.player2.draw(screen)
        self.hud.draw(screen, self.player1, self.player2)

class StageIcon:
    def __init__(self, name, ID, assets, highlight, **pos_kwargs):
        #backgrounds are already scaled to the screen size
        #0.25 will work on any screen
        #mini preview not large
        self.preview = pygame.transform.scale_by(assets.getBackground(ID), 0.25)
        self.rect = self.preview.get_frect(**pos_kwargs)

        #outline will light up if mouse hover
        self.outline = pygame.Surface((self.preview.get_width() + 0.05*self.preview.get_height(), 1.05* self.preview.get_height()))
        self.orect=  self.outline.get_frect(**pos_kwargs)

        self.ID = ID
        self.name = name

        self.font = assets.getFont("PressStart2P")

        #Creates text surface and places it mid top of the mini preview outline
        self.text = self.font.render(self.name, True, (255,255,255))
        self.textR = self.text.get_frect(midbottom = self.orect.midtop)

        #for nice visual effect to change the outline
        self.colour = (0,0,0)
        self.highlight = highlight #constant
    
    def update(self, mpos, mbut_j):
        #returns true if clicked
        if self.rect.collidepoint(mpos):
            #changes colour for hover effect
            self.colour = self.highlight
            if mbut_j[0]:
                return True
        else:
            #black if no hover
            self.colour = (0,0,0)
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.orect, border_radius=5)
        screen.blit(self.preview, self.rect)
        screen.blit(self.text, self.textR)
     

class StageSelectScene(scene):
    def __init__(self, manager, assets, sSize, mode):
        super().__init__(manager, assets, sSize)
        #Sets background
        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay, so user can focus on settings
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #mode for switching scenes
        self.mode = mode

        vv = StageIcon("Volcano Valley", "volcano_valley", assets, (255, 64, 0), center = (self.sSize[0]/3, self.sSize[1]/3))
        af = StageIcon("Arctic Fracture", "arctic_fracture", assets, (102, 229, 255), center = (2*self.sSize[0]/3, self.sSize[1]/3))
        cr = StageIcon("Celestial Ruins", "celestial_ruins", assets, (245, 250, 255), center = (self.sSize[0]/2, 2*self.sSize[1]/3))
        self.icons = [vv, af, cr]



    def switchScene(self, ID):
        match self.mode:
            case "practise":
                #should be changed to character selection once made
                self.manager.change_scene(CharacterSelectScene,self.manager, self.assets, self.sSize, self.mode, ID)
            case "host":
                #should be changed to character selection once made
                self.manager.change_scene(WaitingScene, self.manager, self.assets, self.sSize, ID)
            case "local":
                self.manager.change_scene(CharacterSelectScene, self.manager, self.assets, self.sSize, self.mode, ID)

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        for icon in self.icons:
            if icon.update(mpos, mbut_j):
                self.switchScene(icon.ID)

    def draw(self, screen):
        screen.blit(self.background, self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        for icon in self.icons:
            icon.draw(screen)


class CharacterIcon:
    def __init__(self, name, assets, sSize, **pos_kwargs):
        self.name = name

        #icon files have a "_icon" at the end
        self.icon = assets.getIcon(name+"_icon")
        self.iconR = self.icon.get_frect(**pos_kwargs)

        #first frame of the idle animation will be a preview
        self.preview = assets.getAnimations(name)["idle"][0]
        self.preview = self.preview.subsurface(self.preview.get_bounding_rect())
        self.preview = pygame.transform.scale_by(self.preview, 3*assets.SF)
        self.x1 = sSize[0]/3
        #reflects around the middle of the screen of p2
        self.x2 = sSize[0] - self.x1
        #default is p1
        self.previewR = self.preview.get_frect(midbottom = (self.x1,sSize[1]))
    
    def hover(self, mpos, mbut_j):
        #retuns if the mouse is hovering over the icon
        #so that the preview can change
        if self.iconR.collidepoint(mpos):
            return True 
        
    def isPressed(self, mpos, mbut_j):
        #returns if the button is pressed
        if self.iconR.collidepoint(mpos):
            if mbut_j[0]:
                return True
    
    def draw(self, screen):
        screen.blit(self.icon, self.iconR)

    def drawPreview(self, screen , preview):
        #if the preview is for player 1
        if preview == 1:
            #change x to left side and blit
            self.previewR.centerx = self.x1
            screen.blit(self.preview, self.previewR)
        #if the preview is for player 2
        elif preview ==2:
            self.previewR.centerx = self.x2
            flip = pygame.transform.flip(self.preview, True, False)
            screen.blit(flip, self.previewR)


class CharacterSelectScene(scene):
    def __init__(self, manager, assets, sSize, mode, stage):
        super().__init__(manager, assets, sSize)
        #Sets background
        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay, so user can focus on settings
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #stores the mode and stage for switch scene
        self.stage = stage
        self.mode = mode

        #icons are manually made for each character
        self.icons = [CharacterIcon("knight", assets, sSize, center = (sSize[0]/4, sSize[1]/4)),
                 CharacterIcon("evil_wizard", assets, sSize, center = (sSize[0]*2/4, sSize[1]/4)),
                 CharacterIcon("samurai", assets,sSize, center = (3*sSize[0]/4, sSize[1]/4))
                 ]

        self.turn = 0
        #list for easy access
        #2 values, for player 1 and 2
        self.selected = [None, None]
        #confirmed if the player presses on the icon
        self.confirmed = [None, None]

    def switchScene(self):
        match self.mode:
            case "practise":
                #should be changed to character selection once made
                self.manager.change_scene(PractiseScene,self.manager, self.assets, self.sSize, 
                                          self.stage, self.confirmed[0].name)
            case "local":
                #should be changed to character selection once made
                self.manager.change_scene(LocalModeScene, self.manager, self.assets, self.sSize, 
                                          self.stage, self.confirmed[0].name , self.confirmed[1].name)


    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        for icon in self.icons:
            #if hover then change the selected on that player's turn
            if icon.hover(mpos, mbut_j) == True:
                self.selected[self.turn] = icon
            #if pressed then confirm the choice
            if icon.isPressed(mpos, mbut_j) == True:
                self.confirmed[self.turn] = icon
                #if single player then one confirm is enough
                if self.mode == "practise":
                    self.switchScene()
                    return
                #otherwise second player turn
                self.turn = 1 
        
        #if all choices confirmed
        if None not in self.confirmed:
            self.switchScene()


    def draw(self,screen ):
        screen.blit(self.background, self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        for icon in self.icons:
            icon.draw(screen)
        
        #will only draw the selected if a there is no confirmed yet
        #lists are 0-indexed
        if self.confirmed[0] != None:
            self.confirmed[0].drawPreview(screen, 1)
        elif self.selected[0] != None:
            self.selected[0].drawPreview(screen, 1)


        if self.confirmed[1] != None:
            self.confirmed[1].drawPreview(screen,2)
        elif self.selected[1] != None:
            self.selected[1].drawPreview(screen, 2)



class KeybindWidget:
    def __init__(self, font, size, action, key , **pos_kwargs):
        #sets the outline box which contains the key and action
        self.bg = pygame.Surface(size)
        self.bg.fill((100,100,100))
        self.bgr = self.bg.get_frect(**pos_kwargs)

        #default font
        self.font = font
        #highlight colour
        self.orange = (222, 156, 42)
        
        #sets action and action position
        self.action = action
        self.actionI = self.font.render(self.action, True, (0,0,0))
        self.actionR = self.actionI.get_frect(topleft = self.bgr.topleft)

        #Key in both text and pygame code format
        self.key = key
        self.keyText = pygame.key.name(self.key)

        self.keyI = self.font.render(self.keyText, True, (0,0,0))
        self.keyR  = self.keyI.get_frect(topright = self.bgr.topright)
    
    def changeKey(self, key):
        #Supports both pygame key and string
        if isinstance(key, str):
            #If string then sets text first
            self.keyText = key
            #Then retrieves the code
            self.key = pygame.key.key_code(self.keyText)
        else:
            #Otherwise set code first
            self.key = key
            #Then retrieve text
            self.keyText = pygame.key.name(self.key)

        #Must rerender to change colour back
        #Each time it is set, colour changes back to white
        self.keyI = self.font.render(self.keyText, True, (0,0,0))
        self.keyR  = self.keyI.get_frect(topright = self.bgr.topright)
    
    def changeKeyColour(self, colour):
        #Changes colour of keybind
        self.keyI = self.font.render(self.keyText, True, colour)
        self.keyR  = self.keyI.get_frect(topright = self.bgr.topright)
    
    def changeActionColour(self, colour):
        #Changes the description of the action
        self.actionI = self.font.render(self.action, True, colour)
        self.actionR = self.actionI.get_frect(topleft = self.bgr.topleft)

    def update(self, mpos, mbut_j):
        #If mouse hover
        if self.bgr.collidepoint(mpos): 
            #Activate orange highlight
            self.changeActionColour(self.orange)

            #If press too
            if mbut_j[0]:
                #Set key to ? to change later
                #Highlight so user can see
                self.changeKey("?")
                self.changeKeyColour(self.orange)
                #True for press
                return True 
        else:
            #No highlight if no hover
            self.changeActionColour((0,0,0))
        
        #No press
        return False

    def draw(self, screen):
        #draws background, action on the left, key on the right
        screen.blit(self.bg, self.bgr)
        screen.blit(self.actionI, self.actionR)
        screen.blit(self.keyI, self.keyR)

class SettingsScene(scene):
    def __init__(self, manager, assets, sSize):
        super().__init__(manager, assets, sSize)
        #Sets background
        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay, so user can focus on settings
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #controls is a dictionary: {"P1 Right": blah...}
        self.controls = self.manager.controls
        self.widgets = []

        #Default font for actions
        self.font = self.assets.getFont("Cinzel-Regular")

        #Sets active action and listening for handle events function
        self.activeAction = None
        self.listening = False

        for i, (action, key) in enumerate(self.controls.items()):
            #i is used for determining y position of widgets
            #screen is divided into 16 for positions and sizes

            #size for the widget background
            xSize = self.sSize[0]/16*(6)
            ySize = self.sSize[1]/32
            size = (xSize, ySize)
            
            #P1 controls go on the left of the screen
            if "P1" in action:
                pos = (1/16*self.sSize[0], (i+4)*self.sSize[1]/16)

            elif "P2" in action:
                #P2 starts at index 5
                j = i-5
                #x changed
                pos = (9/16*self.sSize[0], (j+4)*self.sSize[1]/16)
            
            #creates and adds widget, based on calculated positions/sizes, to list
            self.widgets.append(KeybindWidget(self.font, size, action, key, topleft = pos))

        #Back button        
        back, backG = self.assets.getButton("back")
        self.backButton  = Button(back,backG, lambda: self.manager.change_scene(MenuScene, self.manager, self.assets, self.sSize),
                                  center = (self.sSize[0]/2, self.sSize[1]*0.9))
    
    def handle_events(self, events):
        #Basic inherited function for all scenes to check whether user closes the window
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            #If user has pressed a key and settings is in listening mode
            if event.type == pygame.KEYDOWN and self.listening:
                #Change controls to that key
                self.manager.controls[self.activeAction] = event.key
                for widget in self.widgets:
                    #Searches for the current action being changed
                    if widget.action == self.activeAction:
                        #Changes key to display to user
                        widget.changeKey(event.key)
                        break #Stops loop
                #Resets listening and active action
                self.listening = False
                self.activeAction = None
            

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        for widget in self.widgets:
            #Updates each widget
            if not self.listening:
                if widget.update(mpos, mbut_j):
                    #If widget pressed then, 
                    #turns on listening
                    self.activeAction = widget.action
                    self.listening = True

        self.backButton.update(mpos,mbut)
    
    def draw(self,screen):
        screen.blit(self.background, self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        #Draws each widget
        for widget in self.widgets:
            widget.draw(screen)
        self.backButton.draw(screen)

class PractiseScene(scene):
    def __init__(self, manager, assets, sSize, stage, character):
        super().__init__(manager, assets, sSize)
        self.stage = StageFactory(stage, self.assets, self.sSize)
        self.Player1 = CharacterFactory(character, self.assets,self.manager.controls, self.stage.getSpawnPoint(1), 1)

        #back button to joining menu, in top left corner
        exit,exitG = self.assets.getButton("exit")
        self.exitButton = Button(exit, exitG, lambda: self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize), 
                                 topleft=(self.sSize[0]/128, self.sSize[1]/128))

        #characters button to character selection menu, topleft corner
        characters, charactersG = self.assets.getButton("characters")
        self.charactersButton = Button(characters, charactersG, lambda: 
                                       self.manager.change_scene(CharacterSelectScene, self.manager, self.assets, self.sSize,
                                                                                                "practise", stage), 
                                       topleft = (exit.get_width() + (self.sSize[0]/100), self.sSize[1]/128))

    
    def update(self, dt, mpos, mbut, mbut_j, keys, keys_j):
        self.Player1.update(self.stage.getHitboxes(), dt, mpos, mbut, mbut_j, keys, keys_j)
        self.exitButton.update(mpos, mbut_j)
        self.charactersButton.update(mpos, mbut_j)
        #removes deaths
        self.noDeath()

    def draw(self, screen):
        self.stage.draw(screen)
        self.Player1.draw(screen)
        self.exitButton.draw(screen)
        self.charactersButton.draw(screen)

    def noDeath(self):
        #Checks whether player is out of screen
        if self.Player1.rect.bottom > self.sSize[1]:
            self.Player1.rect.midbottom = self.stage.getSpawnPoint(1)


def checkLANErr(scene, response):
    '''This function works on these assumptions:
    -network send returns ["Error"] if there is
    -the scenes that use this function have a server, manager,
    assets, and sSize attribute'''
    if response == ["Error"]:
        #reset the server too
        scene.server.shutdown()
        scene.manager.server =server()
        #change scenes to the play menu
        scene.manager.change_scene(PlayMenuScene, scene.manager, scene.assets, scene.sSize)
        #error identified
        return True

    return False



class LANgame(scene):
    #pNumber should be 1 for host and 2 for join
    #this will be used to identify whether to run code for the server
    #and for init
    def __init__(self, manager, assets, sSize, pNumber):
        super().__init__(manager, assets, sSize)
        self.network = self.manager.network
        self.server = self.manager.server
        self.hud = HUD(self.sSize, self.assets)
        
        self.pNumber = pNumber
        #other player number used for indexing
        self.opNumber = 1 if pNumber == 2 else 2 
        self.players = [None, None]
        
        #gets the stage from the server
        stage = self.network.send(["request_stage"])[0]
        #check for errors to reset
        if checkLANErr(self, stage):
            return

        self.stage = StageFactory(stage, assets, sSize)
        
        #should return [home player name, opponent player name]
        players = self.network.send(["request_all_character_selections"])
        if checkLANErr(self, players):
            return
        self.players[self.pNumber-1] = CharacterFactory(players[0], assets, self.manager.controls, self.stage.getSpawnPoint(pNumber), pNumber)
        self.players[self.opNumber-1] = CharacterFactory(players[1], assets, self.manager.controls, self.stage.getSpawnPoint(self.opNumber), self.opNumber)
        
        #resets the hud, incase there was a delay
        self.hud.reset()

    def DeathFall(self):
        # Checks whether player is out of screen
        if self.players[0].rect.bottom > self.sSize[1]:
            self.players[0].health = 0
        if self.players[1].rect.bottom > self.sSize[1]:
            self.players[1].health = 0

    def set_data(self, dt):
        other = self.network.send(["game", self.players[self.pNumber-1].rect.midbottom,
                                   self.players[self.pNumber-1].animation_state,
                                   self.players[self.pNumber-1].current_animation.getFrameNumber(),
                                   self.players[self.pNumber-1].facing_left,
                                   self.players[self.pNumber-1].health])
        #check for LAN errors
        if checkLANErr(self, other):
            return

        self.players[self.opNumber - 1].set_lan_data(dt, other["position"], other["animation_state"], other["frame"], other["facing_left"], other["health"])
        self.wins = other["wins"]

        if other["status"] == "active":
            pass
        elif other["status"] == "new_round":
            self.players[self.pNumber-1].reset()
            self.hud.reset()
        else:
            #switch scenes to the ending banner
            #use the "victory_1" to get the player number
            player_number = int(other["status"][-1])
            #extract name
            name = self.players[player_number-1].name
            self.manager.change_scene(EndingBannerScene, self.manager, self.assets, self.sSize, self.stage.name, player_number, name)


    def update(self, dt, mpos, mbut, mbut_j, keys, keys_j):

        status = self.network.send(["request_lan_status"])
        if not status[0]:
            #reset all network attributes
            self.network.reset()
            self.server.shutdown()
            self.manager.server = server()
            self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize)
            return

        self.players[self.pNumber-1].update(self.stage.getHitboxes(), dt, mpos, mbut, mbut_j, keys, keys_j)
        self.set_data(dt)

        #if both players in the game
        if not(None in self.players):
            #check if other player has attacked successfully
            self.players[self.pNumber-1].take_damage(self.players[self.opNumber-1]) 
            self.DeathFall()
            #check who wins

            
    def draw(self,screen):
        self.stage.draw(screen)

        self.players[self.pNumber-1].draw(screen)
        self.players[self.opNumber-1].draw(screen)

        if not(None in self.players):
            self.hud.draw(screen, self.players[0], self.players[1])


class WaitingScene(scene):
    def __init__(self, manager, assets, sSize, stageID):
        super().__init__(manager, assets, sSize)
        #sets the font for the waiting text
        self.font = self.assets.loadFont("Cinzel-Regular.otf", 67)
        #Sets background
        self.background = self.assets.getBackground(stageID)
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay, reduces the background noise from colours 
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #the text at the bottom left
        self.text = self.font.render("Waiting", True, (255,255,255))
        self.textR  = self.text.get_frect(bottomleft = self.backgroundRect.bottomleft)
        #number of dots after waiting text, every second
        self.nDots = 0

        self.stageID = stageID
        self.init_connection()
    
    def init_connection(self):
        self.network = self.manager.network
        self.server = self.manager.server

        #only the stage has been picked
        status = self.server.start(self.stageID)
        #if there is an error with the server starting
        if status[0] == "Error":
            #reset all network attributes
            self.network.reset()
            self.server.shutdown()
            self.manager.server = server()
            self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize)
            return

        self.network.connect(self.server.addr)

    def update(self, dt, mpos, mbut, mbut_j, keys, keys_j):
        #check on whether a player has joined
        status = self.network.send(["initH"])
        if checkLANErr(self, status):
            return

        if status[0] == "ready":
            self.manager.change_scene(CharacterSelectSceneLAN, self.manager, self.assets, self.sSize, "host")
        elif status[0] == "waiting":
            pass
        #only one of two responses should be given
        else:
            self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize)

        #possible outputs are 0,1,2,3
        #time is in seconds, so it will switch through the numbers
        #every second, max of 3 dots
        self.nDots = int(time.time())%4
        #rerender the text with nDots amount of nDots
        self.text = self.font.render("Waiting" + (self.nDots*"."), True, (255,255,255))
        self.textR  = self.text.get_frect(bottomleft = self.backgroundRect.bottomleft)

    def draw(self,screen):
        #draws all the elements
        screen.blit(self.background,self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        screen.blit(self.text, self.textR)

 
class CharacterSelectSceneLAN(CharacterSelectScene):
    def __init__(self, manager, assets, sSize, mode):
        super().__init__(manager, assets, sSize, mode, None)
        #The network will ALREADY be connected at this point, from the waiting scene
        self.network = self.manager.network
        self.server = self.manager.server

        #sets the home player number and opponent player number
        self.pNumber = 1 if mode == "host" else 2
        self.opNumber = 2 if mode == "host" else 1

        #splitting from a list format is better
        self.selected = None
        self.confirmed = None
        #choice will be false once character is confirmed
        self.choice = True

        #stores the opponent selected/confirmed for drawing
        self.opSelected = None
        self.opConfirmed = None

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j): 

        status = self.network.send(["request_lan_status"])
        if not status[0]:
            #reset all network attributes
            self.network.reset()
            self.server.shutdown()
            self.manager.server = server()
            self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize)
            return

        #CHARACTER SELECTION FOR HOME PLAYER
        if self.choice:
            for icon in self.icons:

                #if hover then change the selected on that player's turn
                if icon.hover(mpos, mbut_j) == True:
                    self.selected = icon

                #if pressed then confirm the choice
                if icon.isPressed(mpos, mbut_j) == True:
                    self.confirmed = icon
                    #once confirmed, the user shouldn't choose
                    self.choice = False

        #get selected/confirmed from the opponent
        self.getOp()
    
        status = self.network.send(["request_character_status"])
        if checkLANErr(self, status):
            return

        if status == ["ongoing"]:
            pass
        elif status == ["start"]:
            # player number should change how the lan game class interprets the confirmed characters
            self.manager.change_scene(LANgame, self.manager, self.assets, self.sSize, self.pNumber)

    #gets opponent selections
    def getOp(self):
        #extracts the names of selected/confirmed characters
        selected = self.selected.name if self.selected != None else None
        confirmed = self.confirmed.name if self.confirmed != None else None

        #retrieves the opponent selections and confirmations
        #server should send ["CHARACTER_NAME", None]
        info = self.network.send(["request_op_character_selections", selected, confirmed])
        if checkLANErr(self, info):
            return 
        opConfirmed = info[0]
        opSelected = info[1]

        #one for loop for both confirmed and selected
        #more efficient
        for icon in self.icons:
            if icon.name == opSelected:
                self.opSelected = icon
            if icon.name == opConfirmed:
                self.opConfirmed = icon

    def draw(self,screen ):
        screen.blit(self.background, self.backgroundRect)

        #draws the opponents selections under the overlay
        #so the players know which character they are
        if self.opConfirmed != None:
            self.opConfirmed.drawPreview(screen, self.opNumber)
        elif self.opSelected != None:
            self.opSelected.drawPreview(screen, self.opNumber)

        screen.blit(self.overlay, self.overlayR)
        for icon in self.icons:
            icon.draw(screen)

        if self.confirmed != None:
            self.confirmed.drawPreview(screen,self.pNumber)
        elif self.selected != None:
            self.selected.drawPreview(screen, self.pNumber)

class widget:
    def __init__(self, font, text, addr, size, **pos_kwargs):
        #sets the outline box which contains the key and action
        self.bg = pygame.Surface(size)
        self.bg.fill((100,100,100))
        self.bgr = self.bg.get_frect(**pos_kwargs)

        #font for text
        self.font = font
        self.addr = addr
        
        #sets text
        self.text = text
        self.textI = self.font.render(text, True, (0,0,0))
        self.textR = self.textI.get_frect(topleft = self.bgr.topleft)
    
    def update(self, mpos, mbut_j):
        #If mouse hover
        if self.bgr.collidepoint(mpos): 
            #If press too
            if mbut_j[0]:
                #True for press
                return True 
        #No press
        return False

    def draw(self, screen):
        #draws background, action on the left, key on the right
        screen.blit(self.bg, self.bgr)
        screen.blit(self.textI, self.textR)

class JoiningScene(scene):
    def __init__(self, manager, assets, sSize):
        super().__init__(manager, assets, sSize)     
        #Sets background
        self.background = self.assets.getBackground("start_menu")
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))
        
        #network attribute for discovering games
        self.network = self.manager.network
        
        #list for storing all widgets
        self.widgets = []
        #size for each widget
        self.widgetSize = (self.sSize[0]/3, self.sSize[1]/28)


        self.font = self.assets.loadFont("Cinzel-Regular.otf", 24)

        back,backG = self.assets.getButton("back")
        self.backButton = Button(back, backG, lambda: self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize), 
                                 center=(self.sSize[0]/2, self.sSize[1]*7/8))

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        #so back button can be clicked
        self.backButton.update(mpos, mbut_j)

        #if the last game discovery is over
        if not self.network.discovering:
            #retrieves the results of the last
            discovered = self.network.discovered
            
            self.widgets = []
            for i, game in enumerate(discovered):
                #stage name is stored in index 0 
                stage = game[0]
                addr  = game[1]
                #addr[1] is always 9999
                #get the RIGHT port
                port = stage[stage.find(".")+1:]
                #keep the ip but replace the port
                addr = (addr[0], int(port))
                #make a new widget for each game
                self.widgets.append(widget(self.font, stage, addr, self.widgetSize, center = (self.sSize[0]/2, (i+4)*self.sSize[1]/8)))

            #needs to run on a seperate thread to not freeze the game
            discover_games = threading.Thread(target=self.network.discover_games, args=(), daemon=True)
            discover_games.start()

        #checks if a player clicked a game
        for game in self.widgets:
            if game.update(mpos, mbut_j):
                #connect using the addr attribute in the widget
                self.network.connect(game.addr)
                #then changes scenes to the character select
                self.manager.change_scene(CharacterSelectSceneLAN, self.manager, self.assets, self.sSize, "join")


    def draw(self, screen):
        screen.blit(self.background, self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        self.backButton.draw(screen)

        for widget in self.widgets:
            widget.draw(screen)



class EndingBannerScene(scene):
    def __init__(self, manager, assets, sSize, stage, pNumber, character):
        super().__init__(manager, assets, sSize)
        #Sets background
        self.background = self.assets.getBackground(stage)
        self.backgroundRect= self.background.get_frect(topleft = (0,0))

        #Transparent darker overlay
        self.overlay= pygame.Surface(self.sSize, pygame.SRCALPHA)
        self.overlay.fill((0,0,0,150))
        self.overlayR = self.overlay.get_frect(topleft=(0,0))

        #gets the first frame of the idle animation
        self.image = self.assets.getAnimations(character)["idle"][0]
        self.preview = self.image.subsurface(self.image.get_bounding_rect())
        self.preview = pygame.transform.scale_by(self.preview, 3*assets.SF)

        #places the feet of the character at the midbottom of the screen
        self.previewR = self.preview.get_frect(midbottom = (self.sSize[0]/2, self.sSize[1]))


        #loads font for custom size
        self.font = self.assets.loadFont("PressStart2P.ttf", 32)
        #specfies the text according to player number
        text = f"Player {pNumber} wins!"
        self.text = self.font.render(text,  True, (255,255,255))
        self.textR = self.text.get_frect(center = (self.sSize[0]/2, self.sSize[1]/3))

        back,backG = self.assets.getButton("back")
        #places back button in the topleft corner with a slight square offset
        self.backButton = Button(back, backG, lambda: self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize), 
                                 topleft=(self.sSize[0]/128, self.sSize[1]/128))

        self.duration = 3
        self.start = time.time()

    def update(self, dt, mpos, mbut,mbut_j, keys, keys_j):
        #if the duration is up
        if time.time() - self.start >= self.duration:
            self.manager.change_scene(PlayMenuScene, self.manager, self.assets, self.sSize)

        self.backButton.update(mpos, mbut_j)

    def draw(self, screen):
        screen.blit(self.background, self.backgroundRect)
        screen.blit(self.overlay, self.overlayR)
        self.backButton.draw(screen)

        screen.blit(self.text, self.textR)
        screen.blit(self.preview, self.previewR)


