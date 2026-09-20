import os
import pygame


class assets:
    def __init__(self, screenSize, buttonSF):
        #Sets base to absolute path of the py file
        self.base = os.path.dirname(os.path.abspath(__file__)) 
        #Assets folder path
        self.path = os.path.join(self.base, "assets")
        
        #Backgrounds,buttons folders path
        self.backgrounds_path = os.path.join(self.path, "backgrounds")
        self.buttons_path = os.path.join(self.path, "buttons")
        self.loading_path = os.path.join(self.path, "loading")
        self.fonts_path = os.path.join(self.path, "fonts")
        self.stages_path = os.path.join(self.path, "stages")
        self.characters_path  = os.path.join(self.path, "characters")
        self.icons_path = os.path.join(self.path, "icons")

        #Specifies screen size and button size for image scaling
        self.screenSize = screenSize
        self.buttonSF = buttonSF

        #development was in 1280x720
        #scale factor for any screen size
        self.SF = min(self.screenSize[0]/1280, self.screenSize[1]/720)

        #assets dictionaries seperated by type eg backgrounds, buttons
        self.backgrounds = {}
        self.buttons = {}
        self.fonts = {}
        self.platforms = {}
        self.characters = {}
        self.icons = {}

        #Total number of images that need to be loaded, progress check (for loading bar)
        #excludes loading screen assets, as they wont be loaded in the load method
        self.counter = self.count(self.path) - self.count(self.loading_path) 
        self.progressCounter = 0

        self.loaded = False

    def ratio(self):
        #Returns loading progress as a ratio to be used for loading bar width
        return self.progressCounter/self.counter

    def status(self):
        #Checks if all assets are loaded
        return self.loaded 

    def count(self, path):
        #Sets file count to 0
        counter = 0
        #For each entry in the folder
        for file in os.listdir(path):
            #Check if its a file
            if os.path.isfile(os.path.join(path,file)):
                #Increment counter if it is a file
                counter+=1
            else:
                #If its a folder recurse and count how many in that folder to add
                counter += self.count(os.path.join(path, file))
        #Once its finished counting everything in asset folder, return counter
        return counter
    
    def getLoadingScreen(self):
        #Returns processed loading screen assets, for displaying to the user
        #Removes any transparent pixels, ready for scaling
        LoadingScreenBackground = pygame.image.load(os.path.join(self.loading_path, "loading_screen.png")).convert_alpha()
        LoadingScreenBackground = pygame.transform.scale(LoadingScreenBackground, self.screenSize)

        LoadingBar = pygame.image.load(os.path.join(self.loading_path, "loading_bar.png")).convert_alpha()
        LoadingBar = LoadingBar.subsurface(LoadingBar.get_bounding_rect())

        Bar = pygame.image.load(os.path.join(self.loading_path, "gold_bar.png")).convert_alpha()
        Bar = Bar.subsurface(Bar.get_bounding_rect())
        
        
        return LoadingScreenBackground, LoadingBar, Bar

    
    def load_buttons(self):
            for file in os.listdir(self.buttons_path):
                #All buttons are png
                #Allows transparent pixels, then removes them
                image = pygame.image.load(os.path.join(self.buttons_path, file)).convert_alpha()
                image = image.subsurface(image.get_bounding_rect())
                #Scales using button size
                image = pygame.transform.smoothscale_by(image, self.buttonSF*self.SF)
                
                #scales to any screen size
                #image = pygame.transform.smoothscale_by(image, self.SF)

                name = file[:file.find(".")]
                self.buttons[name] = image

                self.progressCounter+=1
    
    def load_icons(self):
        #for all icons in the folder
        for file in os.listdir(self.icons_path):
            #all icons are png
            icon = pygame.image.load(os.path.join(self.icons_path, file)).convert_alpha()
            #*by SF to make icon sizes suitable for all screen sizes
            icon = pygame.transform.scale_by(icon, 0.1*self.SF)

            name = file[:file.find(".")]
            self.icons[name] = icon
    
    def load_fonts(self):
        for file in os.listdir(self.fonts_path):
            font = pygame.font.Font(os.path.join(self.fonts_path, file), 16)
            name = file[:file.find(".")]
            self.fonts[name] = font

            self.progressCounter+=1
            
    def load_backgrounds(self):
        #Goes through each file in backgrounds folder
        for file in os.listdir(self.backgrounds_path):
            #if image is png
            if file[-3:] == "png":
                #Allows transparent pixels
                image = pygame.image.load(os.path.join(self.backgrounds_path, file)).convert_alpha() 
            else:
                image = pygame.image.load(os.path.join(self.backgrounds_path, file)) 
            image = pygame.transform.smoothscale(image, self.screenSize)

            #Removes file extension for easy storing
            name = file[:file.find(".")]
            #Stores each image in dictionary
            self.backgrounds[name] = image

            self.progressCounter+=1 #Increases loaded images counter by 1

    def load_stages(self):
        self.load_volcano_valley()
        self.load_celestial_ruins()
        self.load_arctic_fracture()
    
    def load(self):
        self.load_backgrounds()
        self.load_buttons()
        self.load_fonts()
        self.load_stages()
        self.load_characters()
        self.load_icons()
        
        self.loaded = True

    def load_volcano_valley(self):
        #The path for this function is the volcano valley folder inside the stages folder
        path = os.path.join(self.stages_path, "volcano_valley")
        self.platforms["volcano_valley"] = {} 

        #Goes through each platform
        for file in os.listdir(path):
            #Removes file extension for easy storing
            name = file[:file.find(".")]
            platform = pygame.image.load(os.path.join(path, file)).convert_alpha() 
            platform = platform.subsurface(platform.get_bounding_rect()) #removes transparent pixels
            size = platform.get_size()
            ratio = size[0]/size[1]
            
            if name == "platform1":
                platform = pygame.transform.smoothscale(platform, (self.screenSize[1]/2*ratio, self.screenSize[1]/2)) #half the screen

            #Stores each platform in dictionary
            self.platforms["volcano_valley"][name] = platform 

            self.progressCounter+=1 #Increases loaded images counter by 1
    
    def load_celestial_ruins(self):
        #The path for this function is the celestial ruins folder inside the stages folder
        path = os.path.join(self.stages_path, "celestial_ruins")
        self.platforms["celestial_ruins"] = {} 

        #Goes through each platform
        for file in os.listdir(path):
            #Removes file extension for easy storing
            name = file[:file.find(".")]
            platform = pygame.image.load(os.path.join(path, file)).convert_alpha() 
            platform = platform.subsurface(platform.get_bounding_rect()) #removes transparent pixels
            size = platform.get_size()
            ratio = size[0]/size[1]
            
            if name == "platform1":
                platform = pygame.transform.smoothscale(platform, (self.screenSize[1]/2*ratio, self.screenSize[1]/2)) #half the screen

            #Stores each platform in dictionary
            self.platforms["celestial_ruins"][name] = platform 

            self.progressCounter+=1 #Increases loaded images counter by 1

    def load_arctic_fracture(self):
        #The path for this function is the celestial ruins folder inside the stages folder
        path = os.path.join(self.stages_path, "arctic_fracture")
        self.platforms["arctic_fracture"] = {} 

        #Goes through each platform
        for file in os.listdir(path):
            #Removes file extension for easy storing
            name = file[:file.find(".")]
            platform = pygame.image.load(os.path.join(path, file)).convert_alpha() 
            platform = platform.subsurface(platform.get_bounding_rect()) #removes transparent pixels
            size = platform.get_size()
            ratio = size[0]/size[1]
            
            if name == "platform1":
                platform = pygame.transform.smoothscale(platform, (self.screenSize[1]/4*ratio, self.screenSize[1]/4)) #half the screen

            #Stores each platform in dictionary
            self.platforms["arctic_fracture"][name] = platform 

            self.progressCounter+=1 #Increases loaded images counter by 1

    def getIcon(self, name):
        return self.icons[name]

    def getFont(self, name):
        return self.fonts[name]

    def loadFont(self, name , size):
        font = pygame.font.Font(os.path.join(self.fonts_path, name), size)
        return font

    def getButton(self, text):
        #Returns normal button and glowing button
        return self.buttons[text+"-button"], self.buttons[text+"-button-g"]

    def getBackground(self, name):
        return self.backgrounds[name]

    def getPlatforms(self, name):
        return [self.platforms[name][key] for key in self.platforms[name]]

    def getAnimations(self, name):
        #returns all animations of specified character
        return self.characters[name]["animations"]
    
    def load_characters(self):
        #knight asset has frame size of 96x84, test out oSizes
        #multiply by sf to scale up to any screen size
        self.load_character("knight", (96,84), 2*self.SF)
        self.load_character("evil_wizard", (250,250), 1.5*self.SF)
        self.load_character("samurai", (200,200), 1.75*self.SF)
    
    def load_character(self, name, fSize, sf):
        #name of the character 
        #fSize = size of each frame in the spritesheets
        #oSize = size that the character should get scaled to

        path = os.path.join(self.characters_path, name)
        #inits character and its animations in the dict 
        self.characters[name] = {}
        self.characters[name]["animations"] ={}

        #for each type of animation (should have its own folder)
        for folder in os.listdir(path):
            #sets up a list for each animation (idle, attack etc)
            self.characters[name]["animations"][folder] = []
            #links to the actual folder
            animation = os.path.join(path, folder)

            #just incase there are multiple spritesheets seperate images for each frame
            #a for loop is used
            for spritesheet in os.listdir(animation): 
                #loads the spritesheet after joining paths
                ss = pygame.image.load(os.path.join(animation, spritesheet))
                #retrieves size for splicing
                size = ss.get_size()

                #checks how many rows of frames exist 
                for j in range(size[1]//fSize[1]):
                    #y is the row
                    y = j*fSize[1]

                    #checks how many columns of frames exist
                    for i in range(size[0]//fSize[0]):
                        #x is the column
                        x = i*fSize[0]
                    
                        #splicing and storing
                        frame = ss.subsurface((x,y), fSize)
                        #line below commented out
                        #cutout = frame.subsurface(frame.get_bounding_rect())

                        #scale by takes 2 inputs, image and scale factor ( 1 value )
                        scaled = pygame.transform.scale_by(frame, sf)
                        self.characters[name]["animations"][folder].append(scaled)





