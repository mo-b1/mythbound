import pygame
from animations import animation

class Character:
    def __init__(self, name, assets, controls, spawn_point, number, recovery1 = 2, recovery2 = 2):
        self.name = name
        self.assets = assets

        #Player number is used for controls
        self.controls = controls
        self.number = number

        #loads all the animation images 
        #puts each one into its own class
        self.load_animations()
        self.maxHealth = 100
        self.health = 100
        
        self.animation_state = "idle"
        self.current_animation = self.animations[self.animation_state]

        #frame status
        self.invincible = False
        self.recovery = 0
        self.attacking = False
        self.knockback = False
        
        self.busy = False

        self.direction = pygame.math.Vector2(1,0)
        self.on_ground = True #Starts on platform
        self.gravity = 0
        self.speed = 200 #------------needs to be tested------------
        self.max_fall_speed = 800 #------------needs to be tested------------

        #player 2 should face left as they will be on the right
        self.facing_left = False if number == 1 else True
        self.spawn_point = spawn_point

        #attack recoveries- changable
        self.recovery1 = recovery1
        self.recovery2 = recovery2

        #initilizes the image and rect after the setup
        self.image = self.current_animation.getFrame(self.facing_left)
        self.rect = self.image.get_bounding_rect()
        self.rect.midbottom = self.spawn_point

        self.attack_use = 0

        self.previous_state = "idle"
    
    def set_lan_data(self, dt, position, animation_state, frame, facing_left, health):
        #sets all data as if a player is playing on local pc
        self.rect.midbottom = position
        self.previous_state = self.animation_state
        self.animation_state = animation_state
       
        #if player has JUST attacked
        if ("attack" not in self.previous_state) and ("attack" in self.animation_state):
            self.attack_use = 1

        self.current_animation = self.animations[self.animation_state]
        self.current_animation.SetFrame(frame)
        self.facing_left = facing_left
        self.image = self.current_animation.getFrame(facing_left)

        self.health = health
        self.updateStatus(dt)



    def draw(self, screen):
        #Draws character to screen
        rect = self.image.get_frect(center = self.rect.center)
        screen.blit(self.image, rect)
    
    def update(self, platforms, dt, mpos, mbut, mbut_j, keys, keys_j):
        #move function checks movement/attack keys and changes animations accordingly
        self.moveV(platforms, dt, keys_j) 
        self.moveH(platforms, dt, keys)       
        self.attack(keys_j)
        #needs to be updated after every move function call
        self.current_animation = self.animations[self.animation_state]        

        #updates animation and statuses
        self.updateStatus(dt)

        #updates the image and rect
        self.image = self.current_animation.getFrame(self.facing_left)

    def updateStatus(self, dt):
        #get frame status
        self.invincible = self.current_animation.getIstatus()
        self.attacking = self.current_animation.getAstatus()

        #if animation is finished, character is not busy
        if self.current_animation.update(dt) == True:
            self.busy = False
            self.animation_state = "idle"
        else:
            #otherwise get frame status to check
            self.busy = self.current_animation.getBstatus()
        
        #Allows the player to recover from attacks
        self.Recover()

    def attack(self, keys_j):
        #if player has recovered
        if self.recovery == 0 and self.on_ground == True and not self.busy:
            if keys_j[self.controls[f"P{self.number} Light Attack"]]:
                #attack, lock animation and set recovery
                self.animation_state = "attack1"
                self.attack_use = 1
                self.SetRecover1()
            elif keys_j[self.controls[f"P{self.number} Heavy Attack"]]:
                self.animation_state = "attack2"
                self.attack_use = 1
                self.SetRecover2()
    
    def moveH(self, platforms, dt, keys):
        #Player can move if locked or knockedback
        #returns if any are true
        if self.knockback or (self.busy and self.animation_state != "jump"):
            return
         

        #keys not keys_j --> movement keys can be held
        #move right
        if keys[self.controls[f"P{self.number} Right"]]:
            self.direction = pygame.math.Vector2(1,0)
            self.facing_left = False #Character moving right
            if self.on_ground:
                self.animation_state = "run"
        #move left
        elif keys[self.controls[f"P{self.number} Left"]]:
            self.direction = pygame.math.Vector2(-1,0)
            self.facing_left = True #Character moving left
            if self.on_ground:
                self.animation_state = "run"
        #otherwise idle
        else:
            self.direction = pygame.math.Vector2(0,0)
            if self.on_ground and (self.animation_state != "attack1" and self.animation_state != "attack2"):
                self.animation_state = "idle"
                self.animations["jump"].reset()

        #applies horizontal movement and gravity
        self.rect.center += self.direction * self.speed * dt 
        self.CollideHorizontal(platforms)

    def moveV(self, platforms, dt, keys_j):
        #To pull a player down after jump
        self.gravity+=800*dt #--------------needs to be tested---------------

        #jump logic
        if keys_j[self.controls[f"P{self.number} Jump"]] and self.on_ground == True:
            self.gravity = -400 #upward force for jumping
            self.animation_state = "jump" #start jump animation 
            self.on_ground = False #no longer on the ground
            self.busy = True  #lock

        self.rect.centery += min(self.max_fall_speed, self.gravity) * dt
        self.CollideVertical(platforms)        
        #DOCUEMENT THIS AND THE RECOVERY CHANGES

    def take_damage(self, player):
        #if not invincible and the opponent is attacking
        if player.attacking and not self.invincible:
            if player.attack_use:
                #mask2 is the opponent
                mask2 = pygame.mask.from_surface(player.image)
                me = pygame.mask.from_surface(self.image)
                #need to center the masks perfectly on top of the images
                #the images are centered on the rects, the masks are the same size so
                #center them on rects too
                meIR = self.image.get_frect(center = self.rect.center)  
                otherIR = player.image.get_frect(center = player.rect.center)
                #offset is distance from me to the player
                # AB is B-A
                offset = (otherIR.x-meIR.x, otherIR.y-meIR.y)
                #if the opponent collides 
                if me.overlap(mask2, offset):
                    #value needs to be edited for heavy and light attacks
                    if player.animation_state == "attack1":
                        #light attacks take 8
                        self.health -= 8
                    elif player.animation_state == "attack2":
                        #heavy attacks take 15
                        self.health -= 15
                    #reset attack use
                    player.attack_use = 0

    
    def reset(self):
        #SIMPLE RESET FUNCTION FOR ROUNDS
        for animation in self.animations:
            self.animations[animation].reset()
        self.health = 100
        self.animation_state = "idle"
        self.current_animation = self.animations[self.animation_state]
        self.invincible = False
        self.recovery = 0
        self.attacking = False
        self.knockback = False
        self.busy = False
        self.on_ground = True #Starts on platform
        self.gravity = 0
        #player 2 should face left as they will be on the right
        self.facing_left = False if self.number == 1 else True
        #initilizes the image and rect after the setup
        self.image = self.current_animation.getFrame(self.facing_left)
        self.rect.midbottom = self.spawn_point


    def CollideHorizontal(self, platforms):
        #for each platform
        for platform  in platforms:
            #if player collides with platform
            if self.rect.colliderect(platform):
                if self.direction[0]>0: #moving right
                    self.rect.right = platform.left
                if self.direction[0]<0:#moving left
                    self.rect.left = platform.right

    def CollideVertical(self,platforms):
        #for each platform
        for platform in platforms:
            #if player collides with platform
            if self.rect.colliderect(platform):
                if self.gravity >0: #moving down 
                    self.rect.bottom = platform.top
                    self.on_ground = True # player hit ground
                if self.gravity < 0: #moving up
                    self.rect.top = platform.bottom


    def SetRecover1(self,):
        #How many recovery frames for attack 1
        self.recovery = self.recovery1
    def SetRecover2(self):
        #How many recovery frames for attack 2
        self.recovery = self.recovery2

    def Recover(self):
        #if the player is not currently attacking, they can recover
        if self.animation_state != "attack1" and self.animation_state != "attack2":
            self.recovery = max(0, self.recovery-1)


    #THIS FUNCTION SHOULD BE OVERRIDED AND OPTIMISED FOR EACH CHARACTER
    def load_animations(self,):
        animations = self.assets.getAnimations(self.name)
        self.animations = {}
        #Gets the standard animations from the assets
        #Creates an animation object based off each one
        #Values should be overrided
        self.animations["idle"] = animation(animations["idle"], 0.5, )
        self.animations["jump"] = animation(animations["jump"], 1.25, [i for i in range (20)])
        self.animations["run"] = animation(animations["run"], 1, )
        self.animations["attack1"] = animation(animations["attack1"], 0.5,[i for i in range (20)])
        self.animations["attack2"] = animation(animations["attack2"], 0.5, [i for i in range (20)])

class knight(Character):
    def __init__(self, assets, controls, spawn_point, number, recovery1, recovery2):
        super().__init__("knight", assets, controls, spawn_point, number, recovery1, recovery2)

    def load_animations(self,):
        animations = self.assets.getAnimations(self.name)
        self.animations = {}
        #Gets the standard animations from the assets
        #Creates an animation object based off each one
        #Values should be overrided
        self.animations["idle"] = animation(animations["idle"], 0.75)
        self.animations["jump"] = animation(animations["jump"], 1.25, [i for i in range (20)])
        self.animations["run"] = animation(animations["run"], 0.9)
        self.animations["attack1"] = animation(animations["attack1"], 0.5,[2,3,4,5],[2,3,4], )
        self.animations["attack2"] = animation(animations["attack2"], 1, [3,4,5,6], [3,4,5])
    
class evilWizard(Character):
    def __init__(self, assets, controls, spawn_point, number, recovery1, recovery2):
        super().__init__("evil_wizard", assets, controls, spawn_point, number, recovery1, recovery2)

    
    def draw(self, screen):
        #Draws character to screen
        rect = self.image.get_frect(center = (self.rect.centerx, self.rect.centery+self.rect.h/15))
        #pygame.draw.rect(screen, (0,0,0), self.rect)
        screen.blit(self.image, rect)

    def load_animations(self,):
        animations = self.assets.getAnimations(self.name)
        self.animations = {}
        #Gets the standard animations from the assets
        #Creates an animation object based off each one
        #Values should be overrided
        self.animations["idle"] = animation(animations["idle"], 0.75)
        self.animations["jump"] = animation(animations["jump"], 1.25, [1,2,3,4,5,6,7,8])
        self.animations["run"] = animation(animations["run"], 0.9)
        self.animations["attack1"] = animation(animations["attack1"], 0.5,[3,4,5,6,7,8],[4,5,6,7])
        self.animations["attack2"] = animation(animations["attack2"], 1, [3,4,5,6,7,8], [5,6,7,8])

class samurai(Character):
    def __init__(self, assets, controls, spawn_point, number, recovery1, recovery2):
        super().__init__("samurai", assets, controls, spawn_point, number, recovery1, recovery2)

    #def draw(self, screen):
        #Draws character to screen
       # rect = self.image.get_frect(center = (self.rect.centerx, self.rect.centery))
      #  screen.blit(self.image, rect)
    
    def load_animations(self,):
        animations = self.assets.getAnimations(self.name)
        self.animations = {}
        #Gets the standard animations from the assets
        #Creates an animation object based off each one
        #Values should be overrided
        self.animations["idle"] = animation(animations["idle"], 0.75)
        self.animations["jump"] = animation(animations["jump"], 1.25, [1,2])
        self.animations["run"] = animation(animations["run"], 0.9)
        self.animations["attack1"] = animation(animations["attack1"], 0.5,[2,3,4],[3])
        self.animations["attack2"] = animation(animations["attack2"], 1, [2,3,4], [3])



def CharacterFactory(name, assets, controls, spawn_point, number):
    match name:
        case "knight":
            return knight(assets, controls, spawn_point, number, 2, 2) 
        case "evil_wizard":
            return evilWizard(assets,controls, spawn_point, number, 2, 2)
        case "samurai":
            return samurai(assets, controls, spawn_point, number, 2, 2)
            
