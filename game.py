import pygame

pygame.init()

WIDTH, HEIGHT = 1600, 725
screen = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)

racket_image = pygame.image.load("tennis_racket.png")
racket_image = pygame.transform.scale(racket_image, (50, 125))

field_image = pygame.image.load("field.png")
field_image = pygame.transform.scale(field_image, (1600, 700))


pygame.mouse.set_visible(False)


offset_x = 0

pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()

    offset_x = (WIDTH // 2 - mouse_x) * 0.1

    screen.blit(field_image, (offset_x, 0))

    racket_rect = racket_image.get_rect(center=(mouse_x, mouse_y + 62.5))
    screen.blit(racket_image, racket_rect.topleft)

    pygame.display.flip()

pygame.quit()