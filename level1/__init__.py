import psutil
from queue import PriorityQueue
import math


class Node:
    def __init__(self, position, problem, cost=0, parent=None):
        self.cost = cost
        self.position = position
        self.parent = parent
        self.problem = problem

    def __lt__(self, other):
        return self.cost + self.problem.heuristic(self) < other.cost + other.problem.heuristic(other)


class Problem:
    def __init__(self, grid, start, goal, is_heuristic=False):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.is_heuristic = is_heuristic

    def get_neighbors(self, node):
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        neighbors = []

        for dx, dy in directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1':
                neighbors.append(Node((x, y), self, node.cost + 1, node))
        for dx, dy in diagonal_directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1':
                if self.grid[x][node.position[1]] != '-1' and self.grid[node.position[0]][y] != '-1':
                    neighbors.append(Node((x, y), self, node.cost + math.sqrt(2), node))
        return neighbors

    def is_goal(self, node):
        return node.position == self.goal

    # Euclidean distance
    def heuristic(self, node):
        if self.heuristic:
            return math.sqrt((node.position[0] - self.goal[0]) ** 2 + (node.position[1] - self.goal[1]) ** 2)
        else:
            return 0


def a_star_search(problem):
    start_node = Node(problem.start, problem)
    frontier = PriorityQueue()
    frontier.put(start_node)
    explored = set()
    while not frontier.empty():
        node = frontier.get()
        if problem.is_goal(node):
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node):
            if neighbor.position not in explored:
                frontier.put(neighbor)
    return None




def print_path(node):
    if node is None:
        print("No path found")
        return
    path = []
    while node.parent is not None:
        path.append(node.position)
        node = node.parent
    path.append(node.position)
    print(path[::-1])


# Example usage
grid_example = [
    ["0", "0", "0", "-1", "0"],
    ["0", "0", "0", "-1", "0"],
    ["0", "-1", "0", "0", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "-1", "-1", "-1", "0"],
    ["0", "0", "0", "0", "0"]
]

start_position = (0, 0)
goal_position = (5, 4)
problem = Problem(grid_example, start_position, goal_position, is_heuristic=True)

path = a_star_search(problem)
print_path(path)
