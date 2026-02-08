import numpy as np

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
    
    def is_valid_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        r1, c1 = from_pos
        r2, c2 = to_pos

        if not (
            0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8 and 
            self.board[r1][c1] is not None and self.board[r2][c2] is not None   
            ):
            return False
            
        piece = self.board[r1][c1]

        move_delta = (r2 - r1, c2 - c1)
        if not piece.is_legal_move(move_delta):                                                                     # type: ignore 
            return False

        if not self.is_path_clear(from_pos, to_pos):
            return False

        return True

    def get_all_valid_moves(self):
        """Returns a list of all legal actions [(r1,c1,r2,c2), ...]"""
        moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c] is not None:
                    for tr in range(8):
                        for tc in range(8):
                            if self.is_valid_move((r, c), (tr, tc)):
                                moves.append((r, c, tr, tc))
        return moves
    
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
    
class ChessRangerPuzzle(ChessPuzzle):
    def __init__(self, board_layout: list[list[int]] | None = None):
        super().__init__()
        self.initial_board_layout = None
        if board_layout is None:
            board_layout = [[0]*8 for _ in range(8)]
            board_layout[4][4] = 2 
            board_layout[2][3] = 2
            board_layout[3][5] = 6
        self.initial_board_layout = board_layout
        self.board = ChessRangerBoard(board_layout)

    def step(self, action: tuple[int, int, int, int]):
        success = self.board.move_piece((action[0], action[1]), (action[2], action[3]))
        
        reward = 0
        done = False
        info = {}
        if not success:
            reward = -10
        else:
            reward = 1

            piece_count = self.board.count_pieces()
            if piece_count == 1:
                reward = 100
                done = True
                info['msg'] = "Solved!"
            elif piece_count > 1:
                all_moves = self.board.get_all_valid_moves()
                if len(all_moves) == 0:
                    reward = -50
                    done = True
                    info['msg'] = "Dead End"    
        return self.get_observation(), reward, done, info

    def reset(self, board_layout: list[list[int]] | None = None):
        if board_layout is not None:
            self.board.import_board(board_layout)
        else:
            self.board.import_board(self.initial_board_layout)                                                      # type: ignore
    
    def get_observation(self):
        return np.array(self.board.export_board(), dtype=np.int8)