from figure import *

class ChessRangerBoard(Board): # Only white pieces
    def __init__(self, board: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]) -> None:
        super().__init__(board) 

    def import_board(self, board: list[list[int]]) -> None:
        self.board = []
        for row in board:
            self.board.append([])
            for piece in row:
                if piece == 0:
                    self.board[-1].append(None)
                else:
                    self.board[-1].append(int_to_piece[abs(piece)](True))

class ChessMeleeBoard(Board):
    def __init__(self, board: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]) -> None:
        super().__init__(board)
        self.waiting_turn: bool = True

    def move_piece(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        if self.is_valid_move(from_pos, to_pos):
            if (
                self.waiting_turn != self.board[from_pos[0]][from_pos[1]].get_color() or                            # type: ignore || only move on the correct turn
                self.board[from_pos[0]][from_pos[1]].get_color() != self.board[to_pos[0]][to_pos[1]].get_color()    # type: ignore || must capture the other side pieces
            ):  
                return False
            self.waiting_turn = not self.waiting_turn    
            self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
            self.board[from_pos[0]][from_pos[1]] = None
            return True
        return False
    
class ChessPuzzle:
    def __init__(self):
        pass
    
