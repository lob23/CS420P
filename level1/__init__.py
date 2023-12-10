from queue import PriorityQueue
from queue import Queue
import pygame
from utils.ui import *
import timeit
import os
import psutil

from utils.read_file import read_file

def memoryMeasyrement():
  pid = os.getpid()
  proc = psutil.Process(pid)
  return proc.memory_info().rss / (1024 ** 2)

class Visualizer:
    visited_score = 0

class Node:
    def __init__(self, position, problem, cost=0, parent=None, spot=None):
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


    def get_neighbors(self, node, visual_grid, explored):
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        neighbors = []

        for dx, dy in directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1' and tuple((x,y)) not in explored:
                neighbors.append(Node((x, y), self, node.cost + 1, node, visual_grid[x][y]))
        for dx, dy in diagonal_directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '-1' and tuple((x,y)) not in explored:
                if self.grid[x][node.position[1]] != '-1' and self.grid[node.position[0]][y] != '-1':
                    neighbors.append(Node((x, y), self, node.cost + 1, node, visual_grid[x][y]))
        return neighbors

    def is_goal(self, node):
        return node.position == self.goal

    # Euclidean distance
    def heuristic(self, node):
        if self.is_heuristic:
            dx = abs(node.position[0] - self.goal[0])
            dy = abs(node.position[1] - self.goal[1])
            d1 = 1
            d2 = 1
            return d1 * (dx + dy) + (d2 - 2 * d1) * min(dx, dy)
        else:
            return 0


def a_star_search(problem, visual_grid, grid_start_x, grid_start_y, rows, columns):
    process = psutil.Process(os.getpid())
    beginMem = process.memory_info().rss
    print(beginMem)
    counter = 0
    start_node = Node(problem.start, problem, 0, None, visual_grid[problem.start[0]][problem.start[1]])
    frontier = PriorityQueue()
    frontier.put(start_node)
    explored = set()
    frontier_set = set()
    frontier_set.add(tuple(start_node.position))
    loop_memory_usage = 0.0
    memory_usage = beginMem
    while not frontier.empty():
        node = frontier.get()
        frontier_set.remove(tuple(node.position))
        if problem.is_goal(node):
            print(counter)
            visual_grid[node.position[0]][node.position[1]].make_closed()
            draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
            return node, loop_memory_usage/1000000.0
        explored.add(tuple(node.position))
        for neighbor in problem.get_neighbors(node, visual_grid, explored):
            if tuple(neighbor.position) not in frontier_set:
                frontier.put(neighbor)
                neighbor.spot.make_open()
                frontier_set.add(tuple(neighbor.position))
            elif tuple(neighbor.position) in frontier_set:
                for item in frontier.queue:
                    if item.position == neighbor.position and item > neighbor:
                        frontier.queue.remove(item)
                        frontier.put(neighbor)
                        neighbor.spot.make_open()
            memory_usage = max(process.memory_info().rss, memory_usage)
            loop_memory_usage = memory_usage - beginMem        # Update the spot's color to represent it has been explored
        visual_grid[node.position[0]][node.position[1]].make_closed()
        pygame.time.delay(10)

        draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
        counter += 1
    Visualizer.visited_score = None
    return None, loop_memory_usage/1000000.0


def bfs_search(problem, visual_grid, grid_start_x, grid_start_y, rows, columns):
    process = psutil.Process(os.getpid())
    beginMem = process.memory_info().rss
    counter = 0
    start_node = Node(problem.start, problem, 0,None, visual_grid[problem.start[0]][problem.start[1]])
    frontier = Queue()
    frontier.put(start_node)
    explored = set()
    frontier_set = set()
    frontier_set.add(tuple(start_node.position))

    loop_memory_usage = 0.0
    memory_usage = beginMem
    while not frontier.empty():
        node = frontier.get()
        frontier_set.remove(tuple(node.position))
        if problem.is_goal(node):
            visual_grid[node.position[0]][node.position[1]].make_path()
            print(counter)
            draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
            return node, loop_memory_usage/1000000.0

        explored.add(tuple(node.position))

        for neighbor in problem.get_neighbors(node, visual_grid, explored):
            if tuple(neighbor.position) not in frontier_set:
                frontier.put(neighbor)
                neighbor.spot.make_open()
                frontier_set.add(tuple(neighbor.position))
            # elif tuple(neighbor.position) in frontier_set:
            #     for item in frontier.queue:
            #         if item.position == neighbor.position and item > neighbor:
            #             frontier.queue.remove(item)
            #             frontier.put(neighbor)
            #             neighbor.spot.make_open()
            memory_usage = max(process.memory_info().rss, memory_usage)
            loop_memory_usage = memory_usage - beginMem
        counter += 1
        visual_grid[node.position[0]][node.position[1]].make_closed()
        pygame.time.delay(10)

        draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)

    Visualizer.visited_score = None
    return None, loop_memory_usage/1000000.0


def dfs_search(problem, visual_grid, grid_start_x, grid_start_y, rows, columns):
    process = psutil.Process(os.getpid())
    beginMem = process.memory_info().rss
    counter = 0
    start_node = Node(problem.start, problem, 0, None, visual_grid[problem.start[0]][problem.start[1]])
    frontier = [start_node]
    explored = set()
    frontier_set = set()
    frontier_set.add(tuple(start_node.position))
    
    loop_memory_usage = 0.0
    memory_usage = beginMem
    while len(frontier) != 0:
        memory_usage = max(process.memory_info().rss, memory_usage)
        loop_memory_usage = memory_usage - beginMem  
        node = frontier.pop()
        frontier_set.remove(tuple(node.position))
        if problem.is_goal(node):
            print(counter)
            return node,  loop_memory_usage/1000000.0
        explored.add(tuple(node.position))
        node.spot.make_closed()
        draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)

        for neighbor in problem.get_neighbors(node, visual_grid, explored):
            memory_usage = max(process.memory_info().rss, memory_usage)
            loop_memory_usage = memory_usage - beginMem  
            if tuple(neighbor.position) not in frontier_set:
                frontier.append(neighbor)
                neighbor.spot.make_open()
                frontier_set.add(tuple(neighbor.position))
        counter += 1
        pygame.time.delay(10)
        draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
    Visualizer.visited_score = None
    return None, loop_memory_usage/1000000.0


def ucs(problem, visual_grid, grid_start_x, grid_start_y, rows, columns):
    process = psutil.Process(os.getpid())
    beginMem = process.memory_info().rss
    counter = 0
    start_node = Node(problem.start, problem, 0,None, visual_grid[problem.start[0]][problem.start[1]])
    frontier = PriorityQueue()
    explored = set()
    frontier.put(start_node)
    frontier_set = set()
    frontier_set.add(tuple(start_node.position))
    loop_memory_usage = 0.0
    memory_usage = beginMem
    while not frontier.empty():
        node = frontier.get()
        frontier_set.remove(tuple(node.position))
        if problem.is_goal(node):
            print(counter)
            draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
            return node, loop_memory_usage/1000000.0
        explored.add(tuple(node.position))
        node.spot.make_closed()
        for neighbor in problem.get_neighbors(node, visual_grid, explored):
            if tuple(neighbor.position) not in frontier_set:
                frontier.put(neighbor)
                neighbor.spot.make_open()
                frontier_set.add(tuple(neighbor.position))
            elif tuple(neighbor.position) in frontier_set:
                for item in frontier.queue:
                    if item.position == neighbor.position and item > neighbor:
                        frontier.queue.remove(item)
                        frontier.put(neighbor)
                        neighbor.spot.make_open()
            memory_usage = max(process.memory_info().rss, memory_usage)
            loop_memory_usage = memory_usage - beginMem        
        counter += 1
        pygame.time.delay(10)
        draw(WIN, visual_grid, rows, columns, WIDTH, grid_start_x, grid_start_y)
    Visualizer.visited_score = None
    return None, loop_memory_usage/1000000.0


def print_path(node):
    if node is None:
        print("No path found")
        return
    node.spot.make_end()
    node = node.parent
    counter = 1
    while node.parent is not None:
        node.spot.make_path()
        node = node.parent
        counter += 1
    node.spot.make_start()
    Visualizer.visited_score = counter
    return

def print_grid(ROWS, COLUMN, grid, start_position=None, goal_position=None):
    visual_grid = make_grid(ROWS, COLUMN, WIDTH)

    grid[goal_position[0]][goal_position[1]] = '0'
    grid[start_position[0]][start_position[1]] = '0'
    visual_grid[goal_position[0]][goal_position[1]].make_end()
    visual_grid[start_position[0]][start_position[1]].make_start()

    row_index = 0
    for line in grid:
    #     # if 'A1' in line:
    #     #     start_position_column = line.index('A1')
    #     #     start_position = (row_index, start_position_column)
    #     #     grid[row_index][start_position_column] = '0'
    #     #     visual_grid[row_index][start_position_column].make_start()
    #     #
    #     # if 'T1' in line:
    #     #     start_position_column = line.index('T1')
    #     #     goal_position = (row_index, start_position_column)
    #     #     grid[row_index][start_position_column] = '0'
    #     #     visual_grid[row_index][start_position_column].make_end()
    #
        for column_index, cell in enumerate(line):
            if cell == '-1':
                visual_grid[row_index][column_index].make_barrier()

        row_index += 1
    return visual_grid


def level1(url):
    # Example usage
    file = read_file(url)
    print(file)
    ROWS = file['floor1']['height']
    COLUMN = file['floor1']['width']
    x,y,z = file['atkds']['A1']
    start_position = (x, y)
    x,y,z = file['atkds']['T1']
    goal_position = (x, y)

    # visual_grid = make_grid(ROWS, COLUMN, WIDTH)

    # Calculate the total grid size
    total_grid_width = COLUMN * (WIDTH // COLUMN)
    total_grid_height = ROWS * (WIDTH // ROWS)

    print(total_grid_width, total_grid_height)

    # Calculate the starting position to center the grid
    grid_start_x = (WIDTH - total_grid_width) // 2
    grid_start_y = (WIDTH - total_grid_height) // 2

    print(grid_start_x, grid_start_y)

    grid = file['floor1']['floor_data']
    # print(len(grid), len(grid[0]))
    visual_grid = print_grid(ROWS, COLUMN, grid, start_position, goal_position)

    problem = Problem(grid, start_position, goal_position, is_heuristic=True)

    print(grid, start_position, goal_position)

    run = True
    play_again = False
    while run:
        # command = -1
        # Add draw menu before draw grid
        command = draw_menu_level1()

        # if play_again and command > 0:
        #     visual_grid, start_position, goal_position = print_grid(ROWS, COLUMN, grid, start_position, goal_position)
        #     play_again = False

        if play_again and command > 0:
            visual_grid = print_grid(ROWS, COLUMN, grid, start_position, goal_position)
            play_again = False

        print_score(Visualizer.visited_score)
        draw(WIN, visual_grid, ROWS, COLUMN, WIDTH, grid_start_x, grid_start_y)

        pygame.display.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if pygame.MOUSEBUTTONDOWN:
                if command == 0:
                    run = False
                elif command == 1:
                    Visualizer.visited_score = 0
                    problem.is_heuristic = False
                    start = timeit.default_timer()
                    node, memory = dfs_search(problem, visual_grid, grid_start_x, grid_start_y, ROWS, COLUMN)
                    stop = timeit.default_timer()
                    print('Time: ', stop - start)
                    print('Memory consumption: ', memory)
                    print_path(node)
                    command = -1
                    play_again = True
                elif command == 2:
                    Visualizer.visited_score = 0
                    problem.is_heuristic = False
                    start = timeit.default_timer()
                    node, memory = (bfs_search(problem, visual_grid, grid_start_x, grid_start_y, ROWS, COLUMN))
                    stop = timeit.default_timer()
                    print('Time: ', stop - start)
                    print('Memory consumption: ', memory)
                    print_path(node)
                    command = -1
                    play_again = True

                elif command == 3:
                    Visualizer.visited_score = 0
                    problem.is_heuristic = False
                    start = timeit.default_timer()
                    path, memory = ucs(problem, visual_grid, grid_start_x, grid_start_y, ROWS, COLUMN)
                    stop = timeit.default_timer()
                    print('Time: ', stop - start)
                    print('Memory consumption: ', memory)
                    print_path(path)
                    command = -1
                    play_again = True

                elif command == 4:
                    Visualizer.visited_score = 0
                    problem.is_heuristic = True
                    start = timeit.default_timer()
                    node, memory = (a_star_search(problem, visual_grid, grid_start_x, grid_start_y, ROWS, COLUMN))
                    stop = timeit.default_timer()
                    print('Time: ', stop - start)
                    print('Memory consumption: ', memory)
                    print_path(node)
                    command = -1
                    play_again = True
        pygame.display.flip()

        # pygame.display.update()


# Example usage
# file = read_file('./level1/input.txt')
# ROWS = file['floor1']['height']
# COLUMN = file['floor1']['width']
# start_position = ()
# goal_position = ()
# start_position_column = -1
# goal_position_column = -1
# row_index = 0
#
# visual_grid = make_grid(ROWS, COLUMN, WIDTH)
#
# # Calculate the total grid size
# total_grid_width = COLUMN * (WIDTH // COLUMN)
# total_grid_height = ROWS * (WIDTH // COLUMN)
#
# # Calculate the starting position to center the grid
# grid_start_x = (WIDTH - total_grid_width) // 2
# grid_start_y = (WIDTH - total_grid_height) // 2
#
# grid = file['floor1']['floor_data']
# for line in grid:
#     if 'A1' in line:
#         start_position_column = line.index('A1')
#         start_position = (row_index, start_position_column)
#         grid[row_index][start_position_column] = '0'
#         visual_grid[row_index][start_position_column].make_start()
#
#     if 'T1' in line:
#         start_position_column = line.index('T1')
#         goal_position = (row_index, start_position_column)
#         grid[row_index][start_position_column] = '0'
#         visual_grid[row_index][start_position_column].make_end()
#
#     for column_index, cell in enumerate(line):
#         if cell == '-1':
#             visual_grid[row_index][column_index].make_barrier()
#
#     row_index += 1
#
# problem = Problem(grid, start_position, goal_position, is_heuristic=False)
# ucs(problem, visual_grid)