import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports

# Global variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_IMAGES = {}
GAME_AUDIO = {}

# Asset paths
PLAYER = 'Gallery/images/bird.png'
BACKGROUND = 'Gallery/images/background.jpg'
pipe = 'Gallery/images/pipe.jpg'

def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerx = int(SCREENWIDTH/50)
    playery = int((SCREENHEIGHT - GAME_IMAGES['player'].get_height())/20)
    startx = int((SCREENWIDTH - GAME_IMAGES['start'].get_width())/2)
    starty = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_IMAGES['background'], (0, 0))    
                SCREEN.blit(GAME_IMAGES['player'], (playerx, playery))    
                SCREEN.blit(GAME_IMAGES['start'], (startx,starty ))    
                SCREEN.blit(GAME_IMAGES['base'], (basex, GROUNDY))    
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newpipe1 = getRandompipe()
    newpipe2 = getRandompipe()

    # my List of upper pipes
    upperpipes = [
        {'x': SCREENWIDTH+200, 'y':newpipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newpipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerpipes = [
        {'x': SCREENWIDTH+200, 'y':newpipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newpipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_AUDIO['wing'].play()


        crashTest = isCollide(playerx, playery, upperpipes, lowerpipes) # This function will return true if the player is crashed
        if crashTest:
            return     

        #check for score
        playerMidPos = playerx + GAME_IMAGES['player'].get_width()/2
        for pipe in upperpipes:
            pipeMidPos = pipe['x'] + GAME_IMAGES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_AUDIO['point'].play()


        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False            
        playerHeight = GAME_IMAGES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperpipe , lowerpipe in zip(upperpipes, lowerpipes):
            upperpipe['x'] += pipeVelX
            lowerpipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperpipes[0]['x']<5:
            newpipe = getRandompipe()
            upperpipes.append(newpipe[0])
            lowerpipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperpipes[0]['x'] < -GAME_IMAGES['pipe'][0].get_width():
            upperpipes.pop(0)
            lowerpipes.pop(0)
        
        # Lets blit our sprites now
        SCREEN.blit(GAME_IMAGES['background'], (0, 0))
        for upperpipe, lowerpipe in zip(upperpipes, lowerpipes):
            SCREEN.blit(GAME_IMAGES['pipe'][0], (upperpipe['x'], upperpipe['y']))
            SCREEN.blit(GAME_IMAGES['pipe'][1], (lowerpipe['x'], lowerpipe['y']))

        SCREEN.blit(GAME_IMAGES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_IMAGES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_IMAGES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_IMAGES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperpipes, lowerpipes):
    if playery> GROUNDY - 25  or playery<0:
        GAME_AUDIO['hit'].play()
        return True
    
    for pipe in upperpipes:
        pipeHeight = GAME_IMAGES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_IMAGES['pipe'][0].get_width()):
            GAME_AUDIO['hit'].play()
            return True

    for pipe in lowerpipes:
        if (playery + GAME_IMAGES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_IMAGES['pipe'][0].get_width():
            GAME_AUDIO['hit'].play()
            return True

    return False

def getRandompipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_IMAGES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_IMAGES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper pipe
        {'x': pipeX, 'y': y2} #lower pipe
    ]
    return pipe






if __name__ == "__main__":
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Hacking Bird')
    
    # Load images
    GAME_IMAGES['numbers'] = (
        pygame.image.load('Gallery/images/0.png').convert_alpha(),
        pygame.image.load('Gallery/images/1.png').convert_alpha(),
        pygame.image.load('Gallery/images/2.png').convert_alpha(),
        pygame.image.load('Gallery/images/3.png').convert_alpha(),
        pygame.image.load('Gallery/images/4.png').convert_alpha(),
        pygame.image.load('Gallery/images/5.png').convert_alpha(),
        pygame.image.load('Gallery/images/6.png').convert_alpha(),
        pygame.image.load('Gallery/images/7.png').convert_alpha(),
        pygame.image.load('Gallery/images/8.png').convert_alpha(),
        pygame.image.load('Gallery/images/9.png').convert_alpha(),
    )

    GAME_IMAGES['start'] = pygame.image.load('Gallery/images/front.png').convert_alpha()
    GAME_IMAGES['base'] = pygame.image.load('Gallery/images/base.jpg').convert_alpha()
    GAME_IMAGES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(), 180),
        pygame.image.load(pipe).convert_alpha()
    )
    GAME_IMAGES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_IMAGES['player'] = pygame.image.load(PLAYER).convert_alpha()

    # Resize images
    PLAYER_SIZE = (34, 24)  # Example size for the bird
    BACKGROUND_SIZE = (SCREENWIDTH, SCREENHEIGHT)  # Background should cover the whole screen
    PIPE_SIZE = (52, 320)  # Example size for the pipe (adjust as needed)
    BASE_SIZE = (SCREENWIDTH, 112)  # Example size for the base
    START_SIZE = (SCREENWIDTH, SCREENHEIGHT)  # Example size for the start screen image (adjust as needed)

    # Resize loaded images
    GAME_IMAGES['player'] = pygame.transform.scale(GAME_IMAGES['player'], PLAYER_SIZE)
    GAME_IMAGES['background'] = pygame.transform.scale(GAME_IMAGES['background'], BACKGROUND_SIZE)
    GAME_IMAGES['base'] = pygame.transform.scale(GAME_IMAGES['base'], BASE_SIZE)
    GAME_IMAGES['start'] = pygame.transform.scale(GAME_IMAGES['start'], START_SIZE)

    # Resize pipes
    GAME_IMAGES['pipe'] = (
        pygame.transform.scale(GAME_IMAGES['pipe'][0], PIPE_SIZE),
        pygame.transform.scale(GAME_IMAGES['pipe'][1], PIPE_SIZE)
    )

    # Load sounds
    GAME_AUDIO['die'] = pygame.mixer.Sound('Gallery/Audio/die.mp3')
    GAME_AUDIO['hit'] = pygame.mixer.Sound('Gallery/Audio/hit.mp3')
    GAME_AUDIO['point'] = pygame.mixer.Sound('Gallery/Audio/point.mp3')
    GAME_AUDIO['cyber'] = pygame.mixer.Sound('Gallery/Audio/cyber.mp3')
    GAME_AUDIO['wing'] = pygame.mixer.Sound('Gallery/Audio/wing.mp3')

    while True:
        welcomeScreen()
        mainGame()