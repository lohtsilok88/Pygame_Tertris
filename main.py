
import pygame
import random
import sys

pygame.init()

# Screen settings
CELL = 30
COLS = 10
ROWS = 20
WIDTH = 600
HEIGHT = 700

BOARD_X = 35
BOARD_Y = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RETRO TETRIS")

clock = pygame.time.Clock()

# Retro colours
BLACK = (5, 5, 15)
WHITE = (240, 240, 240)
CYAN = (0, 255, 255)
PINK = (255, 0, 255)
GREEN = (0, 255, 100)
YELLOW = (255, 230, 0)
PURPLE = (160, 70, 255)
BLUE = (50, 100, 255)
ORANGE = (255, 140, 0)

COLORS = [
    CYAN, BLUE, ORANGE, YELLOW,
    GREEN, PURPLE, PINK
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[1, 1, 0],
     [0, 1, 1]]
]

FONT = pygame.font.SysFont("couriernew", 23, bold=True)
BIG_FONT = pygame.font.SysFont("couriernew", 42, bold=True)

def new_piece():
    index = random.randrange(len(SHAPES))
    shape = [row[:] for row in SHAPES[index]]

    return {
        "shape": shape,
        "color": COLORS[index],
        "x": COLS // 2 - len(shape[0]) // 2,
        "y": 0
    }

def create_board():
    return [[None for _ in range(COLS)]
            for _ in range(ROWS)]

def valid(piece, board, dx=0, dy=0):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                nx = piece["x"] + x + dx
                ny = piece["y"] + y + dy

                if nx < 0 or nx >= COLS:
                    return False

                if ny >= ROWS:
                    return False

                if ny >= 0 and board[ny][nx]:
                    return False

    return True

def lock_piece(piece, board):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                bx = piece["x"] + x
                by = piece["y"] + y

                if by < 0:
                    return False

                board[by][bx] = piece["color"]

    return True

def clear_lines(board):
    remaining = [
        row for row in board if any(cell is None for cell in row)
    ]

    cleared = ROWS - len(remaining)

    while len(remaining) < ROWS:
        remaining.insert(0, [None] * COLS)

    return remaining, cleared

def rotate(piece, board):
    old = piece["shape"]

    rotated = [
        list(row) for row in zip(*old[::-1])
    ]

    piece["shape"] = rotated

    if not valid(piece, board):
        piece["shape"] = old

def draw_block(x, y, color, ghost=False):
    rect = pygame.Rect(
        BOARD_X + x * CELL,
        BOARD_Y + y * CELL,
        CELL,
        CELL
    )

    if ghost:
        pygame.draw.rect(screen, color, rect, 2)
    else:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 1)

def draw_board(board):
    pygame.draw.rect(
        screen, (20, 20, 40),
        (BOARD_X, BOARD_Y, COLS * CELL, ROWS * CELL)
    )

    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(
                BOARD_X + x * CELL,
                BOARD_Y + y * CELL,
                CELL, CELL
            )

            if board[y][x]:
                draw_block(x, y, board[y][x])
            else:
                pygame.draw.rect(screen, (35, 35, 55), rect, 1)

def draw_piece(piece, ghost=False):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                draw_block(
                    piece["x"] + x,
                    piece["y"] + y,
                    piece["color"],
                    ghost
                )

def draw_next(piece):
    text = FONT.render("NEXT", True, CYAN)
    screen.blit(text, (400, 150))

    shape = piece["shape"]

    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    410 + x * 24,
                    200 + y * 24,
                    24, 24
                )
                pygame.draw.rect(screen, piece["color"], rect)
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_text(text, x, y, color=WHITE):
    surface = FONT.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_ghost(piece, board):
    ghost = {
        "shape": piece["shape"],
        "color": piece["color"],
        "x": piece["x"],
        "y": piece["y"]
    }

    while valid(ghost, board, dy=1):
        ghost["y"] += 1

    draw_piece(ghost, True)

def main():
    board = create_board()
    current = new_piece()
    next_piece = new_piece()

    score = 0
    lines = 0
    level = 1

    fall_timer = 0
    fall_speed = 500

    paused = False
    game_over = False

    running = True

    while running:
        dt = clock.tick(60)
        fall_timer += dt

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_p and not game_over:
                    paused = not paused

                if event.key == pygame.K_r:
                    return main()

                if not paused and not game_over:

                    if event.key == pygame.K_LEFT:
                        if valid(current, board, dx=-1):
                            current["x"] -= 1

                    elif event.key == pygame.K_RIGHT:
                        if valid(current, board, dx=1):
                            current["x"] += 1

                    elif event.key == pygame.K_DOWN:
                        if valid(current, board, dy=1):
                            current["y"] += 1
                            score += 1

                    elif event.key == pygame.K_UP:
                        rotate(current, board)

                    elif event.key == pygame.K_SPACE:
                        while valid(current, board, dy=1):
                            current["y"] += 1
                            score += 2

        if not paused and not game_over:

            if fall_timer >= fall_speed:
                fall_timer = 0

                if valid(current, board, dy=1):
                    current["y"] += 1
                else:
                    if not lock_piece(current, board):
                        game_over = True
                    else:
                        board, cleared = clear_lines(board)

                        points = [0, 100, 300, 500, 800]
                        score += points[cleared] * level
                        lines += cleared

                        level = lines // 10 + 1
                        fall_speed = max(70, 500 - (level - 1) * 40)

                        current = next_piece
                        next_piece = new_piece()

                        if not valid(current, board):
                            game_over = True

        screen.fill(BLACK)

        # Header
        title = BIG_FONT.render("RETRO TETRIS", True, CYAN)
        screen.blit(title, (135, 8))

        draw_board(board)

        if not game_over:
            draw_ghost(current, board)
            draw_piece(current)

        # Side panel
        draw_text("SCORE", 400, 300, PINK)
        draw_text(str(score), 400, 330)

        draw_text("LEVEL", 400, 390, GREEN)
        draw_text(str(level), 400, 420)

        draw_text("LINES", 400, 480, YELLOW)
        draw_text(str(lines), 400, 510)

        draw_next(next_piece)

        draw_text("CONTROLS", 390, 570, CYAN)
        draw_text("ARROWS: MOVE", 390, 600)
        draw_text("UP: ROTATE", 390, 625)
        draw_text("SPACE: DROP", 390, 650)

        if paused:
            msg = BIG_FONT.render("PAUSED", True, YELLOW)
            screen.blit(msg, (190, 330))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            msg = BIG_FONT.render("GAME OVER", True, PINK)
            screen.blit(msg, (125, 280))

            draw_text("Press R to restart", 175, 350, WHITE)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
