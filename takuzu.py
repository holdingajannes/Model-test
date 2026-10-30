"""Takuzu (binaire puzzel) logica, 10x10. Gebruikt door de terminal- en grafische versie."""

import random

SIZE = 10
HALF = SIZE // 2
EMPTY = None
MAX_STEPS = 20000  # per poging, daarna opnieuw beginnen


def make_empty_board():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def columns(board):
    return [list(col) for col in zip(*board)]


def line_ok_partial(line):
    """Controleert een (deels ingevulde) rij of kolom op de regels die nu al te zien zijn."""
    if line.count(0) > HALF or line.count(1) > HALF:
        return False
    for i in range(len(line) - 2):
        a, b, c = line[i], line[i + 1], line[i + 2]
        if a != EMPTY and a == b == c:
            return False
    return True


def board_ok_partial(board):
    return all(line_ok_partial(r) for r in board) and all(
        line_ok_partial(c) for c in columns(board)
    )


def is_solved(board):
    """Het bord is volledig ingevuld en alle regels kloppen."""
    if any(cell == EMPTY for row in board for cell in row):
        return False
    for line in board + columns(board):
        if line.count(0) != HALF or line.count(1) != HALF:
            return False
        if not line_ok_partial(line):
            return False
    rows = [tuple(r) for r in board]
    cols = [tuple(c) for c in columns(board)]
    return len(set(rows)) == SIZE and len(set(cols)) == SIZE


def row_is_unique(board, r):
    """Controleert of rij r niet gelijk is aan een eerdere, al volledige rij."""
    row = tuple(board[r])
    return all(tuple(board[other]) != row for other in range(r))


def fill(board, pos, budget):
    """Vult het bord cel voor cel met backtracking. budget begrenst het aantal stappen."""
    if pos == SIZE * SIZE:
        return is_solved(board)
    budget[0] -= 1
    if budget[0] <= 0:
        return False

    r, c = divmod(pos, SIZE)
    values = [0, 1]
    random.shuffle(values)
    for v in values:
        board[r][c] = v
        ok = board_ok_partial(board)
        if ok and c == SIZE - 1:
            ok = row_is_unique(board, r)
        if ok and fill(board, pos + 1, budget):
            return True
    board[r][c] = EMPTY
    return False


def generate_solution(max_attempts=500):
    """Maakt een geldige oplossing. Lukt een poging niet binnen het budget, dan begint hij opnieuw."""
    for _ in range(max_attempts):
        board = make_empty_board()
        if fill(board, 0, [MAX_STEPS]):
            return board
    raise RuntimeError("Kon geen oplossing genereren, probeer het opnieuw.")


def make_puzzle(solution, empty_count=50):
    """Maakt een puzzel door een aantal vakjes uit de oplossing leeg te maken."""
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)
    for r, c in cells[:empty_count]:
        puzzle[r][c] = EMPTY
    return puzzle


def show_board(board):
    print()
    print("   " + "".join(f"{c + 1:>2}" for c in range(SIZE)))
    print("  +" + "-" * (SIZE * 2 + 1) + "+")
    for r, row in enumerate(board):
        symbols = "".join(" ." if cell == EMPTY else f" {cell}" for cell in row)
        print(f"{r + 1:>2}|{symbols} |")
    print("  +" + "-" * (SIZE * 2 + 1) + "+")
    print()


def parse_move(text):
    """Zet '2 3 1' om naar (rij, kolom, waarde) met nul-gebaseerde indexen."""
    parts = text.split()
    if len(parts) != 3:
        raise ValueError
    r, c = int(parts[0]) - 1, int(parts[1]) - 1
    if not (0 <= r < SIZE and 0 <= c < SIZE):
        raise ValueError
    if parts[2] == ".":
        value = EMPTY
    elif parts[2] in ("0", "1"):
        value = int(parts[2])
    else:
        raise ValueError
    return r, c, value


def play():
    solution = generate_solution()
    board = make_puzzle(solution, empty_count=50)
    fixed = {(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] != EMPTY}

    print("Binaire puzzel (Takuzu)")
    print(f"Regels: elke rij en kolom heeft {HALF} nullen en {HALF} enen,")
    print("nooit drie gelijke cijfers naast elkaar, en geen dubbele rijen of kolommen.")
    print("Invoer: rij kolom waarde, bijvoorbeeld '2 3 1'. Met '2 3 .' maak je een vak leeg.")
    print("Typ 'q' om te stoppen.")

    while True:
        show_board(board)
        try:
            text = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nTot ziens!")
            return

        if text == "q":
            print("\nDe oplossing was:")
            show_board(solution)
            print("Tot ziens!")
            return

        try:
            r, c, value = parse_move(text)
        except ValueError:
            print("Ongeldige invoer. Gebruik: rij kolom waarde, bijvoorbeeld '2 3 1'.")
            continue

        if (r, c) in fixed:
            print("Dit vak staat al vast en kan niet veranderd worden.")
            continue

        previous = board[r][c]
        board[r][c] = value
        if not board_ok_partial(board):
            board[r][c] = previous
            print("Die zet breekt een regel. Probeer iets anders.")
            continue

        if is_solved(board):
            show_board(board)
            print("Gefeliciteerd, je hebt de puzzel opgelost!")
            return


if __name__ == "__main__":
    play()