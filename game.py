import pygame
import sys

# Initialize pygame
pygame.init()
# DEFINING SCREEN
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 3
CELL_SIZE = 120

# pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GOBBLET JR.")

GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
GRID_OFFSET_X = (WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_HEIGHT) // 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
YELLOW = (255, 255, 0)  # For highlighting valid moves

# DEFINING BACKGROUND
background = pygame.image.load("./images/background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# DEFINING PIECE SIZES
SMALL = 1
MEDIUM = 2
LARGE = 3
# Initialize the game state
grid = [[[] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
current_player = 1  # 1 is BLUE, 2 is ORANGE

# Load and scale piece images
orange_small = pygame.image.load("./images/pieces/orange_small.png").convert_alpha()
orange_medium = pygame.image.load("./images/pieces/orange_mid.png").convert_alpha()
orange_large = pygame.image.load("./images/pieces/orange_large.png").convert_alpha()

blue_small = pygame.image.load("./images/pieces/blue_small.png").convert_alpha()
blue_mid = pygame.image.load("./images/pieces/blue_mid.png").convert_alpha()
blue_large = pygame.image.load("./images/pieces/blue_large.png").convert_alpha()

# Scale factors
orange_small = pygame.transform.scale(orange_small, (int(orange_small.get_width() * 0.7), int(orange_small.get_height() * 0.65)))
orange_medium = pygame.transform.scale(orange_medium, (int(orange_medium.get_width() * 0.7), int(orange_medium.get_height() * 0.65)))
orange_large = pygame.transform.scale(orange_large, (int(orange_large.get_width() * 0.7), int(orange_large.get_height() * 0.65)))

blue_small = pygame.transform.scale(blue_small, (int(blue_small.get_width() * 0.7), int(blue_small.get_height() * 0.65)))
blue_mid = pygame.transform.scale(blue_mid, (int(blue_mid.get_width() * 0.7), int(blue_mid.get_height() * 0.65)))
blue_large = pygame.transform.scale(blue_large, (int(blue_large.get_width() * 0.7), int(blue_large.get_height() * 0.65)))

# For piece selection and movement
selected_piece = None
selected_piece_x, selected_piece_y = None, None
valid_moves = []  # List to store valid move positions for selected piece

# UI text
font = pygame.font.Font(None, 35)
blue_team_text = font.render("TEAM BLUE", True, (0, 0, 255))
orange_team_text = font.render("TEAM ORANGE", True, (255, 165, 0))
message_font = pygame.font.Font(None, 28)
message_text = None
message_timer = 0

# Turn indicator
font_turn = pygame.font.Font(None, 65)

class Piece:
    """Represents a game piece with size and color."""
    def __init__(self, x, y, size, image, player):
        self.x = x
        self.y = y
        self.size = size
        self.image = image
        self.is_selected = False
        self.held = False
        self.player = player  # Track which player owns this piece
        self.on_board = False  # Track if the piece is on the board
        self.grid_pos = None  # Track position on grid when placed
        self.visible = True  # Control visibility (for stacking)

    def draw(self, screen):
        """Draws the piece on the given surface."""
        if self.visible:
            screen.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))

# Create player pieces
player1_pieces = [
    Piece(100, 200, SMALL, blue_small, 1), Piece(150, 200, SMALL, blue_small, 1),
    Piece(90, 280, MEDIUM, blue_mid, 1), Piece(150, 280, MEDIUM, blue_mid, 1),
    Piece(85, 400, LARGE, blue_large, 1), Piece(160, 400, LARGE, blue_large, 1),
]

player2_pieces = [
    Piece(660, 200, SMALL, orange_small, 2), Piece(710, 200, SMALL, orange_small, 2),
    Piece(660, 280, MEDIUM, orange_medium, 2), Piece(720, 280, MEDIUM, orange_medium, 2),
    Piece(655, 400, LARGE, orange_large, 2), Piece(740, 400, LARGE, orange_large, 2),
]

# Dictionary to store pieces on the board, organized by position
board_pieces = {}  # Format: {(row, col): [piece1, piece2, ...]} (in stacking order)

def can_place_piece(row, col, size):
    """Check if a piece can be placed at the given position based on its size."""
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return False
    
    pos = (row, col)
    if pos not in board_pieces or not board_pieces[pos]:
        return True  # Empty cell, can place any piece
    
    top_piece = board_pieces[pos][-1]  # Get the top piece at this position
    return size > top_piece.size  # Can place larger pieces on top of smaller ones

def get_valid_moves(piece):
    """Get all valid moves for a piece."""
    moves = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if can_place_piece(row, col, piece.size):
                moves.append((row, col))
    return moves

def draw_valid_moves():
    """Highlight valid move positions on the grid."""
    for row, col in valid_moves:
        x = GRID_OFFSET_X + col * CELL_SIZE
        y = GRID_OFFSET_Y + row * CELL_SIZE
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((255, 255, 0, 60))  # Yellow with alpha
        screen.blit(s, (x, y))


def draw_pieces():
    """Draw all pieces on the screen."""
    for piece in player1_pieces + player2_pieces:
        if not piece.on_board or piece.held:
            piece.draw(screen)
    
    for pos, stack in board_pieces.items():
        if stack and stack[-1].held:
            continue
        if stack:
            stack[-1].draw(screen)

def draw_board():
    """Draw the game board."""
    screen.blit(background, (0, 0))
    for i in range(1, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y),
                         (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT), 5)
        pygame.draw.line(screen, WHITE, (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE),
                         (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + i * CELL_SIZE), 5)
    pygame.draw.rect(screen, WHITE, (GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT), 5)

def move_piece(mouse_pos):
    """Select a piece at the given mouse position"""
    global selected_piece_x, selected_piece_y

    # First check board pieces (top pieces only)
    for pos, stack in board_pieces.items():
        if not stack:
            continue

        piece = stack[-1]  # Get the top piece
        piece_rect = pygame.Rect(
            piece.x - piece.image.get_width() // 2,
            piece.y - piece.image.get_height() // 2,
            piece.image.get_width(),
            piece.image.get_height()
        )

        if piece_rect.collidepoint(mouse_pos):
            # Calculate position relative to the piece's top left
            rel_x = mouse_pos[0] - (piece.x - piece.image.get_width() // 2)
            rel_y = mouse_pos[1] - (piece.y - piece.image.get_height() // 2)

            # Check if we clicked on a non-transparent part of the image
            if 0 <= rel_x < piece.image.get_width() and 0 <= rel_y < piece.image.get_height():
                pixel_color = piece.image.get_at((rel_x, rel_y))
                if pixel_color[3] > 0:  # Not transparent
                    selected_piece_x, selected_piece_y = piece.x, piece.y
                    return piece

    # Then check pieces off the board
    for piece in reversed(player1_pieces + player2_pieces):
        if piece.on_board:
            continue  # Skip pieces already on the board

        piece_rect = pygame.Rect(
            piece.x - piece.image.get_width() // 2,
            piece.y - piece.image.get_height() // 2,
            piece.image.get_width(),
            piece.image.get_height()
        )

        if piece_rect.collidepoint(mouse_pos):
            # Calculate position relative to the piece's top left
            rel_x = mouse_pos[0] - (piece.x - piece.image.get_width() // 2)
            rel_y = mouse_pos[1] - (piece.y - piece.image.get_height() // 2)

            # Check if we clicked on a non-transparent part of the image
            if 0 <= rel_x < piece.image.get_width() and 0 <= rel_y < piece.image.get_height():
                pixel_color = piece.image.get_at((rel_x, rel_y))
                if pixel_color[3] > 0:  # Not transparent
                    selected_piece_x, selected_piece_y = piece.x, piece.y
                    return piece

    return None

def get_grid_position(mouse_x, mouse_y):
    """Convert mouse coordinates to grid row and column"""
    if (GRID_OFFSET_X <= mouse_x <= GRID_OFFSET_X + GRID_WIDTH and
        GRID_OFFSET_Y <= mouse_y <= GRID_OFFSET_Y + GRID_HEIGHT):
        row = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
        col = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
        return row, col
    return None, None

def move_piece_to_grid(piece, row, col):
    """Move a piece to a grid cell"""
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return False

    if not can_place_piece(row, col, piece.size):
        return False

    # Remove piece from its old position if it was on the board
    if piece.on_board and piece.grid_pos:
        old_row, old_col = piece.grid_pos
        old_pos = (old_row, old_col)

        if old_pos in board_pieces and piece in board_pieces[old_pos]:
            board_pieces[old_pos].remove(piece)

            # Update the board state
            if not board_pieces[old_pos]:
                board[old_row][old_col] = None
            else:
                board[old_row][old_col] = board_pieces[old_pos][-1].player

    # Place the piece on the grid
    piece.x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
    piece.y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

    # Update the board_pieces dictionary
    pos = (row, col)
    if pos not in board_pieces:
        board_pieces[pos] = []

    board_pieces[pos].append(piece)

    # Update the board state
    board[row][col] = piece.player

    # Update piece tracking data
    piece.on_board = True
    piece.grid_pos = (row, col)

    return True

def switch_turn():
    """Switch to the next player's turn"""
    global current_player
    current_player = 3 - current_player  # Toggle between 1 and 2

def check_winner():
    """Check if there is a winner"""
    # Check rows
    for row in range(GRID_SIZE):
        if (board[row][0] is not None and
            board[row][0] == board[row][1] == board[row][2]):
            return board[row][0]

    # Check columns
    for col in range(GRID_SIZE):
        if (board[0][col] is not None and
            board[0][col] == board[1][col] == board[2][col]):
            return board[0][col]

    # Check diagonals
    if (board[0][0] is not None and
        board[0][0] == board[1][1] == board[2][2]):
        return board[0][0]

    if (board[0][2] is not None and
        board[0][2] == board[1][1] == board[2][0]):
        return board[0][2]

    return None

def draw_blinking_text(screen, current_player):
    """Draw blinking text indicating current player's turn"""
    time_now = pygame.time.get_ticks()
    if (time_now // 500) % 2 == 0:  # Blink every 500ms
        text = f"Player {current_player}'s Turn"
        color = NEON_BLUE if current_player == 1 else NEON_PINK
        glow_color = (max(color[0] // 2, 0), max(color[1] // 2, 0), max(color[2] // 2, 0))  # Darker glow

        turn_text = font_turn.render(text, True, color)
        glow_text = font_turn.render(text, True, glow_color)

        x = WIDTH // 2 - turn_text.get_width() // 2
        y = HEIGHT - 60

        # Draw glow effect
        screen.blit(glow_text, (x - 2, y - 2))
        screen.blit(glow_text, (x - 2, y + 2))
        screen.blit(glow_text, (x + 2, y - 2))
        screen.blit(glow_text, (x + 2, y + 2))

        # Draw main text
        screen.blit(turn_text, (x, y))

def show_game_message(message, duration=2000):
    """Display a temporary message on screen"""
    global message_text, message_timer
    message_text = message_font.render(message, True, YELLOW)
    message_timer = pygame.time.get_ticks() + duration

def draw_game_message():
    """Draw the current game message if active"""
    if message_text and pygame.time.get_ticks() < message_timer:
        # Draw message with background
        message_bg = pygame.Surface((message_text.get_width() + 20, message_text.get_height() + 10))
        message_bg.set_alpha(150)
        message_bg.fill(BLACK)

        screen.blit(message_bg, (WIDTH // 2 - message_bg.get_width() // 2, 20))
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, 25))

def show_winner(winner):
    """Display the winner and prompt for restart"""
    screen.fill(BLACK)

    winner_text = "BLUE WINS!" if winner == 1 else "ORANGE WINS!"
    color = NEON_BLUE if winner == 1 else NEON_PINK

    text = font_turn.render(winner_text, True, color)
    restart_text = font.render("Click anywhere to restart", True, WHITE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

def reset_game():
    """Reset the game to its initial state"""
    global grid, board, board_pieces, current_player, game_over, valid_moves, message_text, message_timer

    grid = [[[] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    board_pieces = {}
    current_player = 1
    game_over = False
    valid_moves = []
    message_text = None
    message_timer = 0

    # Reset blue pieces positions
    positions = [(100, 200), (150, 200), (90, 280), (150, 280), (85, 400), (160, 400)]
    for i, piece in enumerate(player1_pieces):
        piece.x, piece.y = positions[i]
        piece.on_board = False
        piece.grid_pos = None
        piece.held = False
        piece.visible = True

    # Reset orange pieces positions
    positions = [(660, 200), (710, 200), (660, 280), (720, 280), (655, 400), (740, 400)]
    for i, piece in enumerate(player2_pieces):
        piece.x, piece.y = positions[i]
        piece.on_board = False
        piece.grid_pos = None
        piece.held = False
        piece.visible = True

def has_any_valid_moves(piece):
    """Check if the piece has any valid moves"""
    return len(get_valid_moves(piece)) > 0

# Main game loop
running = True
game_over = False
winner = None

while running:
    """
    Main game loop for Gobblet Jr.
    """
    if not game_over:
        draw_board()

        # Display team labels
        screen.blit(blue_team_text, (45, 130))
        screen.blit(orange_team_text, (600, 130))

        # Draw valid moves highlight if a piece is selected
        if selected_piece:
            draw_valid_moves()

        draw_pieces()
        draw_blinking_text(screen, current_player)
        draw_game_message()
    else:
        show_winner(winner)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
            # Restart the game when clicking after game over
            reset_game()

        elif not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Try to select a piece if none is already selected
                if not selected_piece:
                    piece = move_piece((mouse_x, mouse_y))
                    if piece and piece.player == current_player:
                        # Check if the piece has any valid moves before selecting
                        valid_moves = get_valid_moves(piece)
                        if valid_moves:
                            selected_piece = piece
                            selected_piece.held = True
                            show_game_message("Touch-move rule: You must move this piece!")
                        else:
                            show_game_message("This piece has no valid moves!")

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    selected_piece.held = False
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    row, col = get_grid_position(mouse_x, mouse_y)

                    if row is not None and col is not None and (row, col) in valid_moves:
                        # Try to place the piece on the grid
                        if move_piece_to_grid(selected_piece, row, col):
                            # Check for a winner
                            winner = check_winner()
                            if winner:
                                game_over = True
                            else:
                                switch_turn()
                                valid_moves = []  # Clear valid moves after placing
                                selected_piece = None
                    else:
                        # If dropped in an invalid position, keep the piece selected
                        # The player must make a valid move with the selected piece
                        selected_piece.x = mouse_x
                        selected_piece.y = mouse_y
                        selected_piece.held = True
                        show_game_message("You must place this piece on a valid spot!")

            elif event.type == pygame.MOUSEMOTION:
                if selected_piece and selected_piece.held:
                    # Move the selected piece with the mouse
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    selected_piece.x = mouse_x
                    selected_piece.y = mouse_y

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # Limit to 60 FPS

pygame.quit()
sys.exit()
