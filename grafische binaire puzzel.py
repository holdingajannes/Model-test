"""Takuzu (binaire puzzel) met grafische interface in pygame, 10x10."""

import sys

import pygame

import takuzu

SIZE = takuzu.SIZE
EMPTY = takuzu.EMPTY
EMPTY_COUNT = 50  # aantal lege vakjes, de rest is vooraf ingevuld

CELL = 52
MARGIN = 30
GRID = CELL * SIZE
WIDTH = GRID + 2 * MARGIN
HEIGHT = GRID + 2 * MARGIN + 110

BG = (30, 32, 38)
CELL_COLOR = (45, 48, 56)
LOCKED_CELL_COLOR = (240, 240, 245)
WRONG_CELL_COLOR = (110, 40, 48)
GRID_COLOR = (90, 95, 105)
THICK_COLOR = (200, 205, 215)
SELECT_COLOR = (80, 130, 200)
GIVEN_TEXT = (240, 240, 245)
PLAYER_TEXT = (110, 200, 255)
LOCKED_TEXT = (150, 230, 170)
WRONG_TEXT = (255, 120, 120)
TEXT = (200, 200, 210)
ERROR_TEXT = (255, 120, 120)
OK_TEXT = (120, 230, 150)
BUTTON = (70, 110, 170)
BUTTON_HOVER = (90, 135, 200)

VALUE_KEYS = {
    pygame.K_0: 0,
    pygame.K_KP0: 0,
    pygame.K_1: 1,
    pygame.K_KP1: 1,
}
CLEAR_KEYS = (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_PERIOD, pygame.K_KP_PERIOD)


def new_game():
    solution = takuzu.generate_solution()
    board = takuzu.make_puzzle(solution, empty_count=EMPTY_COUNT)
    fixed = {
        (r, c)
        for r in range(SIZE)
        for c in range(SIZE)
        if board[r][c] != EMPTY
    }
    return board, fixed, solution


def find_wrong_cells(board, solution):
    """Geeft alle vakjes terug die gevuld zijn in een volledige rij of kolom, maar niet kloppen met de oplossing."""
    wrong = set()

    for r in range(SIZE):
        if all(board[r][c] != EMPTY for c in range(SIZE)):
            for c in range(SIZE):
                if board[r][c] != solution[r][c]:
                    wrong.add((r, c))

    for c in range(SIZE):
        if all(board[r][c] != EMPTY for r in range(SIZE)):
            for r in range(SIZE):
                if board[r][c] != solution[r][c]:
                    wrong.add((r, c))

    return wrong


def find_locked_cells(board, solution):
    """Geeft alle vakjes terug die horen bij een volledige rij of kolom die exact klopt."""
    locked = set()

    for r in range(SIZE):
        if all(board[r][c] != EMPTY for c in range(SIZE)) and board[r] == solution[r]:
            for c in range(SIZE):
                locked.add((r, c))

    for c in range(SIZE):
        column = [board[r][c] for r in range(SIZE)]
        if all(v != EMPTY for v in column) and column == [solution[r][c] for r in range(SIZE)]:
            for r in range(SIZE):
                locked.add((r, c))

    return locked


def draw_board(screen, board, fixed, selected, wrong, locked, font):
    for r in range(SIZE):
        for c in range(SIZE):
            rect = pygame.Rect(MARGIN + c * CELL, MARGIN + r * CELL, CELL, CELL)
            is_wrong = (r, c) in wrong
            is_locked = (r, c) in locked

            if is_wrong:
                bg = WRONG_CELL_COLOR
            else:
                bg = CELL_COLOR
            pygame.draw.rect(screen, bg, rect)

            if selected == (r, c) and not is_locked:
                pygame.draw.rect(screen, SELECT_COLOR, rect.inflate(-4, -4), 3)

            value = board[r][c]
            if value != EMPTY:
                if is_locked:
                    color = LOCKED_TEXT
                elif (r, c) in fixed:
                    color = GIVEN_TEXT
                elif is_wrong:
                    color = WRONG_TEXT
                else:
                    color = PLAYER_TEXT
                text = font.render(str(value), True, color)
                screen.blit(text, text.get_rect(center=rect.center))

    # Dunne lijnen per vakje, dikkere lijnen om elke 5 vakjes.
    for i in range(SIZE + 1):
        pos = MARGIN + i * CELL
        if i % (SIZE // 2) == 0:
            color, width = THICK_COLOR, 3
        else:
            color, width = GRID_COLOR, 1
        pygame.draw.line(screen, color, (MARGIN, pos), (MARGIN + GRID, pos), width)
        pygame.draw.line(screen, color, (pos, MARGIN), (pos, MARGIN + GRID), width)


def cell_at(pos):
    x, y = pos
    c = (x - MARGIN) // CELL
    r = (y - MARGIN) // CELL
    if 0 <= r < SIZE and 0 <= c < SIZE and MARGIN <= x < MARGIN + GRID and MARGIN <= y < MARGIN + GRID:
        return int(r), int(c)
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Takuzu 10x10")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)
    small = pygame.font.Font(None, 28)

    board, fixed, solution = new_game()
    selected = None
    wrong = set()
    locked = set()
    won = False
    message = "Klik op een vakje en typ 0 of 1."
    message_color = TEXT

    status_y = MARGIN * 2 + GRID
    button = pygame.Rect(MARGIN, status_y + 40, 200, 40)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.collidepoint(event.pos):
                    board, fixed, solution = new_game()
                    selected = None
                    wrong = set()
                    locked = set()
                    won = False
                    message = "Nieuwe puzzel. Klik op een vakje en typ 0 of 1."
                    message_color = TEXT
                else:
                    cell = cell_at(event.pos)
                    if cell is not None:
                        selected = cell

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_n:
                    board, fixed, solution = new_game()
                    selected = None
                    wrong = set()
                    locked = set()
                    won = False
                    message = "Nieuwe puzzel. Klik op een vakje en typ 0 of 1."
                    message_color = TEXT

                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    if selected is None:
                        selected = (0, 0)
                    r, c = selected
                    if event.key == pygame.K_UP:
                        r = max(0, r - 1)
                    elif event.key == pygame.K_DOWN:
                        r = min(SIZE - 1, r + 1)
                    elif event.key == pygame.K_LEFT:
                        c = max(0, c - 1)
                    elif event.key == pygame.K_RIGHT:
                        c = min(SIZE - 1, c + 1)
                    selected = (r, c)

                elif (event.key in VALUE_KEYS or event.key in CLEAR_KEYS) and selected and not won:
                    r, c = selected
                    if (r, c) in fixed:
                        message = "Dit vakje staat al vast."
                        message_color = ERROR_TEXT
                    elif (r, c) in locked:
                        message = "Dit vakje is al goedgekeurd en vergrendeld."
                        message_color = ERROR_TEXT
                    else:
                        new_value = VALUE_KEYS[event.key] if event.key in VALUE_KEYS else EMPTY
                        previous = board[r][c]
                        board[r][c] = new_value

                        if not takuzu.board_ok_partial(board):
                            board[r][c] = previous
                            message = "Die zet breekt een regel. Probeer iets anders."
                            message_color = ERROR_TEXT
                        else:
                            wrong = find_wrong_cells(board, solution)
                            locked = find_locked_cells(board, solution) | locked
                            if board == solution:
                                won = True
                                wrong = set()
                                message = "Gefeliciteerd, je hebt de puzzel opgelost! Druk op N voor een nieuwe."
                                message_color = OK_TEXT
                            elif wrong:
                                message = "Een volledige rij of kolom klopt niet. Foute vakjes zijn rood."
                                message_color = ERROR_TEXT
                            elif locked:
                                message = "Goed zo, een rij of kolom is vergrendeld."
                                message_color = OK_TEXT
                            else:
                                message = "Goed zo, ga zo door."
                                message_color = TEXT

        # Tekenen
        screen.fill(BG)
        draw_board(screen, board, fixed, selected, wrong, locked, font)

        status = small.render(message, True, message_color)
        screen.blit(status, (MARGIN, status_y + 5))

        hover = button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER if hover else BUTTON, button, border_radius=8)
        label = small.render("Nieuwe puzzel (N)", True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=button.center))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()