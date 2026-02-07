class Piece:
    def __init__(self, color: bool = True):
        self.name: str = "Piece"
        self.color: bool = color
        self.first_move: bool = False
        if color:
            self.first_move = True
        self.legal_moves: list[tuple[int, int]] = []
        
    def get_name(self) -> str:
        return self.name
    
    def get_color(self) -> bool:
        return self.color
    
    def get_legal_moves(self) -> list[tuple[int, int]]:
        return self.legal_moves
    
    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return move in self.legal_moves
    
class Pawn(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "Pawn"
        if color:
            self.legal_moves = [(1, 1), (1, -1)]
        else:
            self.legal_moves = [(-1, 1), (-1, -1)]
    
class Knight(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "Knight"
        self.legal_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    
    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return move[0] ** 2 + move[1] ** 2 == 5
    
class Bishop(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "Bishop"
        self.legal_moves = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7), (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7), (-8, 8), (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]

    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return abs(move[0]) < 8 and abs(move[1]) < 8 and abs(move[0]) == abs(move[1]) and move != (0, 0)

class Rook(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "Rook"
        self.legal_moves = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)]

    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return move[0]*move[1] == 0 and move != (0, 0)

class Queen(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "Queen"
        self.legal_moves = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7), (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7), (-8, 8), (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)]

    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return abs(move[0]) < 8 and abs(move[1]) < 8 and (abs(move[0]) == abs(move[1]) or move[0]*move[1] == 0) and move != (0, 0)

class King(Piece):
    def __init__(self, color: bool = True):
        super().__init__(color)
        self.name = "King"
        self.legal_moves = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
    
    def is_legal_move(self, move: tuple[int, int]) -> bool:
        return abs(move[0]) < 2 and abs(move[1]) < 2 and move != (0, 0)

int_to_piece: dict[int, type[Piece]] = {
    1: Pawn,
    2: Knight,
    3: Bishop,
    4: Rook,
    5: Queen,
    6: King
}

piece_to_int: dict[type[Piece], int] = {
    Pawn: 1,
    Knight: 2,
    Bishop: 3,
    Rook: 4,
    Queen: 5,
    King: 6
}

class Board:
    def __init__(self, board: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]) -> None:
        self.board: list[list[Piece|None]]
        self.import_board(board)
    
    def import_board(self, board: list[list[int]]) -> None:
        self.board = []
        for row in board:
            self.board.append([])
            for piece in row:
                if piece == 0:
                    self.board[-1].append(None)
                else:
                    self.board[-1].append(int_to_piece[abs(piece)](piece > 0))
    
    def export_board(self) -> list[list[int]]:
        board: list[list[int]] = []
        for row in self.board:
            board.append([])
            for piece in row:
                if piece == None:
                    board[-1].append(0)
                else:
                    board[-1].append(piece_to_int[type(piece)] * (1 if piece.get_color() else -1))
        return board
    
    def move_piece(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        if self.is_valid_move(from_pos, to_pos):    
            self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
            self.board[from_pos[0]][from_pos[1]] = None
            return True
        return False

    def get_board(self) -> list[list[Piece|None]]:
        return self.board
    
    def is_valid_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        return (
            abs(from_pos[0])<=7 and abs(from_pos[1])<=7 and abs(to_pos[0])<=7 and abs(to_pos[1])<=7 and             # valid pos
            self.board[from_pos[0]][from_pos[1]] is not None and                                                    # must be a piece in from_pos
            self.board[to_pos[0]][to_pos[1]] is not None and                                                        # must be a piece in to_pos
            self.board[from_pos[0]][from_pos[1]].is_legal_move((to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]))  # type: ignore || legal move of piece
        )