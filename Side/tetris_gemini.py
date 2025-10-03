import pygame
import random
import time

# --- Game Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100) # Used for the grid lines

# Grid and Block Dimensions (10x20 standard Tetris grid)
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30 # Blocks will be 30x30 pixels
PLAY_AREA_WIDTH = GRID_WIDTH * BLOCK_SIZE  # 300
PLAY_AREA_HEIGHT = GRID_HEIGHT * BLOCK_SIZE # 600

# Calculate the top-left corner of the playable grid area to center it horizontally
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_AREA_WIDTH) // 2
TOP_LEFT_Y = 0

# Timing and Difficulty
FALL_TIME = 0.5  # Time in seconds for the piece to drop one unit
SCORE_FONT_SIZE = 30
GAME_OVER_FONT_SIZE = 50

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Tetris")
font = pygame.font.Font(None, SCORE_FONT_SIZE)
game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
clock = pygame.time.Clock()

# --- Tetromino Shapes (White blocks) ---
# Each piece is defined by a list of 4x4 matrices representing its rotations.
# The '0' in the matrix represents a block.

S = [['..0.',
      '.00.',
      '.0..',
      '....'],
     ['.0..',
      '.00.',
      '..0.',
      '....']]

Z = [['.0..',
      '.00.',
      '..0.',
      '....'],
     ['..0.',
      '.00.',
      '.0..',
      '....']]

I = [['.0..',
      '.0..',
      '.0..',
      '.0..'],
     ['....',
      '0000',
      '....',
      '....']]

O = [['....',
      '.00.',
      '.00.',
      '....']] # O-piece only has one rotation

J = [['.0..',
      '.000',
      '....',
      '....'],
     ['..0.',
      '..0.',
      '.00.',
      '....'],
     ['000.',
      '..0.',
      '....',
      '....'],
     ['.00.',
      '.0..',
      '.0..',
      '....']]

L = [['..0.',
      '000.',
      '....',
      '....'],
     ['.0..',
      '.0..',
      '.00.',
      '....'],
     ['000.',
      '0...',
      '....',
      '....'],
     ['.00.',
      '..0.',
      '..0.',
      '....']]

T = [['.0..',
      '000.',
      '....',
      '....'],
     ['.0..',
      '.00.',
      '.0..',
      '....'],
     ['000.',
      '.0..',
      '....',
      '....'],
     ['..0.',
      '.00.',
      '..0.',
      '....']]

SHAPES = [S, Z, I, O, J, L, T]

# --- Core Game Functions ---

def create_grid(locked_positions):
    """Initializes the main game board (2D list) filled with black cells."""
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # Fill in the locked positions with the WHITE color
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = WHITE
    return grid

def convert_shape_format(shape):
    """Converts the string matrix format of a piece into a list of (x, y) grid coordinates."""
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    
    # Iterate through the 4x4 block
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Map 4x4 coordinate (i, j) to grid coordinate (x, y)
                positions.append((shape.x + j, shape.y + i))
                
    return positions

def valid_space(shape, grid):
    """Checks if the piece's current position is valid (within bounds and not colliding with locked blocks)."""
    # Create a set of all positions currently occupied by settled blocks
    accepted_pos = set([(j, i) for j in range(GRID_WIDTH) for i in range(GRID_HEIGHT) if grid[i][j] == WHITE])
    
    formatted = convert_shape_format(shape)

    for x, y in formatted:
        if y >= GRID_HEIGHT or x < 0 or x >= GRID_WIDTH:
            # Out of boundary
            return False
        if (x, y) in accepted_pos:
            # Collision with a locked block
            return False
        if y < 0:
            # Only check for out of bounds on the bottom, not the top
            continue
            
    return True

def check_lost(positions):
    """Checks if the player has lost (a locked block is above the top of the screen)."""
    for x, y in positions:
        if y < 1: # If any block is in row 0 or higher
            return True
    return False

def get_shape():
    """Returns a new random piece object."""
    return Piece(5, 0, random.choice(SHAPES))

def draw_grid_lines(surface):
    """Draws the thin gray lines on the grid for visual separation."""
    for i in range(GRID_HEIGHT):
        # Horizontal lines
        pygame.draw.line(surface, GRAY, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), 
                         (TOP_LEFT_X + PLAY_AREA_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
    for j in range(GRID_WIDTH):
        # Vertical lines
        pygame.draw.line(surface, GRAY, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), 
                         (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_AREA_HEIGHT))

def draw_window(surface, grid, score):
    """Draws the main game window, including the grid, blocks, and score."""
    surface.fill(BLACK)
    
    # Draw title
    show_message("RETRO TETRIS", 40, 20)
    
    # Draw score
    score_surface = font.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surface, (TOP_LEFT_X + PLAY_AREA_WIDTH + 10, 200))

    # Draw the blocks in the grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == WHITE:
                pygame.draw.rect(surface, WHITE, 
                                 (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, 
                                  BLOCK_SIZE, BLOCK_SIZE), 0) # 0 means filled

    # Draw the main playing boundary
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), 5)
    
    # Draw the grid lines *inside* the boundary
    draw_grid_lines(surface)
    
    pygame.display.update()

def clear_rows(grid, locked_positions):
    """Checks for and clears any full rows, updating the grid and locked_positions."""
    increment = 0
    y_index = GRID_HEIGHT - 1
    while y_index >= 0:
        if BLACK not in grid[y_index]:
            # Found a full row!
            increment += 1
            # Remove positions from locked_positions dictionary for this row
            for x in range(GRID_WIDTH):
                try:
                    del locked_positions[(x, y_index)]
                except:
                    continue

            # Shift all blocks above this line down by 1 unit
            # Shift blocks in the locked_positions dictionary
            new_locked_positions = {}
            for (x, y), color in locked_positions.items():
                if y < y_index:
                    new_locked_positions[(x, y + 1)] = color
                else:
                    new_locked_positions[(x, y)] = color
            
            locked_positions.clear()
            locked_positions.update(new_locked_positions)

            # Re-create the grid with the new locked positions
            grid = create_grid(locked_positions)
            
            # Note: We don't decrement y_index here because the row above it has moved down
        else:
            y_index -= 1 # Move up to the next row
            
    return increment, grid

def show_message(text, size, y_pos, color=WHITE):
    """Helper function to render and display text on the screen."""
    message_font = pygame.font.Font(None, size)
    message_surface = message_font.render(text, True, color)
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
    screen.blit(message_surface, message_rect)

def main_menu_screen():
    """Displays the main menu screen."""
    screen.fill(BLACK)
    show_message("RETRO TETRIS", 60, SCREEN_HEIGHT // 3)
    show_message("Press any key to start", 30, SCREEN_HEIGHT // 2)
    pygame.display.flip()

def game_over_screen(score):
    """Displays the game over screen with the final score and restart prompt."""
    screen.fill(BLACK)
    show_message("GAME OVER", GAME_OVER_FONT_SIZE, SCREEN_HEIGHT // 3)
    show_message(f"Final Score: {score}", FONT_SIZE, SCREEN_HEIGHT // 2)
    show_message("Press Enter or Space to restart", 25, (SCREEN_HEIGHT // 2) + 50)
    pygame.display.flip()

# --- Classes ---

class Piece(object):
    """
    Represents a falling Tetris piece.
    """
    def __init__(self, x, y, shape):
        self.x = x             # Grid column index
        self.y = y             # Grid row index
        self.shape = shape     # The list of 4x4 matrices defining the piece
        self.rotation = 0      # Index of the current rotation
        self.color = WHITE     # All blocks are white

def main():
    """Main function to run the Tetris game loop."""
    running = True
    game_state = STATE_MENU
    score = 0
    
    # Dictionary to store settled blocks: {(x, y): color}
    locked_positions = {} 
    
    current_piece = get_shape()
    fall_speed = FALL_TIME
    last_fall_time = time.time()
    
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
                        current_piece.x -= 1
                        if not valid_space(current_piece, create_grid(locked_positions)):
                            current_piece.x += 1 # Move back if invalid
                    
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, create_grid(locked_positions)):
                            current_piece.x -= 1 # Move back if invalid
                            
                    elif event.key == pygame.K_UP: # Rotate the piece
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                        if not valid_space(current_piece, create_grid(locked_positions)):
                            current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape) # Revert rotation
                            
                    elif event.key == pygame.K_DOWN: # Soft drop (speed up fall)
                        current_piece.y += 1
                        if not valid_space(current_piece, create_grid(locked_positions)):
                            current_piece.y -= 1
                    
                    elif event.key == pygame.K_SPACE: # Hard drop (instant lock)
                        while valid_space(current_piece, create_grid(locked_positions)):
                            current_piece.y += 1
                        current_piece.y -= 1 # Move back one step to be on top of locked blocks
                        # The piece will now lock at the start of the game loop
                        last_fall_time = 0 # Force immediate locking logic

            elif game_state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        # Reset game state
                        game_state = STATE_PLAYING
                        score = 0
                        locked_positions.clear()
                        current_piece = get_shape()
                        last_fall_time = time.time()
                        fall_speed = FALL_TIME

        if game_state == STATE_MENU:
            main_menu_screen()
            continue

        if game_state == STATE_GAME_OVER:
            game_over_screen(score)
            continue

        # --- Game Logic (Playing State) ---
        grid = create_grid(locked_positions)
        
        # 1. Handle Gravity (Automatic Falling)
        if time.time() - last_fall_time > fall_speed:
            current_piece.y += 1
            last_fall_time = time.time()
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1 # Move back
                
                # 2. Lock the piece
                positions = convert_shape_format(current_piece)
                for x, y in positions:
                    locked_positions[(x, y)] = current_piece.color # Lock position
                
                # 3. Spawn new piece
                current_piece = get_shape() 
                
                # 4. Check for lost game
                if not valid_space(current_piece, grid):
                    game_state = STATE_GAME_OVER

        # 5. Draw the current falling piece
        piece_positions = convert_shape_format(current_piece)
        for x, y in piece_positions:
            if y >= 0: # Don't draw blocks above the screen
                # Mark the piece's position in the grid with WHITE for drawing
                # Note: This is temporary, only the locked_positions are permanent in the grid state
                grid[y][x] = current_piece.color 

        # 6. Check and Clear Rows
        lines_cleared, grid = clear_rows(grid, locked_positions)
        if lines_cleared > 0:
            # Score logic: 1 line = 10, 2 = 30, 3 = 60, 4 = 100
            score_multiplier = {1: 10, 2: 30, 3: 60, 4: 100}
            score += score_multiplier.get(lines_cleared, 100) # Use 100 for 4 lines or more

        # 7. Drawing and Updating Screen
        draw_window(screen, grid, score)
        
        # Frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
