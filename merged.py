import pygame
import cv2
import numpy as np
import random
import time

pygame.init()

# Spielkonstanten
WIDTH, HEIGHT = 1600, 725
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
FONT = pygame.font.Font(None, 36)

# Punktwerte und Spielstand
POINT_VALUES = [0, 15, 30, 40]
player_points = 0
opponent_points = 0
player_games = 0
opponent_games = 0
player_sets = 0
opponent_sets = 0

# Init Kamera und Spielbildschirm
screen = pygame.display.set_mode((WIDTH, HEIGHT))
racket_image = pygame.image.load("tennis_racket.png")
field_image = pygame.image.load("field.png")
field_image = pygame.transform.scale(field_image, (1600, 700))
pygame.mouse.set_visible(False)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler beim Öffnen der Kamera")
    exit()

def reset_game_points():
    global player_points, opponent_points
    player_points = 0
    opponent_points = 0

def win_game(winner):
    global player_games, opponent_games, player_sets, opponent_sets
    if winner == "player":
        player_games += 1
        if player_games >= 6 and player_games - opponent_games >= 2:
            player_sets += 1
            player_games, opponent_games = 0, 0
    elif winner == "opponent":
        opponent_games += 1
        if opponent_games >= 6 and opponent_games - player_games >= 2:
            opponent_sets += 1
            player_games, opponent_games = 0, 0

    reset_game_points()

def rectangles_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 > x2 + w2 or x2 > x1 + w1 or y1 > y2 + h2 or y2 > y1 + h1)

def detect_green_object(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    mask = cv2.inRange(hsv_frame, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    objects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contour)
            current_rect = (x, y, w, h)

            overlap = False
            for obj_rect in objects:
                if rectangles_overlap(current_rect, obj_rect):
                    overlap = True
                    break

            if not overlap:
                objects.append(current_rect)
                cx, cy = x + w // 2, y + h // 2
                return cx, cy, w  

    return None, None, None  

def random_ball_position():
    ball_x = random.randint(50, WIDTH - 50)
    ball_y = random.randint(50, HEIGHT - 50)
    return ball_x, ball_y

# Initiale Ball- und Timer-Variablen
ball_radius = 30
ball_x, ball_y = random_ball_position()
ball_spawn_time = time.time()

running = True
offset_x = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Abrufen des Frames")
        break

    green_x, green_y, green_w = detect_green_object(frame)
    screen.fill(WHITE)

    if time.time() - ball_spawn_time >1:
        opponent_points += 1
        if opponent_points >= len(POINT_VALUES):
            win_game("opponent")
        ball_x, ball_y = random_ball_position()
        ball_spawn_time = time.time()

    if green_x is not None:
        flipped_x = cap.get(3) - green_x
        mapped_x = int((flipped_x / cap.get(3)) * WIDTH)
        mapped_y = int((green_y / cap.get(4)) * HEIGHT)

        scaled_width = int(50 + (green_w / 100) * 100)
        scaled_height = int(125 + (green_w / 100) * 250)
        scaled_racket_image = pygame.transform.scale(racket_image, (scaled_width, scaled_height))

        offset_x = (WIDTH // 2 - mapped_x) * 0.1
        screen.blit(field_image, (offset_x, 0))

        racket_rect = scaled_racket_image.get_rect(center=(mapped_x, mapped_y + scaled_height // 2))
        screen.blit(scaled_racket_image, racket_rect.topleft)

        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
        
        if racket_rect.colliderect(ball_rect):
            player_points += 1
            if player_points >= len(POINT_VALUES):
                win_game("player")
            ball_x, ball_y = random_ball_position()
            ball_spawn_time = time.time()

    pygame.draw.circle(screen, GREEN, (ball_x, ball_y), ball_radius)

    #Scoreboard
    player_score_text = f"Spieler: {POINT_VALUES[player_points]} | Spiele: {player_games} | Sätze: {player_sets}"
    opponent_score_text = f"Gegner: {POINT_VALUES[opponent_points]} | Spiele: {opponent_games} | Sätze: {opponent_sets}"
    
    player_score_surface = FONT.render(player_score_text, True, (0, 0, 0))
    opponent_score_surface = FONT.render(opponent_score_text, True, (0, 0, 0))
    
    screen.blit(player_score_surface, (WIDTH - 500, 20))
    screen.blit(opponent_score_surface, (WIDTH - 500, 60))

    pygame.display.flip()

cap.release()
pygame.quit()