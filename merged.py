import pygame
import cv2
import numpy as np
import random


pygame.init()

WIDTH, HEIGHT = 1600, 725
screen = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

racket_image = pygame.image.load("tennis_racket.png")
field_image = pygame.image.load("field.png")
field_image = pygame.transform.scale(field_image, (1600, 700))

pygame.mouse.set_visible(False)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler beim Öffnen der Kamera")
    exit()

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
    for i, contour in enumerate(contours):
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

ball_radius = 30
ball_x, ball_y = random_ball_position()

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
            ball_x, ball_y = random_ball_position()

    pygame.draw.circle(screen, GREEN, (ball_x, ball_y), ball_radius)

    pygame.display.flip()

cap.release()
pygame.quit()