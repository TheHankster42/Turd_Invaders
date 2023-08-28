import pygame
import random
import math
from pygame import mixer
import shelve

ACCELERATION = 0.5
MAXSPEED = 5
FRICTION = 0.1
ENEMYSPEED = 2
ENEMYDOWNSTEP = 64
YSPAWNLOCATIONS = [0,64,128]

# Intializes pygame
pygame.init()
pygame.mixer.init()

# create window :   width & hieght
screen = pygame.display.set_mode((800,600))
background = pygame.image.load("images/TurdInvadersBackground.png")
mixer.music.load('sound/backgroundmusic.wav')
mixer.music.set_volume(0.75)
mixer.music.play(-1)
bullet_sound=mixer.Sound('sound/whoosh.wav')
explosion_sound=mixer.Sound('sound/fart.wav')
explosion_sound.set_volume(0.5)

#title and icon
pygame.display.set_caption("Turd Invaders")
icon=pygame.image.load("images/poo.png")
pygame.display.set_icon(icon)

#read highscore

d = shelve.open('score.txt')
highscore = 0
if "score" in d:
    highscore = d["score"]
d.close()

#score
score_value = 0
font = pygame.font.Font("freesansbold.ttf",32)

textX= 10
textY=10

#game over
over_font = pygame.font.Font("freesansbold.ttf",64)

#Player
playerImg = pygame.image.load("images/toilet-paper.png")
playerX=368
playerY=480
playerX_change = 0
playerX_direction = 1
playerX_accelerating = False

#Enemy
enemyImg=[]
enemyX=[]
enemyY=[]
enemyX_direction=[]
speed=ENEMYSPEED
num_of_enemies = 10

for i in range (num_of_enemies):
    enemyImg.append(pygame.image.load("images/poop.png"))
    enemyX.append(random.randint(0,735))
    enemyY.append(random.choice(YSPAWNLOCATIONS))
    enemyX_direction.append(1)

#bullet
bulletImg = pygame.image.load("images/burrito(1).png")
bulletX=0
bulletY=480
bulletX_change = 0
bulletY_change = 10
bullet_state="ready"

def show_score(x,y):
    score = font.render("Score : " + str(score_value),True, (0,0,0))
    highscore_text = font.render("Highscore : " + str(highscore),True, (0,0,0))
    screen.blit(score, (x,y))
    screen.blit(highscore_text,(x,y+32))

def game_over_text():
    over_text = over_font.render("GAME OVER",True, (0,0,0))
    screen.blit(over_text, (200,250))

def player(x,y):
    screen.blit(playerImg, (x,y))
    
def enemy(x,y,i):
    screen.blit(enemyImg[i], (x,y))

def fire_bullet(x,y):
    global bullet_state
    bullet_state="fire"
    screen.blit(bulletImg, (x+16,y+10))

def isCollision(enemyX,enemyY,bulletX,bulletY):
    distance = (math.sqrt(math.pow(enemyX-bulletX,2)) + (math.pow(enemyY-bulletY,2)))
    if distance < 42:
        return True
    else: return False

# Game loop
running = True
game_over = False
saved = False
while running:
    #Background
    screen.fill((173,216,230))
    screen.blit(background,(0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_direction = -1
                playerX_accelerating = True
            if event.key == pygame.K_RIGHT:
                playerX_direction = 1
                playerX_accelerating = True
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bulletX = playerX
                fire_bullet(bulletX,bulletY)
                bullet_sound.play()
            if event.key == pygame.K_r and game_over:
                game_over = False
                saved = False
                score_value = 0
                playerImg = pygame.image.load("images/toilet-paper.png")
                for i in range (num_of_enemies):
                    enemyX[i] = random.randint(0,735)
                    enemyY[i] = random.choice(YSPAWNLOCATIONS)
                speed = ENEMYSPEED

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                playerX_direction = -1
                playerX_accelerating = False
            if event.key == pygame.K_RIGHT:
                playerX_direction = 1
                playerX_accelerating = False

    if playerX_accelerating:
        playerX_change += playerX_direction * ACCELERATION
        playerX_change = min(playerX_change, MAXSPEED) if playerX_direction == 1 else max(playerX_change, -MAXSPEED)
    elif playerX_change != 0:
        current_direction = 1 if playerX_change > 0 else -1
        playerX_change -= current_direction * FRICTION
        if current_direction * playerX_change < 0: playerX_change = 0

    playerX += playerX_change
#bouncy wall
    if (playerX <=0):  
        playerX_change *= -1
        playerX = 0

    elif (playerX >= 736):
        playerX_change *= -1
        playerX = 736
#bullet movement
    if bulletY <= 0:
        bulletY=480
        bullet_state="ready"

    if bullet_state == "fire":
        fire_bullet(bulletX,bulletY)
        bulletY -= bulletY_change

    #enemy movement
    if not game_over:
        for i in range (num_of_enemies):

            #GAME OVER
            if enemyY[i] > 448:
                game_over = True
                for j in range (num_of_enemies):
                    enemyY[j] = 2000
                break
                
            enemyX[i] += enemyX_direction[i]*speed

            if (enemyX[i] <=0) or (enemyX[i]>=736):
                enemyX_direction[i] *= -1
                enemyY[i]+=64
    #collision
            collision = isCollision(enemyX[i],enemyY[i],bulletX,bulletY)
            if collision:
                explosion_sound.play()
                bulletY=480
                bullet_state="ready"
                score_value += 1
                enemyX[i]=random.randint(0,735)
                enemyY[i]=random.choice(YSPAWNLOCATIONS)
                speed += score_value * 0.01


            enemy(enemyX[i], enemyY[i], i)

    if game_over and not saved:
        playerImg = pygame.image.load("images/soiled-toilet-paper.png")
        d = shelve.open("score.txt")
        if "score" not in d or score_value > d["score"]:
            d["score"] = score_value
            highscore = score_value
        d.close()
        
        saved = True
    if game_over:
        game_over_text()
    player(playerX,playerY)
    show_score(textX,textY)
    pygame.display.update()