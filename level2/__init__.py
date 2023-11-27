import heapq

class Node:
    def __init__(self, position, keys, cost=0, parent=None):
        self.position = position
        self.keys = frozenset(keys)
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

class Problem:
    def __init__(self, grid, start, goal, key_locations, door_locations):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.key_locations = key_locations
        self.door_locations = door_locations

    def get_neighbors(self, node):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        for dx, dy in directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]):
                cell = self.grid[x][y]
                if cell == '0' or (cell.startswith('K') or (cell.startswith('D') and cell[1:] in node.keys)):
                    new_keys = set(node.keys)
                    if cell.startswith('K'):
                        new_keys.add(cell[1:])
                    neighbors.append(Node((x, y), new_keys, node.cost + 1, node))
        return neighbors

    def is_goal(self, node):
        return node.position == self.goal

    def heuristic(self, node):
        return abs(node.position[0] - self.goal[0]) + abs(node.position[1] - self.goal[1])

def a_star_search(problem):
    start_node = Node(problem.start, set())
    open_set = []
    heapq.heappush(open_set, (0, start_node))
    visited = set()

    while open_set:
        current_node = heapq.heappop(open_set)[1]

        if problem.is_goal(current_node):
            return reconstruct_path(current_node)

        visited.add((current_node.position, tuple(sorted(current_node.keys))))

        for neighbor in problem.get_neighbors(current_node):
            if (neighbor.position, tuple(sorted(neighbor.keys))) not in visited:
                heapq.heappush(open_set, (neighbor.cost + problem.heuristic(neighbor), neighbor))

    return None

def reconstruct_path(node):
    path = []
    while node:
        path.append(node.position)
        node = node.parent
    return path[::-1]

# Example grid, key, and door setup
grid_example = [
    ["0", "K1", "0", "D1", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "D2", "0", "K2", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "0", "0", "0", "0"],
]

start_position = (0, 0)  # Starting position of the agent
goal_position = (4, 4)   # Goal position (Mr. Thanh's location)

key_locations = {"K1": (0, 1), "K2": (2, 3)}
door_locations = {"D1": (4, 3), "D2": (3, 4)}

# Create a Problem instance
problem = Problem(grid_example, start_position, goal_position, key_locations, door_locations)

# Perform A* search
path = a_star_search(problem)

# Output the path found
print("Path:", path)
