import agent

class game:
    def __init__(self, grid, agents, destinations, is_heuristic=False):
        self.grid = grid
        self.agents = agents # list of agents
        self.destinations = destinations # Mr.Thanh destination
        self.key_door = 0
        self.is_heuristic = is_heuristic
        
    def resolveGrid(self, grid):
        agents = []
        destinations = []
        key_door = []
        
        for i in range (len(grid)):
            for j in range (len(grid[i])):
                if ("A" in grid[i][j]):
                    agents.append(agent([i,j], 0))
                    continue
                if ("T1" == grid[i][j]):
                    destinations = (i,j)       
                    continue
                if ("D" in grid[i][j]):
                    key_door[(i,j)]
                
        return (agents, destinations, key_door)