import pygame
import sys

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60
FLOOR_HEIGHT = 50
GRAVITY = 1

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 90
PLAYER_SPEED = 5
JUMP_HEIGHT = 15
ATTACK_RANGE = 20
SPRITE_SHEET = "hero.png"
SPRITE_FRAME_W, SPRITE_FRAME_H = 16, 18

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# -----------------------------------------------------------------------------
# Helper functions and sprite handling
# -----------------------------------------------------------------------------
def load_sprite_frames(path, frame_w, frame_h):
    """Load a sprite sheet and return scaled frames."""
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    rows = sheet.get_height() // frame_h
    cols = sheet.get_width() // frame_w
    for j in range(rows):
        for i in range(cols):
            frame = sheet.subsurface((i * frame_w, j * frame_h, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
            frames.append(frame)
    return frames

def draw_background(surface):
    """Draw a simple gradient sky and ground."""
    sky_top = (20, 20, 80)
    sky_bottom = (255, 140, 0)
    for y in range(HEIGHT - FLOOR_HEIGHT):
        ratio = y / (HEIGHT - FLOOR_HEIGHT)
        r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * ratio)
        g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * ratio)
        b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    pygame.draw.rect(surface, (60, 40, 20), (0, HEIGHT - FLOOR_HEIGHT, WIDTH, FLOOR_HEIGHT))

def draw_health_bar(surface, x, y, pct, color):
    pygame.draw.rect(surface, BLACK, (x - 2, y - 2, 204, 24), 2)
    pygame.draw.rect(surface, color, (x, y, int(200 * pct), 20))

class Player:
    def __init__(self, x, y, sprite_colors, controls, facing_right=True):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.body_color, self.pants_color = sprite_colors
        self.frames = load_sprite_frames(SPRITE_SHEET, SPRITE_FRAME_W, SPRITE_FRAME_H)
        self.sprite = self.frames[0]
        self.controls = controls
        self.facing_right = facing_right
        self.vel_y = 0
        self.on_ground = True
        self.health = 100
        self.attack_cooldown = 0
        self.attack_effect_timer = 0
        self.remote_cooldown = 0
        self.projectiles = []

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
            self.attack_effect_timer = 10
        if self.controls.get('ranged') and keys[self.controls['ranged']] and self.remote_cooldown == 0:
            proj_x = self.rect.right if self.facing_right else self.rect.left - 10
            self.projectiles.append(Projectile(proj_x, self.rect.centery, self.facing_right, self.body_color))
            self.remote_cooldown = FPS
        # keep inside screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def update(self):
        # gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - FLOOR_HEIGHT:
            self.rect.bottom = HEIGHT - FLOOR_HEIGHT
            self.vel_y = 0
            self.on_ground = True
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.remote_cooldown > 0:
            self.remote_cooldown -= 1
        if self.attack_effect_timer > 0:
            self.attack_effect_timer -= 1
        for p in list(self.projectiles):
            p.update()
            if p.off_screen():
                self.projectiles.remove(p)

    def draw(self, surface):
        image = self.sprite
        if self.attack_effect_timer > 0:
            image = self.frames[1 % len(self.frames)]
        else:
            image = self.frames[0]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, self.rect.topleft)
        if self.attack_effect_timer > 0:
            effect = pygame.Rect(0, 0, ATTACK_RANGE, PLAYER_HEIGHT // 2)
            if self.facing_right:
                effect.midleft = (self.rect.right, self.rect.centery)
            else:
                effect.midright = (self.rect.left, self.rect.centery)
            pygame.draw.rect(surface, YELLOW, effect)
        for p in self.projectiles:
            p.draw(surface)

    def attack(self, other):
        if self.attack_cooldown == FPS - 1:  # attack triggers once when cooldown starts
            hitbox = self.rect.inflate(ATTACK_RANGE, 0)
            if self.facing_right:
                hitbox.left = self.rect.right
            else:
                hitbox.right = self.rect.left
            if hitbox.colliderect(other.rect):
                other.health = max(0, other.health - 10)

    def check_projectiles(self, other):
        for p in list(self.projectiles):
            if p.rect.colliderect(other.rect):
                other.health = max(0, other.health - 5)
                self.projectiles.remove(p)

class Projectile:
    def __init__(self, x, y, facing_right, color):
        self.rect = pygame.Rect(x, y - 5, 10, 10)
        self.speed = 7 if facing_right else -7
        self.color = color

    def update(self):
        self.rect.x += self.speed

    def off_screen(self):
        return self.rect.right < 0 or self.rect.left > WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


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
        'ranged': pygame.K_g,
    }
    controls2 = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'attack': pygame.K_l,
        'ranged': pygame.K_o,
    }

    player1 = Player(
        100,
        HEIGHT - PLAYER_HEIGHT - FLOOR_HEIGHT,
        (BLUE, YELLOW),
        controls1,
        facing_right=True,
    )
    player2 = Player(
        WIDTH - 160,
        HEIGHT - PLAYER_HEIGHT - FLOOR_HEIGHT,
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
        player1.check_projectiles(player2)
        player2.check_projectiles(player1)

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