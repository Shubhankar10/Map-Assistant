import pygame
import random
import time

# --- Game Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 30
GAME_OVER_FONT_SIZE = 50

# Game properties
NUM_LANES = 3  # New constant for number of lanes

# Player car properties
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_SPEED = 10 # Not used for smooth movement, but good to have
# Dynamically calculate player lanes based on NUM_LANES
# The formula centers the lanes in the available width
PLAYER_LANES = [(SCREEN_WIDTH // (NUM_LANES + 1)) * (i + 1) for i in range(NUM_LANES)]

# Enemy car properties
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 50
ENEMY_SPAWN_INTERVAL = 1.0 # Initial spawn interval in seconds
ENEMY_SPEED_INCREMENT = 0.5 # Speed increase per point
ENEMY_SPAWN_DECREMENT = 0.01 # Spawn interval decrease per point

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Racer")
font = pygame.font.Font(None, FONT_SIZE)
game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
clock = pygame.time.Clock()

# --- Classes ---

class Car(pygame.Rect):
    """
    A simple class representing a car. Inherits from pygame.Rect for easy collision detection.
    """
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)
        self.color = color

    def draw(self, surface):
        """Draws the car on the given surface."""
        pygame.draw.rect(surface, self.color, self)

# --- Functions ---

def draw_lanes():
    """Draws the simple vertical white lanes on the black background."""
    lane_width = 5
    for lane_x in PLAYER_LANES:
        pygame.draw.line(screen, WHITE, (lane_x, 0), (lane_x, SCREEN_HEIGHT), lane_width)

def show_message(text, size, y_pos, color=WHITE):
    """Helper function to render and display text on the screen."""
    message_font = pygame.font.Font(None, size)
    message_surface = message_font.render(text, True, color)
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(message_surface, message_rect)

def main_menu_screen():
    """Displays the main menu screen."""
    screen.fill(BLACK)
    show_message("Retro Racer", 60, SCREEN_HEIGHT // 3)
    show_message("Press any key to start", 30, SCREEN_HEIGHT // 2)
    pygame.display.flip()

def game_over_screen(score):
    """Displays the game over screen with the final score and restart prompt."""
    screen.fill(BLACK)
    show_message("Game Over", GAME_OVER_FONT_SIZE, SCREEN_HEIGHT // 3)
    show_message(f"Final Score: {score}", FONT_SIZE, SCREEN_HEIGHT // 2)
    show_message("Press Enter or Space to restart", 25, (SCREEN_HEIGHT // 2) + 50)
    pygame.display.flip()

def main():
    """Main function to run the game loop."""
    running = True
    game_state = STATE_MENU
    score = 0
    enemy_speed = 3
    enemies = []
    # Start the player in the middle lane
    player = Car(PLAYER_LANES[NUM_LANES // 2] - PLAYER_WIDTH // 2, SCREEN_HEIGHT - 100, PLAYER_WIDTH, PLAYER_HEIGHT, WHITE)
    
    last_spawn_time = time.time()
    current_spawn_interval = ENEMY_SPAWN_INTERVAL

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    game_state = STATE_PLAYING
            
            elif game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_lane_index = PLAYER_LANES.index(player.centerx)
                        if current_lane_index > 0:
                            player.centerx = PLAYER_LANES[current_lane_index - 1]
                    elif event.key == pygame.K_RIGHT:
                        current_lane_index = PLAYER_LANES.index(player.centerx)
                        if current_lane_index < len(PLAYER_LANES) - 1:
                            player.centerx = PLAYER_LANES[current_lane_index + 1]

            elif game_state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        # Reset game state
                        game_state = STATE_PLAYING
                        score = 0
                        enemy_speed = 3
                        enemies.clear()
                        player.centerx = PLAYER_LANES[NUM_LANES // 2] # Reset to center lane
                        last_spawn_time = time.time()
                        current_spawn_interval = ENEMY_SPAWN_INTERVAL

        if game_state == STATE_MENU:
            main_menu_screen()
            continue

        if game_state == STATE_GAME_OVER:
            game_over_screen(score)
            continue
        
        # --- Game Logic (Playing State) ---
        
        # Enemy spawning
        if time.time() - last_spawn_time > current_spawn_interval:
            lane = random.choice(PLAYER_LANES)
            new_enemy = Car(lane - ENEMY_WIDTH // 2, -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, WHITE)
            enemies.append(new_enemy)
            last_spawn_time = time.time()

        # Update enemies
        for enemy in enemies:
            enemy.y += enemy_speed
        
        # Remove off-screen enemies and update score
        enemies_to_remove = []
        for enemy in enemies:
            if enemy.y > SCREEN_HEIGHT:
                enemies_to_remove.append(enemy)
                score += 1
                # Increase difficulty
                enemy_speed += ENEMY_SPEED_INCREMENT
                current_spawn_interval = max(0.5, current_spawn_interval - ENEMY_SPAWN_DECREMENT)
        
        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        # Collision detection
        for enemy in enemies:
            if player.colliderect(enemy):
                game_state = STATE_GAME_OVER
                break
        
        # --- Drawing ---
        screen.fill(BLACK)
        draw_lanes()
        player.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)
        
        # Display score
        score_surface = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

        # Frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
