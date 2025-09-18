"""
game.py
Retro-style vertical lane car dodger in black & white using Pygame.

Features:
- Vertical screen (taller than wide)
- Black background, white game elements
- Player car snaps between lanes using LEFT/RIGHT arrow keys
- Enemy cars spawn in lanes and move downward; speed ramps up
- Score increments when an enemy passes off-screen (avoided)
- Start screen ("Press any key to start")
- Game Over screen with final score and restart via Enter/Space
- Single-file, uses classes and functions, well commented

Run:
    python game.py
"""

import pygame
import random
import sys

# -----------------------------
# Constants / Configuration
# -----------------------------
SCREEN_WIDTH = 360              # narrow width (vertical orientation)
SCREEN_HEIGHT = 640             # taller height
FPS = 60

LANE_COUNT = 3                  # number of lanes
LANE_PADDING = 20               # left/right pad for lane area

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

ENEMY_WIDTH = 40
ENEMY_HEIGHT = 60

SPAWN_INTERVAL_INITIAL = 900    # milliseconds between spawns (will decrease to increase difficulty)
SPEED_INITIAL = 3.0             # initial enemy speed (pixels/frame)
SPEED_INCREASE_PER_SCORE = 0.05 # how much enemy speed increases per score increment

FONT_NAME = None                # default system font

# Colors (black & white style)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

# -----------------------------
# Helper functions
# -----------------------------
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# -----------------------------
# Car class - used for both player and enemies
# -----------------------------
class Car:
    def __init__(self, x, y, width, height, lane_index=0, is_player=False):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.lane_index = lane_index
        self.is_player = is_player
        # rectangle used for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update_rect(self):
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface):
        # Draw the car as a white rectangle with a thin border to look "retro"
        pygame.draw.rect(surface, WHITE, self.rect)
        # add inner shading rectangle for a little visual variety (still monochrome)
        inner = self.rect.inflate(-6, -8)
        pygame.draw.rect(surface, BLACK, inner)

# -----------------------------
# Game class - main game logic
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Retro Lane Dodger")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.large_font = pygame.font.SysFont(FONT_NAME, 48)
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)

        # Precompute lane X centers (snap positions)
        lane_width = (SCREEN_WIDTH - 2 * LANE_PADDING) / LANE_COUNT
        self.lane_centers = [
            LANE_PADDING + lane_width * i + lane_width / 2 - PLAYER_WIDTH / 2
            for i in range(LANE_COUNT)
        ]

        # Game state
        self.running = True
        self.state = "START"  # other values: "PLAYING", "GAMEOVER"

        # initialize/reset gameplay variables
        self.reset_game_state()

    def reset_game_state(self):
        """Reset or initialize variables used while playing (not UI state)."""
        self.player_lane = LANE_COUNT // 2  # start in middle lane
        px = self.lane_centers[self.player_lane]
        py = SCREEN_HEIGHT - PLAYER_HEIGHT - 30
        self.player = Car(px, py, PLAYER_WIDTH, PLAYER_HEIGHT, lane_index=self.player_lane, is_player=True)

        self.enemies = []            # list of Car objects (enemies)
        self.score = 0
        self.enemy_speed = SPEED_INITIAL
        self.spawn_interval = SPAWN_INTERVAL_INITIAL
        self.last_spawn_time = pygame.time.get_ticks()
        self.last_score_check = pygame.time.get_ticks()

        # minor control guard to avoid continuous rapid lane changes if key held
        self.can_move = True

    def spawn_enemy(self):
        """Spawn a single enemy in a random lane at the top of the screen."""
        lane = random.randrange(LANE_COUNT)
        ex = self.lane_centers[lane]
        ey = -ENEMY_HEIGHT - 10  # start just above the screen
        enemy = Car(ex, ey, ENEMY_WIDTH, ENEMY_HEIGHT, lane_index=lane, is_player=False)
        self.enemies.append(enemy)

    def handle_input_start_screen(self, event):
        """Start screen: press any key to start playing."""
        if event.type == pygame.KEYDOWN:
            # any key begins the game
            self.state = "PLAYING"
            self.reset_game_state()

    def handle_input_game(self, event):
        """Handle input while the game is playing."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # move left one lane
                self.player_lane = clamp(self.player_lane - 1, 0, LANE_COUNT - 1)
                self.player.x = self.lane_centers[self.player_lane]
                self.player.update_rect()
            elif event.key == pygame.K_RIGHT:
                # move right one lane
                self.player_lane = clamp(self.player_lane + 1, 0, LANE_COUNT - 1)
                self.player.x = self.lane_centers[self.player_lane]
                self.player.update_rect()
            elif event.key == pygame.K_ESCAPE:
                # allow quitting with ESC
                self.running = False

    def handle_input_gameover(self, event):
        """Game over screen: restart if Enter or Space."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "PLAYING"
                self.reset_game_state()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def update_enemies(self, dt):
        """
        Move enemies downward, remove off-screen ones and increment score
        when player successfully avoids them.
        dt: time elapsed in milliseconds since last frame (unused for now but kept for extensibility).
        """
        to_remove = []
        for enemy in self.enemies:
            enemy.y += self.enemy_speed  # constant per frame speed (FPS-based)
            enemy.update_rect()
            # if enemy passed bottom => player avoided it
            if enemy.y > SCREEN_HEIGHT:
                to_remove.append(enemy)
                self.score += 1
                # increase speed gradually based on score
                self.enemy_speed = SPEED_INITIAL + self.score * SPEED_INCREASE_PER_SCORE
                # optionally make spawn faster (increase difficulty)
                # clamp spawn interval so it doesn't get ridiculously small
                self.spawn_interval = clamp(SPAWN_INTERVAL_INITIAL - int(self.score * 10), 300, SPAWN_INTERVAL_INITIAL)

        for e in to_remove:
            if e in self.enemies:
                self.enemies.remove(e)

    def check_collisions(self):
        """Check if player's rect collides with any enemy rect."""
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                return True
        return False

    def draw_hud(self):
        """Draw the score at top-left corner."""
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

    def draw_lanes(self):
        """Draw subtle lane separators to show lanes (monochrome)."""
        lane_width = (SCREEN_WIDTH - 2 * LANE_PADDING) / LANE_COUNT
        for i in range(1, LANE_COUNT):
            x = int(LANE_PADDING + lane_width * i)
            # dashed line effect: draw short segments
            seg_h = 10
            gap = 8
            y = 40
            while y < SCREEN_HEIGHT - 40:
                pygame.draw.line(self.screen, GRAY, (x, y), (x, y + seg_h), 2)
                y += seg_h + gap

    def draw_start_screen(self):
        self.screen.fill(BLACK)
        title = self.large_font.render("RETRO DODGER", True, WHITE)
        prompt = self.font.render("Press any key to start", True, WHITE)
        subtitle = self.small_font.render("Left / Right arrows to move  •  Avoid incoming cars", True, WHITE)

        # center title
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.35)))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.55)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.62)))

        # draw a sample player car preview
        preview = Car(self.lane_centers[LANE_COUNT//2], SCREEN_HEIGHT * 0.75, PLAYER_WIDTH, PLAYER_HEIGHT)
        preview.update_rect()
        preview.draw(self.screen)

    def draw_gameover_screen(self):
        self.screen.fill(BLACK)
        go_text = self.large_font.render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        prompt = self.font.render("Press Enter or Space to restart", True, WHITE)
        exit_prompt = self.small_font.render("Press ESC to quit", True, WHITE)

        self.screen.blit(go_text, go_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.35)))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.5)))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.62)))
        self.screen.blit(exit_prompt, exit_prompt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.7)))

    def run(self):
        """Main loop of the game."""
        while self.running:
            dt = self.clock.tick(FPS)  # milliseconds since last frame

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "START":
                    self.handle_input_start_screen(event)
                elif self.state == "PLAYING":
                    self.handle_input_game(event)
                elif self.state == "GAMEOVER":
                    self.handle_input_gameover(event)

            # State updates
            if self.state == "PLAYING":
                # spawn logic based on time
                now = pygame.time.get_ticks()
                if now - self.last_spawn_time >= self.spawn_interval:
                    self.spawn_enemy()
                    self.last_spawn_time = now

                # update enemies movement
                self.update_enemies(dt)

                # update player's rect (in case lane changed)
                self.player.update_rect()

                # collision check
                if self.check_collisions():
                    self.state = "GAMEOVER"

            # Rendering
            if self.state == "START":
                self.draw_start_screen()
            elif self.state == "PLAYING":
                # background
                self.screen.fill(BLACK)

                # lanes lines
                self.draw_lanes()

                # draw player
                self.player.draw(self.screen)

                # draw enemies
                for enemy in self.enemies:
                    enemy.draw(self.screen)

                # HUD (score)
                self.draw_hud()

            elif self.state == "GAMEOVER":
                self.draw_gameover_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    Game().run()
