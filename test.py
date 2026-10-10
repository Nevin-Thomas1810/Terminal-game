from blessed import Terminal
import chess

term = Terminal()
board = chess.Board()

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

def render_board(selected=None):
    print(term.clear)
    print(term.bold("----TERMINAL CHESS----\n"))

    print("   a  b  c  d  e  f  g  h")

    for rank in reversed(range(8)):
        line = f" {rank + 1}"
        for file in range(8):
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            piece_str = PIECE[piece.symbol()] if piece else ' '

            is_dark = (rank + file) % 2 == 0
            bg_color = term.on_black if is_dark else term.on_gray

            if selected == sq:
                bg_color = term.on_yellow
            elif selected is not None and chess.Move(selected, sq) in board.legal_moves:
                bg_color = term.on_green

            line += bg_color + f" {piece_str} " + term.normal

        line += f" {rank+1}"
        print(line)

    print("   a  b  c  d  e  f  g  h\n")

    if board.is_checkmate():
        print(term.red_bold("CHECKMATE GAME OVER"))

    elif board.is_check():
        print(term.yellow_bold("CHECK PLEASE MOVE OR BLOCK OR CAPTURE."))

    if board.turn == chess.WHITE:
        turn_str = "White"

    else:
        turn_str = "Black"

    print(f" {turn_str}")

def parse_click(x,y):

    #COORDINATE LOGIC
    board_top = 4
    board_left = 2
    rank = 7 - (y - board_top)
    file = (x - board_left)//3

    if 0 <= rank <= 7 and 0 <= file <= 7:
        return chess.square(file, rank)
    return None

def main():
    global sq_selected

    with term.cbreak(), term.hidden_cursor(), term.mouse_enabled():
        render_board()

        #MOUSE LOGIC
        while True:
            val = term.inkey()

            if val.lower() == "q":
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
                            elif board.piece_at(sq) and board.piece_at(sq).color == board.turn:
                                sq_selected = sq
                            else:
                                sq_selected = None

                    render_board(sq_selected)

                        
if __name__ == "__main__":
    main()

