from queue import PriorityQueue
from queue import Queue
import pygame

import math

from utils.read_file import read_file


class Node:
    def __init__(self, position, problem, cost=0, parent=None, spot = None):
        self.cost = cost
        self.position = position
        self.parent = parent
        self.problem = problem
        self.spot = spot

    def __lt__(self, other):
        return self.cost + self.problem.heuristic(self) < other.cost + other.problem.heuristic(other)


class Problem:
    def __init__(self, grid, start, goal, is_heuristic=False):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.is_heuristic = is_heuristic

    def get_neighbors(self, node, visual_grid):
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        neighbors = []

        for dx, dy in directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1':
                neighbors.append(Node((x, y), self, node.cost + 1, node, visual_grid[x][y]))
        for dx, dy in diagonal_directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1':
                if self.grid[x][node.position[1]] != '-1' and self.grid[node.position[0]][y] != '-1':
                    neighbors.append(Node((x, y), self, node.cost + math.sqrt(2), node, visual_grid[x][y]))
        return neighbors

    def is_goal(self, node):
        return node.position == self.goal

    # Euclidean distance
    def heuristic(self, node):
        if self.is_heuristic:
            return abs(node.position[0] - self.goal[0]) + abs(node.position[1] - self.goal[1])
        else:
            return 0


def a_star_search(problem, draw, grid, visual_grid, grid_start_x, grid_start_y, win, width, rows, columns):
    counter = 0
    start_node = Node(problem.start, problem, 0, None, visual_grid[problem.start[0]][problem.start[1]] )
    frontier = PriorityQueue()
    frontier.put(start_node)
    explored = set()
    while not frontier.empty():
        node = frontier.get()
        if problem.is_goal(node):
            visual_grid[node.position[0]][node.position[1]].make_closed()
            print(counter)
            draw(win, visual_grid, rows, columns, width, grid_start_x, grid_start_y)
            return node
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node, visual_grid):
            if neighbor.position not in explored:
                frontier.put(neighbor)
                # Update the spot's color to represent it's in the frontier
                visual_grid[neighbor.position[0]][neighbor.position[1]].make_open()

        # Update the spot's color to represent it has been explored
        visual_grid[node.position[0]][node.position[1]].make_closed()
        draw(win, visual_grid, rows, columns, width, grid_start_x, grid_start_y)
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

    while node is not None:
        node.spot.make_path()
        node = node.parent


def level1(win, width, make_grid, draw):
    # Example usage
    file = read_file('./level1/input.txt')
    ROWS = file['floor1']['width']
    COLUMN = file['floor1']['height']
    start_position = ()
    goal_position = ()
    start_position_column = -1
    goal_position_column = -1
    row_index = 0

    visual_grid = make_grid(ROWS, COLUMN, width)

    # Calculate the total grid size
    total_grid_width = COLUMN * (width // COLUMN)
    total_grid_height = ROWS * (width // COLUMN)

    # Calculate the starting position to center the grid
    grid_start_x = (width - total_grid_width) // 2
    grid_start_y = (width - total_grid_height) // 2

    grid = file['floor1']['floor_data']
    for line in grid:
        if 'A1' in line:
            start_position_column = line.index('A1')
            start_position = (row_index, start_position_column)
            grid[row_index][start_position_column] = '0'
            visual_grid[row_index][start_position_column].make_start()

        if 'T1' in line:
            start_position_column = line.index('T1')
            goal_position = (row_index, start_position_column)
            grid[row_index][start_position_column] = '0'
            visual_grid[row_index][start_position_column].make_end()

        for column_index, cell in enumerate(line):
            if cell == '-1':
                visual_grid[row_index][column_index].make_barrier()

        row_index += 1

    problem = Problem(grid, start_position, goal_position, is_heuristic=True)

    print(grid, start_position, goal_position)

    run = True
    while run:
        draw(win, visual_grid, ROWS, COLUMN, width, grid_start_x, grid_start_y)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                node = a_star_search(problem, draw, grid, visual_grid, grid_start_x, grid_start_y, win, width, ROWS, COLUMN)
                print_path(node)
    pygame.quit()
