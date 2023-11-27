import psutil
from queue import PriorityQueue
from queue import Queue

import math

from level1.read_file import read_file


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
        if self.is_heuristic:
            return math.sqrt((node.position[0] - self.goal[0]) ** 2 + (node.position[1] - self.goal[1]) ** 2)
        else:
            return 0


def a_star_search(problem):
    counter = 0
    start_node = Node(problem.start, problem)
    frontier = PriorityQueue()
    frontier.put(start_node)
    explored = set()
    while not frontier.empty():
        node = frontier.get()
        if problem.is_goal(node):
            print(counter)
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node):
            if neighbor.position not in explored:
                frontier.put(neighbor)
        counter += 1
    return None


def bfs_search(problem):
    counter = 0
    start_node = Node(problem.start, problem)
    frontier = Queue()
    frontier.put(start_node)
    explored = set()
    while not frontier.empty():
        node = frontier.get()
        if problem.is_goal(node):
            print(counter)
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node):
            if neighbor.position not in explored:
                frontier.put(neighbor)
        counter += 1
    return None


def dfs_search(problem):
    counter = 0
    start_node = Node(problem.start, problem)
    frontier = [start_node]
    explored = set()
    while len(frontier) != 0:
        node = frontier.pop()
        if problem.is_goal(node):
            print(counter)
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node):
            if neighbor.position not in explored:
                frontier.append(neighbor)
        counter += 1
    return None


def ucs(problem):
    counter = 0
    start_node = Node(problem.start, problem)
    frontier = PriorityQueue()
    explored = set()
    frontier.put(start_node)
    while not frontier.empty():
        node = frontier.get()
        if problem.is_goal(node):
            print(counter)
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node):
            if neighbor.position not in explored:
                frontier.put(neighbor)
        counter += 1
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
file = read_file()
start_position = ()
goal_position = ()
start_position_column = -1
goal_position_column = -1
row_index = 0

grid = file['floor1']['floor_data']
for line in grid:
    if 'A1' in line:
        start_position_column = line.index('A1')
        start_position = (row_index, start_position_column)
        grid[row_index][start_position_column] = '0'

    if 'T1' in line:
        start_position_column = line.index('T1')
        goal_position = (row_index, start_position_column)
        grid[row_index][start_position_column] = '0'

    row_index += 1

print(grid, start_position, goal_position)

problem = Problem(grid, start_position, goal_position, is_heuristic=True)

path = a_star_search(problem)
print_path(path)
