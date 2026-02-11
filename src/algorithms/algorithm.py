class ChessSolver:
    def __init__(self, env):
        self.env = env
        self.final_node = None
        
    def take_action(self):
        pass
    
    def get_final_path(self):
        if not self.final_node:
            return []
        path = []
        curr = self.final_node
        while curr.parent:
            path.append(curr.action)
            curr = curr.parent
        return path[::-1]
