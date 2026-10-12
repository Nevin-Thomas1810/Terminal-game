from blessed import Terminal
import chess
import chess.engine
import time
term = Terminal()
board = chess.Board()

WHITE_TIME = 5 * 60
BLACK_TIME = 5 * 60
last_time = time.monotonic()

#PIECES
PIECE = {
    'P':'♙',
    'p':'♟',
    'K':'♔',
    'k':'♚',
    'Q':'♛',
    'q':'♕',
    'B':'♝',
    'b':'♗',
    'N':'♞',
    'n':'♘',
    'R':'♜',
    'r':'♖'
}
#BOARD LOGIC
sq_selected = None
def format_time(seconds):
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02}:{secs:02}"

def show_clock():
    print(f"{format_time(WHITE_TIME)} | {format_time(BLACK_TIME)}")

def render_board(selected=None):
    print(term.clear)
    print(term.bold("----TERMINAL CHESS----\n"))

    square_width = 5
    square_height = 3
    board_left = 2

    print(" " * board_left + "".join(f"{chr(file + 97):^{7}}" for file in range(8)))

    for rank in reversed(range(8)):
        for row in range(square_height):
            line = f"{rank + 1}" if row == square_height // 2 else ' '

            for file in range(8):
                sq = chess.square(file, rank)
                piece = board.piece_at(sq)
                piece_str = PIECE[piece.symbol()] if piece else ''

                is_dark = (rank + file) % 2 == 0
                bg_color = term.on_black if is_dark else term.on_gray

                if selected == sq:
                    bg_color = term.on_yellow
                elif selected is not None and chess.Move(selected, sq) in board.legal_moves:
                    bg_color = term.on_green

                if row == square_height // 2:
                    cell = f"{piece_str:^{square_width}}"
                else:
                    cell = " "*square_width

                line += bg_color + f" {cell} " + term.normal

            line += f" {rank + 1}" if row == square_height // 2 else ""
            print(line)
    print(" " * board_left + "".join(f"{chr(file + 97):^{7}}" for file in range(8)))

    show_clock()
    if board.is_checkmate():
        print(term.red_bold("CHECKMATE GAME OVER"))

    elif board.is_check():
        print(term.yellow_bold("CHECK PLEASE MOVE OR BLOCK OR CAPTURE."))

    if board.turn == chess.WHITE:
        turn_str = "White"

    else:
        turn_str = "Black"

    print(f" {turn_str}")

ENGINE_PATH = r"C:\Users\binut\Documents\GDrive\Stopckfish_extract\stockfish\stockfish-windows-x86-64-universal.exe"
engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

def parse_click(x,y):

    #COORDINATE LOGIC
    board_top = 3
    board_left = 2
    square_width = 7
    square_height = 3
    rank = 7 - ((y - board_top) // square_height)
    file = (x - board_left)//square_width

    if 0 <= rank <= 7 and 0 <= file <= 7:
        return chess.square(file, rank)
    return None

def ai_move():
    global BLACK_TIME, last_time
    if board.is_game_over():
        return

    ai_start = time.monotonic()

    result = engine.play(board, chess.engine.Limit(time = 2))

    ai_elapsed = time.monotonic() - ai_start
    BLACK_TIME -= ai_elapsed
    last_time = time.monotonic()

    if BLACK_TIME <= 0:
        BLACK_TIME = 0
        render_board()
        print(term.red_bold("TIME OUT. WHITE WON."))
        return
    
    board.push(result.move)
    render_board()

def main():
    global sq_selected, last_time, WHITE_TIME, BLACK_TIME

    with term.cbreak(), term.hidden_cursor(), term.mouse_enabled():
        render_board()

        #MOUSE LOGIC
        while True:
            val = term.inkey(timeout=0.1)

            now = time.monotonic()
            elapsed = now - last_time
            last_time = now

            if board.turn == chess.WHITE:
                WHITE_TIME -= elapsed

            if board.turn == chess.BLACK:
                BLACK_TIME -= elapsed

            if WHITE_TIME <= 0 or BLACK_TIME <= 0:
                print("Time up")
                break

            if val.lower() == "q":
                engine.quit()
                break

            if val.is_sequence and val.name.startswith("MOUSE_"):
                x,y = val.mouse_xy
                print("Event: ", repr(val))
                print("Name: ", val.name)
                print("Type: ", type(val))

                sq = parse_click(x, y)
                print("cords: ", x, y)
                print("Square: ", chess.square_name(sq) if sq is not None else "Outside Board")

                if sq is None:
                    continue
                if sq_selected is None:
                    piece = board.piece_at(sq)
                    if piece  and piece.color == board.turn:
                        sq_selected = sq

                else:
                    move = chess.Move(sq_selected, sq)

                    is_pawn = board.piece_at(sq_selected) and board.piece_at(sq_selected).piece_type == chess.PAWN
                    target_rank = chess.square_rank(sq)
                        #PROMOTION LOGIC
                    if is_pawn and target_rank in (0,7):
                        print(term.bold_yellow("\nPromote pawn to queen = q, bishop = b, knight = n, rook = r: "), end = '', flush = True)

                        promo_key = ''

                        while promo_key.lower() not in ('q', 'b', 'n', 'r'):
                                promo_key = term.inkey()

                        promo_map = {
                                    'q': chess.QUEEN,
                                    'r': chess.ROOK,
                                    'b': chess.BISHOP,
                                    'n': chess.KNIGHT
                                }

                        promo_move = chess.Move(sq_selected, sq, promotion=promo_map[promo_key.lower()])

                        if promo_move in board.legal_moves:
                                board.push(promo_move)
                                
                        sq_selected = None

                    else:
                            if move in board.legal_moves:
                                board.push(move)
                                sq_selected = None

                                if not board.is_game_over():
                                    ai_move()

                            elif board.piece_at(sq) and board.piece_at(sq).color == board.turn:
                                sq_selected = sq
                            else:
                                sq_selected = None

                    render_board(sq_selected)

                        
if __name__ == "__main__":
    main()

