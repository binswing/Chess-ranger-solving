import heapq
import copy
from typing import List, Tuple, Set

# Import your classes
# from figure import ChessRangerBoard 

class AStarNode:
    def __init__(self, board_matrix: List[List[int]], g: int, parent=None, action=None):
        self.board_matrix = board_matrix
        self.g = g  # Cost (moves made)
        self.h = self._calculate_heuristic()
        self.f = self.g + self.h
        self.parent = parent
        self.action = action  # The move (r1, c1, r2, c2) that got us here

    def __lt__(self, other):
        # Priority Queue sorts by 'f' (lowest cost first)
        return self.f < other.f

    def _calculate_heuristic(self) -> int:
        """
        The 'Connectivity' Heuristic.
        1. Build a graph of pieces.
        2. If pieces are broken into >1 unconnected islands, massive penalty.
        3. Otherwise, h = number of pieces remaining.
        """
        # We need a temporary board to calculate valid moves/graph
        temp_board = ChessRangerBoard(self.board_matrix)
        pieces = []
        
        # 1. Find all piece locations
        for r in range(8):
            for c in range(8):
                if temp_board.board[r][c] is not None:
                    pieces.append((r, c))
        
        count = len(pieces)
        if count <= 1: return 0 # Solved!

        # 2. Build Adjacency Graph (Who can capture whom?)
        # We use your board's logic to find edges
        adj = {pos: set() for pos in pieces}
        valid_moves = temp_board.get_all_valid_moves()
        
        for r1, c1, r2, c2 in valid_moves:
            # Undirected graph for connectivity: A captures B means they are 'linked'
            if (r1, c1) in adj and (r2, c2) in adj:
                adj[(r1, c1)].add((r2, c2))
                adj[(r2, c2)].add((r1, c1))

        # 3. Count Islands (Connected Components)
        visited = set()
        islands = 0
        for p in pieces:
            if p not in visited:
                islands += 1
                # Flood fill this island
                stack = [p]
                visited.add(p)
                while stack:
                    curr = stack.pop()
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)
        
        # HEURISTIC SCORING
        # If > 1 island, it's impossible to win (unless pieces=0, handled above).
        # We give a massive penalty (1000) so A* avoids this path.
        if islands > 1:
            return 1000 + count
        
        # Otherwise, cost is simply the number of pieces left to remove.
        return count

class ChessRangerSolver:
    def __init__(self, initial_board: List[List[int]]):
        self.start_matrix = initial_board
        self.visited = set()

    def solve(self):
        start_node = AStarNode(self.start_matrix, g=0)
        pq = []
        heapq.heappush(pq, start_node)
        
        print("A* Solver Started...")
        
        while pq:
            current_node = heapq.heappop(pq)
            
            # Check Goal: 1 Piece Left
            # (We can check pieces by counting non-zeros in matrix)
            piece_count = sum(row.count(0) for row in current_node.board_matrix)
            # Total cells (64) - Zeros = Pieces
            curr_pieces = 64 - piece_count
            
            if curr_pieces == 1:
                return self._reconstruct_path(current_node)
            
            # Convert to tuple for hashing in visited set
            state_tuple = tuple(tuple(row) for row in current_node.board_matrix)
            if state_tuple in self.visited:
                continue
            self.visited.add(state_tuple)
            
            # Optimization: If heuristic is huge (broken islands), skip generating children
            if current_node.h >= 1000:
                continue

            # Generate Children
            # 1. Load state into a Board object logic
            temp_board = ChessRangerBoard(current_node.board_matrix)
            possible_moves = temp_board.get_all_valid_moves()
            
            for move in possible_moves:
                # 2. Execute move on a COPY of the data
                # (We don't need deepcopy of object, just the matrix)
                new_matrix = [row[:] for row in current_node.board_matrix]
                
                # Apply move logic manually on matrix for speed
                # (move is r1, c1, r2, c2)
                r1, c1, r2, c2 = move
                val = new_matrix[r1][c1]
                new_matrix[r2][c2] = val # Capture
                new_matrix[r1][c1] = 0   # Empty source
                
                # 3. Create new node
                child_node = AStarNode(
                    new_matrix, 
                    g=current_node.g + 1, 
                    parent=current_node, 
                    action=move
                )
                
                heapq.heappush(pq, child_node)
                
        return None # No solution

    def _reconstruct_path(self, node):
        path = []
        while node.parent is not None:
            path.append(node.action)
            node = node.parent
        return path[::-1] # Return reversed (Start -> End)