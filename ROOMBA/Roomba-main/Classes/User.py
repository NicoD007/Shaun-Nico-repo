import pygame
import sys


class User:
    def __init__(self, username: str, email: str, password: str) -> None:
        self._username = username
        self._password = password
        self._email = email
        self._userId: int = 0

    def getUsername(self) -> str:
        return self._username

    def setEmail(self, email: str) -> None:
        self._email = email

    def start(self) -> None:
        pass

    def checkPassword(self, password: str) -> bool:  ##new method (add to class diagram)
        return password == self._password


pygame.init()

screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Login")
clock = pygame.time.Clock()
font = pygame.font.SysFont("segoeui", 20)

user = User(username="TestUser", email="test@gmail.com", password="roomba123")

input_text = ""
active = False
status = ""

while True:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            active = True
        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if user.checkPassword(input_text):
                    status = "success"
                else:
                    status = "error"
                input_text = ""
            else:
                input_text += event.unicode

    # Email
    screen.blit(font.render("Email:", True, (255, 255, 255)), (60, 80))
    screen.blit(font.render(user._email, True, (180, 180, 180)), (160, 80))

    # Password
    screen.blit(font.render("Password:", True, (255, 255, 255)), (60, 130))
    box_rect = pygame.Rect(60, 160, 280, 34)
    pygame.draw.rect(screen, (40, 40, 40), box_rect)
    pygame.draw.rect(screen, (150, 150, 150), box_rect, 1)
    screen.blit(font.render("•" * len(input_text), True, (255, 255, 255)), (68, 165))

    # Status text
    if status == "success":
        screen.blit(font.render("Login successful!", True, (0, 200, 0)), (60, 220))
    elif status == "error":
        screen.blit(font.render("Incorrect password.", True, (200, 0, 0)), (60, 220))

    pygame.display.flip()