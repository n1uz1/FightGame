import pygame
import sys

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 90
PLAYER_SPEED = 5
JUMP_HEIGHT = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self, x, y, color, controls):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = color
        self.controls = controls
        self.vel_y = 0
        self.on_ground = True
        self.health = 100
        self.attack_cooldown = 0

    def handle_input(self, keys):
        if keys[self.controls['left']]:
            self.rect.x -= PLAYER_SPEED
        if keys[self.controls['right']]:
            self.rect.x += PLAYER_SPEED
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = -JUMP_HEIGHT
            self.on_ground = False
        if keys[self.controls['attack']] and self.attack_cooldown == 0:
            self.attack_cooldown = FPS  # simple cooldown

    def update(self):
        # gravity
        self.vel_y += 1
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # health bar
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, PLAYER_WIDTH, 5))
        pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.y - 10, PLAYER_WIDTH * (self.health / 100), 5))

    def attack(self, other):
        if self.attack_cooldown == FPS - 1:  # attack triggers once when cooldown starts
            hitbox = self.rect.copy()
            hitbox.width += 20
            if self.color == BLUE:
                hitbox.x += 20
            else:
                hitbox.x -= 20
            if hitbox.colliderect(other.rect):
                other.health = max(0, other.health - 10)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Fight Game")

    controls1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_f}
    controls2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'attack': pygame.K_KP0}
    player1 = Player(100, HEIGHT - PLAYER_HEIGHT - 50, BLUE, controls1)
    player2 = Player(WIDTH - 160, HEIGHT - PLAYER_HEIGHT - 50, RED, controls2)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player1.handle_input(keys)
        player2.handle_input(keys)

        player1.update()
        player2.update()

        player1.attack(player2)
        player2.attack(player1)

        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 50, WIDTH, 50))
        player1.draw(screen)
        player2.draw(screen)

        if player1.health == 0 or player2.health == 0:
            winner = "Player 1" if player2.health == 0 else "Player 2"
            font = pygame.font.SysFont(None, 72)
            text = font.render(f"{winner} Wins!", True, BLACK)
            rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
