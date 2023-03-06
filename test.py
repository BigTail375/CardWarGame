#imports
import pygame

#Game Control Object       
class Game:
    
    def __init__(self,windowWidth,windowHeight):
        
        #Pygame Setup
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.window = pygame.display.set_mode((self.windowWidth,self.windowHeight))
        self.clock = pygame.time.Clock()
        pygame.init()
    
        #Rooms / Levels are stored in a list
        self.rooms = [] 
    
    #Begin the game loop
    def start(self):
        self.running = True #game is running or not?
        self.inRoom = 0 #Current Room index
        self.rooms[self.inRoom].setDisplay() #Sets the window display with room name
      
    #Stop the game loop
    def stop(self):
        self.running = False
    
    #Add Room to the game list
    def addRoom(self, r):
        self.rooms.append(r)
    
    #Returns a Room Object for the room that is currently being displayed
    def currentRoom(self):
        return self.rooms[self.inRoom]
    
    #Send Game to a specific room -> x is the index of the room
    def goToRoom(self,x):
        self.inRoom = x
        self.rooms[self.inRoom].setDisplay()
    
    #Send Game to the next room in the list
    def nextRoom(self):
        self.inRoom = self.inRoom + 1
        self.rooms[self.inRoom].setDisplay()

    #Create a Surface to represent the background in the game with specific color
    def makeBackground(self, val):
        
        #If parameter sent is a string assume its a file to be loaded
        if isinstance(val, str):
            background = pygame.image.load(val).convert()
            
        #If parameter sent is a tuple assume its a color to be loaded
        if isinstance(val, tuple):    
            background = pygame.Surface( (self.windowWidth,self.windowHeight) )
            background.fill(val)
        
        return background
    
    #Create a Surface to represent an image
    def makeSpriteImage(self, picturePath):
        return pygame.image.load(picturePath).convert()
   
    #Create a font
    def makeFont(self, name, size):
        return pygame.font.SysFont(name,size)
    
    #Make a Rectangle
    def makeRectangle(self, width, height, color):
        
        #Create a surface with the correct color
        s = pygame.Surface((width,height))
        s.fill(color)
        return s
    
    #Make a Circle    
    def makeCircle(self, radius, color):
        #Create the image Surface to Draw 
        s = pygame.Surface((radius*2 , radius*2), pygame.SRCALPHA)
        
        #Create the circle on the surface
        pygame.draw.circle(s, color, (int(radius),int(radius)), int(radius))
    
        return s
    
    def getCollisions(self, obj):
        return pygame.sprite.spritecollide(obj ,self.currentRoom().roomObjects, False, pygame.sprite.collide_mask)
                
#Room / Level Object       
class Room:
    
    def __init__(self, name, background):
        self.roomObjects = pygame.sprite.Group() #Create a group of Game Objects
        self.background = background #Sets the background for the room
        self.name = name #Sets the name of the room

    #Add object to Room Group
    def addObject(self, obj):
        self.roomObjects.add(obj)

    #Call update function for each Game Object in the room
    def updateObjects(self):
        self.roomObjects.update()
    
    #Draw each Game Object in the room -> Need to know the game object to draw on
    def renderObjects(self,game):
        self.roomObjects.draw(game.window)
    
    #Draw the background -> Need to know the game object to draw on
    def renderBackground(self, game):
        game.window.blit(self.background, (0, 0))
    
    #Set the caption of the room window
    def setDisplay(self):
        pygame.display.set_caption(self.name)
    
    #Check each object in the room to see what got clicked on
    def whatGotClicked(self):
        for obj in self.roomObjects:
            mouseX, mouseY = pygame.mouse.get_pos()
            maskX, maskY = (mouseX - obj.rect.x, mouseY - obj.rect.y)
            
            if obj.rect.collidepoint((mouseX,mouseY)) and obj.mask.get_at((maskX,maskY)):
            
                return obj
                           
                
#All Objects in the Game are part of pygames Sprite Class
#Sprite requires an image / Surface
#rect is a bounding box sized to the image / Surface -> Its how you control an objects position

#Any object that is put in a room must extend GameObject
#picture is the image of the object to display on the screen, if none given it creates a blank surface with no size
class GameObject(pygame.sprite.Sprite):
    
    def __init__(self,picture = None):
        pygame.sprite.Sprite.__init__(self)

        if picture == None:
            self.image = pygame.Surface((0,0))
        else:
            self.image = picture
    
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.mouseHasPressedOnMe = False

    def checkMousePressedOnMe(self, e):
        mouseX, mouseY = pygame.mouse.get_pos()
        maskX, maskY = (mouseX - self.rect.x, mouseY - self.rect.y)
        if e.type == pygame.MOUSEBUTTONDOWN:    
            if self.rect.collidepoint((mouseX,mouseY)) and self.mask.get_at((maskX,maskY)):
                self.mouseHasPressedOnMe = True         


#Helpful Objects to Have in a game --------------------------------------------

#Timer Object
class Alarm:
    def __init__(self):
       
        self.alarm = False
        self.alarmTime = pygame.time.get_ticks()
        self.alarmValue = 0
    
    #Set alarm timer to start counting down -> In ms so time = 1000 -> 1 s    
    def setAlarm(self, time):
        self.alarm = True
        self.alarmTime = pygame.time.get_ticks()
        self.alarmValue = time 
    
    #Checks if the alarm is finished or not
    def finished(self): 
        currentTime = pygame.time.get_ticks()
        if self.alarm and currentTime - self.alarmTime > self.alarmValue:
            self.alarmTime = currentTime
            self.alarm = False  
            return True
        else:
            return False    



#Text Boxes / Buttons

#Creates a transparent rectangular text box if buttonWidth, buttonHeight, buttonColor = None
#Creates a colored rectangular text box if they are specified
class TextRectangle(GameObject):
    
    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth = None, buttonHeight = None, buttonColor = None):
        GameObject.__init__(self)

        self.font = font
        self.textColor = textColor
        self.buttonColor = buttonColor
        self.buttonWidth = buttonWidth
        self.buttonHeight = buttonHeight
        
        self.setText(text)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        #Top Left Corner is position
        self.rect.x = xPos 
        self.rect.y = yPos

    def setText(self,text):
        #Create the text surface
        self.textSurface = self.font.render(text, True, self.textColor)
        self.textWidth = self.textSurface.get_width()
        self.textHeight = self.textSurface.get_height()
        
        #Create the image and draw the text centered on the image
        if self.buttonColor == None and self.buttonWidth == None and self.buttonHeight == None:
           
            self.image = pygame.Surface((self.textWidth, self.textHeight), pygame.SRCALPHA)
            self.image.blit(self.textSurface,(0,0))

        else:
            self.image = pygame.Surface((self.buttonWidth, self.buttonHeight))
            self.image.fill(self.buttonColor)
            self.image.blit(self.textSurface,(self.buttonWidth/2-self.textWidth/2,self.buttonHeight/2-self.textHeight/2))
   

#Draws a colored circle with text in it
class TextCircle(GameObject):

    def __init__(self,text, xCenter, yCenter, font, textColor, buttonRadius, buttonColor):
        GameObject.__init__(self)
        self.font = font
        self.textColor = textColor
        self.buttonColor = buttonColor
        self.buttonRadius = buttonRadius
        
        self.setText(text)
        
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.centerx = xCenter
        self.rect.centery = yCenter

    def setText(self,text):
        
        #Create the text surface
        self.textSurface = self.font.render(text, True, self.textColor)
        self.textWidth = self.textSurface.get_width()
        self.textHeight = self.textSurface.get_height()
        
        #Create the image Surface to Draw 
        self.image = pygame.Surface((self.buttonRadius*2 , self.buttonRadius*2), pygame.SRCALPHA)
        
        #Create the circle on the image
        self.cir = pygame.draw.circle(self.image, self.buttonColor, (int(self.buttonRadius),int(self.buttonRadius)), int(self.buttonRadius))
    
        #Draw the text on the image
        self.image.blit(self.textSurface,(self.buttonRadius-self.textWidth/2,self.buttonRadius-self.textHeight/2))
    
   