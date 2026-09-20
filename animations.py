import pygame

class animation:
    def __init__(self, frames, animation_time, bFrames=[],aFrames=[], iFrames=[], ):
        # iFrames = frames that character should be invincible in
        # bFrames = busy frames, animation is LOCKED
        # aFrames = frames that should damage the enemy if in contact
        self.frames = frames
        self.frame_duration = animation_time/len(self.frames)
        
        self.index = 0
        self.stopwatch = 0

        self.iFrames = iFrames
        self.bFrames = bFrames
        self.aFrames = aFrames
    
    def reset(self):
        self.index = 0
        self.stopwatch = 0
    
    def SetFrame(self, n):
        self.stopwatch = 0
        self.index = n

    def getFrameNumber(self,):
        return self.index

    def getFrame(self, facing_left):
        return pygame.transform.flip(self.frames[self.index], facing_left, False)
    
    def getIstatus(self):
        '''returns whether or not the player
        should be invincible'''
        return (self.index+1 in self.iFrames)
    
    def getBstatus(self):
        '''returns whether or not, the player should
        be able to cancel their attack in the 
        current frame'''
        return (self.index+1 in self.bFrames)
    
    def getAstatus(self):
        '''returns whether or not, the player 
        should actually damage the enemy'''
        return (self.index+1 in self.aFrames)
    

    def update(self, dt):
        #increment stopwatch by time elapsed since last frame
        self.stopwatch += dt

        if self.stopwatch >= self.frame_duration:
            #reset stopwatch
            self.stopwatch = 0

            #move to next frame
            self.index +=1
            
            #if animation is finished, reset to be reused
            # and return true
            if self.index >= len(self.frames):
                self.reset()
                return True
                
        return False       
        

                