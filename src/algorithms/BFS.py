import collections
import copy

from src.entities.chess import ChessRangerPuzzle
from src.algorithms.algorithm import ChessSolver

class BFSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = copy.deepcopy(state)
        self.parent = parent
        self.action = action

class BFSSolver(ChessSolver):
    def __init__(self, env: ChessRangerPuzzle):
        super().__init__(env)

        start_matrix = env.get_state()
        env.set_state(start_matrix)
        
        start_node = BFSNode(start_matrix)
        self.queue = collections.deque([start_node])
        self.visited = set()
        
        state_tuple = tuple(tuple(row) for row in start_matrix)
        self.visited.add(state_tuple)
        
        self.current_parent_node = None 
        self.pending_moves = []       
        self.solution_found = False
        self.final_node = None

        if self.env.calculate_heuristic(start_matrix) == 0:
            self.solution_found = True
            self.final_node = start_node

    def take_action(self):
        if self.solution_found or (not self.queue and not self.pending_moves and not self.current_parent_node):
            return None, None 

        while True:
            if self.current_parent_node and self.pending_moves:
                move = self.pending_moves.pop(0)

                self.env.set_state(self.current_parent_node.state)
                state_before_move = self.env.get_state()
                self.env.step(move)
                
                child_state = self.env.get_state()
                state_tuple = tuple(tuple(row) for row in child_state)
                if state_tuple in self.visited:
                    continue
                
                self.visited.add(state_tuple)
                child_node = BFSNode(
                    child_state, 
                    parent=self.current_parent_node, 
                    action=move
                )
                self.queue.append(child_node)
                if self.env.calculate_heuristic(child_state) == 0:
                    print("Solution Found!")
                    self.solution_found = True
                    self.final_node = child_node
                    return state_before_move, move

                return state_before_move, move
            if not self.queue:
                return None, None 
            best_node = self.queue.popleft()
            
            self.current_parent_node = best_node
            self.env.set_state(best_node.state)
            self.pending_moves = self.env.board.get_all_valid_moves()