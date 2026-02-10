import heapq
import copy

from src.entities.chess import ChessRangerPuzzle
from src.algorithms.algorithm import ChessSolver

class AStarNode:
    def __init__(self, state_matrix, g, h, parent=None, action=None):
        self.state = state_matrix   # The board configuration
        self.g = g                  # Steps taken so far
        self.h = h                  # Heuristic (estimated steps to go)
        self.f = g + h              # Total Score
        self.parent = parent        # For reconstructing path
        self.action = action        # The move that got us here

    def __lt__(self, other):
        return self.f < other.f

class AStarSolver(ChessSolver):
    def __init__(self, env):
        super().__init__(env)
        
        # --- A* STATE INITIALIZATION ---
        # We start the algorithm but PAUSE immediately.
        start_matrix = env.get_state()
        env.set_state(start_matrix)
        start_h = env.calculate_heuristic()
        
        start_node = AStarNode(start_matrix, 0, start_h)
        
        # The Open Set (Priority Queue)
        self.pq = []
        heapq.heappush(self.pq, start_node)
        
        # The Closed Set (Visited)
        self.visited = set()
        
        # --- ITERATION STATE ---
        # These keep track of "Where are we currently looking?"
        self.current_parent_node = None # The node we are currently expanding
        self.pending_moves = []         # The children of that node we haven't checked yet
        self.solution_found = False
        self.final_node = None

    def take_action(self):
        """
        Executes ONE search step.
        
        Returns:
            (board_layout, action): 
                - board_layout: The 'parent' state (where the branch starts).
                - action: The move the AI is about to try.
            None: If search is finished (Solution found or No solution).
        """
        if self.solution_found or (not self.pq and not self.pending_moves):
            return None # Done

        # LOOP until we find a move to return to the UI
        while True:
            
            # CASE 1: We are in the middle of expanding a node
            # (We have a parent, and we have moves left to try)
            if self.current_parent_node and self.pending_moves:
                move = self.pending_moves.pop(0)
                
                # --- A* LOGIC: PROCESS THE CHILD ---
                # 1. Restore Parent State (Crucial for calculation)
                self.env.set_state(self.current_parent_node.state)
                
                # 2. Execute Move
                self.env.step(move)
                
                # 3. Create Child Node
                child_state = self.env.get_state()
                child_h = self.env.calculate_heuristic()
                
                child_node = AStarNode(
                    child_state, 
                    g=self.current_parent_node.g + 1, 
                    h=child_h, 
                    parent=self.current_parent_node, 
                    action=move
                )
                
                # 4. Push to Queue (if promising)
                # We skip huge heuristic values (Islands detected)
                if child_h < 1000:
                    heapq.heappush(self.pq, child_node)
                
                # --- RETURN TO UI ---
                # We return the PARENT state so you can reset the board visual,
                # and the ACTION so you can show the move happening.
                return self.current_parent_node.state, move


            # CASE 2: We need to pick a new 'Best Node' to explore
            # (Our current parent has no more moves, or we just started)
            if not self.pq:
                return None # Queue empty, no solution
            
            # Pop the best candidate from Priority Queue
            best_node = heapq.heappop(self.pq)
            
            # Check if this node is the GOAL
            if best_node.h == 0:
                print("Solution Found!")
                self.solution_found = True
                self.final_node = best_node
                return None # Stop searching
            
            # Check if visited
            state_tuple = tuple(tuple(row) for row in best_node.state)
            if state_tuple in self.visited:
                continue # Skip this node, loop again
            self.visited.add(state_tuple)
            
            # Set this as the new Parent to expand
            self.current_parent_node = best_node
            
            # Generate all valid moves for this parent
            self.env.set_state(best_node.state)
            self.pending_moves = self.env.board.get_all_valid_moves()
            
            # (Loop continues immediately to Case 1 to process the first move)

    def get_final_path(self):
        """Recover the winning path after take_action returns None."""
        if not self.final_node:
            return []
        path = []
        curr = self.final_node
        while curr.parent:
            path.append(curr.action)
            curr = curr.parent
        return path[::-1]