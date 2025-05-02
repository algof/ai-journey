import pygame
import numpy as np
import sys
import random
import math

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
BOT = 1
EMPTY = 0
PLAYER_PIECE = 1
BOT_PIECE = 2
WINDOW_LENGTH = 4
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
width = COLUMN_COUNT * SQUARESIZE * 1.5
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BOARD_OFFSET_X = (width - COLUMN_COUNT * SQUARESIZE) // 2
GRAY = (100,100,100)
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four")
myfont = pygame.font.Font(None, 60)  # Adjust size as needed
myfont_small = pygame.font.Font(None, 30)  # Smaller font for instructions or labels
player_color = RED
bot_color = YELLOW


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (BOARD_OFFSET_X + c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (BOARD_OFFSET_X + int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, player_color, (BOARD_OFFSET_X + int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == BOT_PIECE:
                pygame.draw.circle(screen, bot_color, (BOARD_OFFSET_X + int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    pygame.display.update()



def drop_piece(board, row, col, piece):
    board[row][col] = piece


def animate_chip_drop(board, col, piece, color):
    """
    Animates the chip dropping from the top to the target row in the given column.
    """
    row = get_next_open_row(board, col)
    x = col * SQUARESIZE + SQUARESIZE // 2 +  BOARD_OFFSET_X
    y = SQUARESIZE // 2

    # Keep updating the y-coordinate until it reaches the target row position
    while y < (ROW_COUNT - row) * SQUARESIZE + SQUARESIZE // 2:
        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))  # Clear the hover effect
        draw_board(board)
        pygame.draw.circle(screen, color, (x, y), RADIUS)
        pygame.display.update()
        pygame.time.wait(10)  # Adjust this value for faster or slower animation
        y += 20  # Speed of the animation

    # Finally, drop the piece at the target row
    drop_piece(board, row, col, piece)
    draw_board(board)





def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r





def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == BOT_PIECE else BOT_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0


    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3


    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)


    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0


difficulty = "medium"  

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, BOT_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000000000)
            else: 
                return (None, 0)
        else:  
            return (None, score_position(board, BOT_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, BOT_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: 
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def bot_move(board):
    """
    Determines the bot's move based on the selected difficulty level.
    """
    if difficulty == "easy":
        valid_locations = get_valid_locations(board)
        return random.choice(valid_locations) 
    elif difficulty == "medium":
        return minimax(board, 1, -math.inf, math.inf, True)[0]  
    elif difficulty == "hard":
        return minimax(board, 5, -math.inf, math.inf, True)[0]  


def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def select_game_type():
    """
    Allows the user to select the game type: Connect 4, Connect 6, or Connect 8.
    Adjusts the global WINDOW_LENGTH and COLUMN_COUNT variables accordingly.
    """
    global WINDOW_LENGTH, COLUMN_COUNT, size, width, BOARD_OFFSET_X

    screen.fill(BLACK)

    # Render game type options
    text_header = myfont.render("Select Game Type", True, WHITE)
    text_connect_4 = myfont.render("Connect 4", True, GREEN)
    text_connect_6 = myfont.render("Connect 6", True, YELLOW)
    text_connect_8 = myfont.render("Connect 8", True, RED)

    header_x = width // 2 - text_header.get_width() // 2
    header_y = height // 4 - text_header.get_height() // 2
    connect_4_x = width // 6 - text_connect_4.get_width() // 2
    connect_6_x = width // 2 - text_connect_6.get_width() // 2
    connect_8_x = 5 * width // 6 - text_connect_8.get_width() // 2
    option_y = height // 2 - text_connect_4.get_height() // 2

    screen.blit(text_header, (header_x, header_y))
    screen.blit(text_connect_4, (connect_4_x, option_y))
    screen.blit(text_connect_6, (connect_6_x, option_y))
    screen.blit(text_connect_8, (connect_8_x, option_y))
    pygame.display.update()

    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 3:
                    WINDOW_LENGTH = 4
                elif x_pos < 2 * width // 3:
                    WINDOW_LENGTH = 6
                else:
                    WINDOW_LENGTH = 8

                COLUMN_COUNT = max(7, WINDOW_LENGTH + 3)  # Ensure enough columns for larger window sizes

                # Adjust screen dimensions dynamically
                width = COLUMN_COUNT * SQUARESIZE * 1.5
                size = (width, height)
                BOARD_OFFSET_X = (width - COLUMN_COUNT * SQUARESIZE) // 2
                pygame.display.set_mode(size)
                selecting = False

def winning_move(board, piece):
    """
    Check if the given piece has achieved a winning condition based on WINDOW_LENGTH.
    """
    # Check horizontal locations for win
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check positively sloped diagonals
    for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check negatively sloped diagonals
    for r in range(WINDOW_LENGTH - 1, ROW_COUNT):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    return False

def select_difficulty():
    global difficulty
    screen.fill(BLACK)
    text_header = myfont.render("Select Difficulty", True, WHITE)
    text_easy = myfont.render("Easy", True, GREEN)
    text_medium = myfont.render("Medium", True, YELLOW)
    text_hard = myfont.render("Hard", True, RED)

    header_x = width // 2 - text_header.get_width() // 2
    header_y = height // 4 - text_header.get_height() // 2
    easy_x = width // 6 - text_easy.get_width() // 2
    medium_x = width // 2 - text_medium.get_width() // 2
    hard_x = 5 * width // 6 - text_hard.get_width() // 2
    option_y = height // 2 - text_easy.get_height() // 2

    screen.blit(text_header, (header_x, header_y))
    screen.blit(text_easy, (easy_x, option_y))
    screen.blit(text_medium, (medium_x, option_y))
    screen.blit(text_hard, (hard_x, option_y))
    pygame.display.update()

    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 3:
                    difficulty = "easy"
                elif x_pos < 2 * width // 3:
                    difficulty = "medium"
                else:
                    difficulty = "hard"
                selecting = False

def select_color():
    global player_color, bot_color

    screen.fill(BLACK)
    text_header = myfont.render("Select Your Color", True, WHITE)
    text_red = myfont.render("Red", True, RED)
    text_yellow = myfont.render("Yellow", True, YELLOW)


    header_x = width // 2 - text_header.get_width() // 2
    header_y = height // 4 - text_header.get_height() // 2
    red_x = width // 4 - text_red.get_width() // 2
    yellow_x = 3 * width // 4 - text_yellow.get_width() // 2
    option_y = height // 2 - text_red.get_height() // 2


    screen.blit(text_header, (header_x, header_y))
    screen.blit(text_red, (red_x, option_y))
    screen.blit(text_yellow, (yellow_x, option_y))
    pygame.display.update()

    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 2:
                    player_color = RED
                    bot_color = YELLOW
                else:
                    player_color = YELLOW
                    bot_color = RED
                selecting = False

def display_turn_message(turn):
    screen.fill(BLACK)  # Clear the screen
    if turn == PLAYER:
        text = myfont.render("Player First!", True, WHITE)
    else:
        text = myfont.render("Bot First!", True, WHITE)

    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2

    screen.blit(text, (text_x, text_y))
    pygame.display.update()
    pygame.time.wait(1000)  # Display message for 2 seconds

    # Clear the message and prepare for game board
    screen.fill(BLACK)
    draw_board(create_board())  # Draw an empty board to reset visuals



def main():
    select_game_type() 

    select_board_size()

    # Select difficulty
    select_difficulty()

    # Select color
    select_color()

    # Initialize game
    board = create_board()
    game_over = False
    screen.fill(BLACK)
    turn = random.choice([PLAYER, BOT])
    
    # Display who goes first
    display_turn_message(turn)

    draw_board(board)  # Redraw the board after showing the message

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Player turn logic
            if turn == PLAYER:
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))  # Clear hover area
                    posx = event.pos[0]
                    pygame.draw.circle(screen, player_color, (posx, SQUARESIZE // 2), RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    col = int(posx - BOARD_OFFSET_X) // SQUARESIZE  # Adjust column calculation for offset

                    if is_valid_location(board, col):
                                    pygame.time.wait(100)
                                    row = get_next_open_row(board, col)
                                    animate_chip_drop(board, col, PLAYER_PIECE, player_color)

                                    if winning_move(board, PLAYER_PIECE):
                                        game_over = True
                                        display_winner("Player Wins!")
                                    turn = BOT

        # BOT turn logic
        if turn == BOT and not game_over:
            col = bot_move(board) 
        
            if is_valid_location(board, col):
                pygame.time.wait(500)
                row = get_next_open_row(board, col)
                animate_chip_drop(board, col, BOT_PIECE, bot_color)

                if winning_move(board, BOT_PIECE):
                    game_over = True
                    display_winner("Bot Wins!")
                turn = PLAYER

        draw_board(board)


        if game_over:
            pygame.time.wait(1000)
            show_end_buttons()

def select_board_size():
    """
    Allows the user to select the board size (rows and columns).
    Adjusts ROW_COUNT, COLUMN_COUNT, and scaling variables accordingly.
    """
    global ROW_COUNT, COLUMN_COUNT, SQUARESIZE, RADIUS, size, width, height, BOARD_OFFSET_X

    screen.fill(BLACK)

    # Render board size selection instructions
    text_header = myfont.render("Select Board Size", True, WHITE)
    text_instructions = myfont_small.render("Use arrow keys to adjust. Press Enter to confirm.", True, GRAY)

    header_x = width // 2 - text_header.get_width() // 2
    header_y = height // 4 - text_header.get_height() // 2
    instructions_x = width // 2 - text_instructions.get_width() // 2
    instructions_y = header_y + text_header.get_height() + 20

    if WINDOW_LENGTH == 4:
        ROW_COUNT, COLUMN_COUNT = 6, 7  # Default size for Connect 4
    elif WINDOW_LENGTH == 6:
        ROW_COUNT, COLUMN_COUNT = 8, 9  # Default size for Connect 4
    else: 
        ROW_COUNT, COLUMN_COUNT = 10, 11  # Default size for Connect 4
        
    selecting = True
    while selecting:
        screen.fill(BLACK)
        screen.blit(text_header, (header_x, header_y))
        screen.blit(text_instructions, (instructions_x, instructions_y))

        # Display current size
        size_text = myfont.render(f"Rows: {ROW_COUNT}, Columns: {COLUMN_COUNT}", True, WHITE)
        size_x = width // 2 - size_text.get_width() // 2
        size_y = instructions_y + 50
        screen.blit(size_text, (size_x, size_y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and ROW_COUNT < 15:
                    ROW_COUNT += 1
                elif event.key == pygame.K_DOWN and ROW_COUNT > WINDOW_LENGTH + 2:
                    ROW_COUNT -= 1
                elif event.key == pygame.K_RIGHT and COLUMN_COUNT < 15:
                    COLUMN_COUNT += 1
                elif event.key == pygame.K_LEFT and COLUMN_COUNT > WINDOW_LENGTH + 3:
                    COLUMN_COUNT -= 1
                elif event.key == pygame.K_RETURN:
                    selecting = False

    # Adjust scaling based on board size
    SQUARESIZE = min(700 // COLUMN_COUNT, 600 // ROW_COUNT)
    RADIUS = SQUARESIZE // 2 - 5
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)
    BOARD_OFFSET_X = (width - COLUMN_COUNT * SQUARESIZE) // 2
    pygame.display.set_mode(size)

def display_winner(text):
    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
    label = myfont.render(text, True, WHITE)
    screen.blit(label, (width // 2 - label.get_width() // 2, SQUARESIZE // 2 - label.get_height() // 2))
    pygame.display.update()


def show_end_buttons():
    screen.fill(BLACK)
    text_header = myfont.render("Connect Four", True, WHITE)
    text_refresh = myfont.render("Restart", True, BLUE)
    text_quit = myfont.render("Quit", True, RED)
    screen.blit(text_header, (width // 2 - text_header.get_width() // 2,  text_header.get_height() // 2))
    screen.blit(text_refresh, (width // 4 - text_refresh.get_width() // 2 + 30, height // 2 - text_refresh.get_height() // 2))
    screen.blit(text_quit, (3 * width // 4 - text_quit.get_width() // 2 + 30, height // 2 - text_quit.get_height() // 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 2:
                    main()  # Refresh the game
                else:
                    sys.exit()


# Call the main function to start the game
if __name__ == "__main__":
    main()
