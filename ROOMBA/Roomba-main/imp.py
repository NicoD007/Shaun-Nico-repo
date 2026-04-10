import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Message for Nico")

font = pygame.font.SysFont("Arial", 60, bold=True)

TEXT = "NICO IS GAY AND STUPID"

# VIBGYOR colors (Violet, Indigo, Blue, Green, Yellow, Orange, Red)
VIBGYOR = [
    (148, 0,   211),  # Violet
    (75,  0,   130),  # Indigo
    (0,   0,   255),  # Blue
    (0,   255, 0  ),  # Green
    (255, 255, 0  ),  # Yellow
    (255, 127, 0  ),  # Orange
    (255, 0,   0  ),  # Red
]

def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def get_vibgyor_color(t):
    """t is 0.0 to 1.0, cycles through VIBGYOR"""
    t = t % 1.0
    n = len(VIBGYOR)
    scaled = t * n
    idx = int(scaled) % n
    frac = scaled - int(scaled)
    return lerp_color(VIBGYOR[idx], VIBGYOR[(idx + 1) % n], frac)

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill((10, 10, 10))  # Near-black background

    elapsed = (pygame.time.get_ticks() - start_time) / 1000.0  # seconds

    # Render each character with its own color offset
    total_width = font.size(TEXT)[0]
    x_start = (WIDTH - total_width) // 2
    y = (HEIGHT - font.get_height()) // 2

    x = x_start
    for i, char in enumerate(TEXT):
        # Each character gets a phase offset based on position + time
        phase = (i / len(TEXT)) + elapsed * 0.4
        color = get_vibgyor_color(phase)
        char_surf = font.render(char, True, color)
        screen.blit(char_surf, (x, y))
        x += font.size(char)[0]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()