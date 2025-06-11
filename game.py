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
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# -----------------------------------------------------------------------------
# Helper functions to build a more colorful game
# -----------------------------------------------------------------------------
def create_sprite(body_color, pants_color):
    """Create a simple humanoid sprite surface."""
    surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
    head_r = PLAYER_WIDTH // 4
    body_top = head_r * 2
    # head
    pygame.draw.circle(surf, body_color, (PLAYER_WIDTH // 2, head_r), head_r)
    # torso
    torso_height = PLAYER_HEIGHT - body_top
    upper = torso_height // 2
    pygame.draw.rect(
        surf,
        body_color,
        (PLAYER_WIDTH // 3, body_top, PLAYER_WIDTH // 3, upper),
    )
    # pants
    pygame.draw.rect(
        surf,
        pants_color,
        (PLAYER_WIDTH // 3, body_top + upper, PLAYER_WIDTH // 3, upper),
    )
    # arms
    pygame.draw.rect(
        surf,
        body_color,
        (PLAYER_WIDTH // 3 - 10, body_top + 10, PLAYER_WIDTH // 3 + 20, 10),
    )
    # legs
    pygame.draw.rect(
        surf,
        pants_color,
        (PLAYER_WIDTH // 3 - 5, body_top + upper + 10, 10, upper - 10),
    )
    pygame.draw.rect(
        surf,
        pants_color,
        (
            PLAYER_WIDTH // 3 + PLAYER_WIDTH // 3 - 5,
            body_top + upper + 10,
            10,
            upper - 10,
        ),
    )
    return surf

def draw_background(surface):
    """Draw a simple gradient sky and floor."""
    for y in range(HEIGHT - 50):
        c = 60 + 120 * y // (HEIGHT - 50)
        pygame.draw.line(surface, (0, c, 200), (0, y), (WIDTH, y))
    pygame.draw.rect(surface, (60, 40, 20), (0, HEIGHT - 50, WIDTH, 50))

def draw_health_bar(surface, x, y, pct, color):
    pygame.draw.rect(surface, BLACK, (x - 2, y - 2, 204, 24), 2)
    pygame.draw.rect(surface, color, (x, y, int(200 * pct), 20))

class Player:
    def __init__(self, x, y, sprite_colors, controls, facing_right=True):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.body_color, self.pants_color = sprite_colors
        self.sprite = create_sprite(self.body_color, self.pants_color)
        self.controls = controls
        self.facing_right = facing_right
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
        image = self.sprite
        if not self.facing_right:
            image = pygame.transform.flip(self.sprite, True, False)
        surface.blit(image, self.rect.topleft)

    def attack(self, other):
        if self.attack_cooldown == FPS - 1:  # attack triggers once when cooldown starts
            hitbox = self.rect.copy()
            hitbox.width += 20
            if self.facing_right:
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

    controls1 = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_w,
        'attack': pygame.K_f,
    }
    controls2 = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'attack': pygame.K_KP0,
    }

    player1 = Player(
        100,
        HEIGHT - PLAYER_HEIGHT - 50,
        (BLUE, YELLOW),
        controls1,
        facing_right=True,
    )
    player2 = Player(
        WIDTH - 160,
        HEIGHT - PLAYER_HEIGHT - 50,
        (RED, GREEN),
        controls2,
        facing_right=False,
    )

    font = pygame.font.SysFont(None, 72)

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

        draw_background(screen)
        player1.draw(screen)
        player2.draw(screen)
        draw_health_bar(screen, 50, 20, player1.health / 100, BLUE)
        draw_health_bar(screen, WIDTH - 250, 20, player2.health / 100, RED)

        if player1.health == 0 or player2.health == 0:
            winner = "Player 1" if player2.health == 0 else "Player 2"
            text = font.render(f"{winner} Wins!", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
