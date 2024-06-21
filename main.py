import pygame
import random
import math
import cv2
import mediapipe as mp
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Load background music
mixer.music.load('background.wav')
mixer.music.play(-1)

# Screen setup
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption('Space Invader')
icon = pygame.image.load('img.png')
pygame.display.set_icon(icon)

# Load images
background = pygame.image.load('img_1.png')
background = pygame.transform.scale(background, (1000, 700))
playerImg = pygame.image.load('img_3.png')
playerImg = pygame.transform.scale(playerImg, (64, 64))
bullet = pygame.image.load('img_5.png')
bullet = pygame.transform.scale(bullet, (32, 32))

# Initialize game variables
running = True
alien = []
alienX = []
alienY = []
alienChange = []
no_of_aliens = 6

for i in range(no_of_aliens):
    alien1 = pygame.image.load('img_4.png')
    alien1 = pygame.transform.scale(alien1, (56, 56))
    alien.append(alien1)
    alienX.append(random.randint(1, 899))
    alienY.append(random.randint(30, 200))
    alienChange.append(35)

spaceShipX = 450
spaceShipY = 580
check = False
bulletX = 454
bulletY = 590
score = 0
font = pygame.font.SysFont('Arial', 32, 'bold')
game_over = pygame.font.SysFont('Arial', 64, 'bold')

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 256)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 256)
def GameOver():
    gm = game_over.render('G A M E  O V E R', True, 'white')
    screen.blit(gm, (290, 320))

def Scores():
    img = font.render(f'Score: {score}', True, 'white')
    screen.blit(img, (10, 10))

def player():
    screen.blit(playerImg, (spaceShipX, spaceShipY))

def collission():
    for i in range(no_of_aliens):
        distance = math.sqrt(math.pow(bulletX - alienX[i], 2) + math.pow(bulletY - alienY[i], 2))
        if distance <= 37:
            alienX[i] = random.randint(1, 899)
            alienY[i] = random.randint(30, 200)
            return True
    return False

def detect_gesture(landmarks):
    fingers=[]
    tipId=[4,8,12,16,20]
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    thumb_index_dist = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
    index_middle_dist = math.sqrt((index_tip.x - middle_tip.x) ** 2 + (index_tip.y - middle_tip.y) ** 2)
    middle_ring_dist = math.sqrt((middle_tip.x - ring_tip.x) ** 2 + (middle_tip.y - ring_tip.y) ** 2)
    ring_pinky_dist = math.sqrt((ring_tip.x - pinky_tip.x) ** 2 + (ring_tip.y - pinky_tip.y) ** 2)

    if landmarks[4].x < landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for id in range(1, 5):
        if landmarks[tipId[id]].y < landmarks[tipId[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    total=fingers.count(1)
    if total==2:
       if fingers[0]:
          if fingers[1]:
              if thumb_index_dist>0.3:
                 return 'L'
       elif fingers[1]:
           if fingers[2]:
               if index_middle_dist<0.1:
                  return 'R'
    if total==5:
        if index_middle_dist<0.1 and middle_ring_dist<0.1 and ring_pinky_dist<0.1 and thumb_index_dist>0.3:
           return 'S'
    return None

inc = 0
while running:
    success, image = cap.read()
    if not success:
        continue
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(hand_landmarks.landmark)
            if gesture == 'L':
                inc = -40
            elif gesture == 'R':
                inc = 40
            elif gesture == 'S' and not check:
                bulletSound = mixer.Sound('laser.wav')
                bulletSound.play()
                check = True
                bulletX = spaceShipX + 18
            else:
                inc = 0

    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    Scores()
    spaceShipX += inc
    if spaceShipX <= 0:
        spaceShipX = 0
    elif spaceShipX >= 900:
        spaceShipX = 900

    for i in range(no_of_aliens):
        alienX[i] -= alienChange[i]
        if alienX[i] <= 0:
            alienY[i] += 30
            alienChange[i] = -35
        elif alienX[i] >= 900:
            alienY[i] += 30
            alienChange[i] = 35

    if bulletY <= 0:
        bulletY = 590
        check = False

    player()
    for i in range(no_of_aliens):
        screen.blit(alien[i], (alienX[i], alienY[i]))

    if check:
        screen.blit(bullet, (bulletX, bulletY))
        bulletY -= 45

    for i in range(no_of_aliens):
        if alienY[i] >= 545:
            for j in range(no_of_aliens):
                alienY[j] = 2000
            GameOver()
            break

    colllisionOcc = collission()
    if colllisionOcc:
        collSound = mixer.Sound('explosion.wav')
        collSound.play()
        bulletY = 590
        score += 1
        Scores()
        check = False

    pygame.display.update()

cap.release()
cv2.destroyAllWindows()
pygame.quit()
