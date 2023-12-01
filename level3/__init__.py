import heapq
import math
import re
import timeit
from queue import Queue, PriorityQueue

import pygame

from utils.read_file import read_file
from utils.ui import *


def octile_distance(source, target):
    dx = abs(source[0] - target[0])
    dy = abs(source[1] - target[1])
    return dx + dy + (math.sqrt(2) - 2) * min(dx, dy)


def chebyshev_distance(source, target):
    return max(abs(source[0] - target[0]), abs(source[1] - target[1]), abs(source[2] - target[2]))


class Boundary:
    N = None
    M = None

# Visual grid
class Visualizer:
    visual_grid = None
    grid_start_x = None
    grid_start_y = None


class Dnode:
    goal = None
    vgoal = None
    map_data = None

    def __init__(self, name: str, value: (int, int, int), parent=None, g=0):
        self.parent = parent
        self.name = name
        self.keys = parent.keys.copy() if parent is not None else set()
        self.value = value
        self.g = g
        if self.name.startswith("K") and self.name[1:] not in self.keys:
            self.keys.add(self.name[1:])

    def __lt__(self, other):
        return True if other is None else self.cost() < other.cost()

    def __str__(self):
        return self.name

    def cost(self):
        return self.g

    @staticmethod
    def is_reachable(cell):
        return cell != "-1"

    def children(self):
        queue = Queue()
        children = []
        visited = set()
        if re.search(r'^D(\d+)$', self.name) is not None and self.name[1:] not in self.keys:
            return []
        if self.name.startswith("UP"):
            z = self.value[2] + 1
        elif self.name.startswith("DO"):
            z = self.value[2] - 1
        else:
            z = self.value[2]
        grid = Dnode.map_data[f"floor{z}"]["floor_data"]
        queue.put((self.value[0], self.value[1], 0))
        while not queue.empty():
            x, y, c = queue.get()
            if (x, y) not in visited:
                visited.add((x, y))
                if grid[x][y].startswith("T"):
                    children.append(Dnode(grid[x][y], (x, y, z), self,  self.g + c))
                    continue
                if (x, y) != (self.value[0], self.value[1]):
                    if grid[x][y] == "DO" or grid[x][y] == "UP":
                        children.append(Dnode(grid[x][y] + str(z), (x, y, z), self, self.g + c))
                    elif grid[x][y].startswith("K"):
                        children.append(Dnode(grid[x][y], (x, y, z), self, self.g + c))
                    elif re.search(r'^D(\d+)$', grid[x][y]) is not None:
                        children.append(Dnode(grid[x][y], (x, y, z), self, self.g + c))
                        continue
                if x > 0 and Dnode.is_reachable(grid[x - 1][y]):
                    queue.put((x - 1, y, c + 1))
                if x < Boundary.N - 1 and Dnode.is_reachable(grid[x + 1][y]):
                    queue.put((x + 1, y, c + 1))
                if y > 0 and Dnode.is_reachable(grid[x][y - 1]):
                    queue.put((x, y - 1, c + 1))
                if y < Boundary.M - 1 and Dnode.is_reachable(grid[x][y + 1]):
                    queue.put((x, y + 1, c + 1))
                if (x, y + 1) in visited and (x + 1, y) in visited and Dnode.is_reachable(grid[x + 1][y + 1]):
                    queue.put((x + 1, y + 1, c + 1))
                if (x + 1, y) in visited and (x, y - 1) in visited and Dnode.is_reachable(grid[x + 1][y - 1]):
                    queue.put((x + 1, y - 1, c + 1))
                if (x, y - 1) in visited and (x - 1, y) in visited and Dnode.is_reachable(grid[x - 1][y - 1]):
                    queue.put((x - 1, y - 1, c + 1))
                if (x - 1, y) in visited and (x, y + 1) in visited and Dnode.is_reachable(grid[x - 1][y + 1]):
                    queue.put((x - 1, y + 1, c + 1))
        return children

    def reconstruct_path(self):
        path = []
        node = self
        while node:
            path.append(node)
            node = node.parent
        return path[::-1]


class Pnode:
    goal = None
    vgoal = None
    grid = None
    level = None
    valid = set()

    def __init__(self, value, parent=None, g=0):
        self.parent = parent
        self.value = value
        self.g = g

    def __lt__(self, other):
        return True if other is None else self.cost() < other.cost()

    def h(self):
        return octile_distance(self.value, Pnode.vgoal)

    def cost(self):
        return self.h() + self.g

    @staticmethod
    def preprocessing_goal(goal):
        if goal.startswith("DO") or goal.startswith("UP"):
            return goal[:2]
        else:
            return goal

    def children(self):
        children = []
        x = self.value[0]
        y = self.value[1]
        hv = [False, False, False, False]  # up, right, down, left
        if x > 0 and Pnode.grid[x - 1][y] in Pnode.valid:
            children.append(Pnode((x - 1, y), self, self.g + 1))
            hv[3] = True
        if x < Boundary.N - 1 and Pnode.grid[x + 1][y] in Pnode.valid:
            children.append(Pnode((x + 1, y), self, self.g + 1))
            hv[1] = True
        if y > 0 and Pnode.grid[x][y - 1] in Pnode.valid:
            children.append(Pnode((x, y - 1), self, self.g + 1))
            hv[2] = True
        if y < Boundary.M - 1 and Pnode.grid[x][y + 1] in Pnode.valid:
            children.append(Pnode((x, y + 1), self, self.g + 1))
            hv[0] = True
        if hv[0] and hv[1] and Pnode.grid[x + 1][y + 1] in Pnode.valid:
            children.append(Pnode((x + 1, y + 1), self, self.g + 1))
        if hv[1] and hv[2] and Pnode.grid[x + 1][y - 1] in Pnode.valid:
            children.append(Pnode((x + 1, y - 1), self, self.g + 1))
        if hv[2] and hv[3] and Pnode.grid[x - 1][y - 1] in Pnode.valid:
            children.append(Pnode((x - 1, y - 1), self, self.g + 1))
        if hv[3] and hv[0] and Pnode.grid[x - 1][y + 1] in Pnode.valid:
            children.append(Pnode((x - 1, y + 1), self, self.g + 1))
        return children

    def reconstruct_path(self):
        path = []
        node = self
        while node:
            path.append((node.value[0], node.value[1], Pnode.level))
            node = node.parent
        return path[::-1]

    @staticmethod
    def a_star(map_data, start: Dnode, goal: Dnode):
        Pnode.goal = Pnode.preprocessing_goal(goal.name)
        Pnode.level = start.value[2] if start.value[2] == goal.value[2] else goal.value[2]
        Pnode.grid = map_data[f"floor{Pnode.level}"]["floor_data"]
        Pnode.vgoal = (goal.value[0], goal.value[1])
        Pnode.valid.add(Pnode.goal)
        frontier = PriorityQueue()
        frontier.put(Pnode((start.value[0], start.value[1])))
        visited = set()
        while not frontier.empty():
            current_node = frontier.get()
            if current_node is not None and current_node.value not in visited:
                if current_node.value == Pnode.vgoal:
                    # print the visited node to the screen
                    Visualizer.visual_grid[Pnode.level - 1][current_node.value[0]][current_node.value[1]].make_visited()
                    return current_node.reconstruct_path()
                visited.add(current_node.value)
                Visualizer.visual_grid[Pnode.level - 1][current_node.value[0]][current_node.value[1]].make_visited()
                for child in current_node.children():
                    index = next((i for i, e in enumerate(frontier.queue) if e is not None and e.value == child.value), -1)
                    if child.value not in visited and index == -1:
                        frontier.put(child)
                        # Visualizer.visual_grid[Pnode.level - 1][child.value[0]][child.value[1]].make_open()
                    elif index != -1 and frontier.queue[index].cost() > child.cost():
                        frontier.queue[index] = None
                        frontier.put(child)

            pygame.time.delay(100)
            # redraw the screen
            draw_menu_level3(Pnode.level - 1)
            draw(WIN, Visualizer.visual_grid[Pnode.level - 1], Boundary.N, Boundary.M, WIDTH, Visualizer.grid_start_x, Visualizer.grid_start_y)

        return None


def find_dtree(map_data):
    Dnode.map_data = map_data
    Dnode.goal = 'T1'
    Dnode.vgoal = map_data['atkds'][Dnode.goal]
    start = Dnode('A1', map_data['atkds']['A1'])
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if current_node is not None and (current_node.value, tuple(current_node.keys)) not in visited:
            if current_node.name == Dnode.goal:
                # Visualizer.visual_grid[current_node.value[2] - 1][current_node.value[0]][current_node.value[1]].make_end()
                return current_node.reconstruct_path()
            visited.add((current_node.value, tuple(current_node.keys)))
            for child in current_node.children():
                index = next((i for i, e in enumerate(frontier.queue) if e is not None and e.value == child.value and e.keys == child.keys),
                             -1)
                if (child.value, tuple(child.keys)) not in visited and index == -1:
                    frontier.put(child)
                    # Visualizer.visual_grid[child.value[2] - 1][child.value[0]][child.value[1]].make_start()
                elif index != -1 and frontier.queue[index].cost() > child.cost():
                    frontier.queue[index] = None
                    frontier.put(child)
    return None


def simple_visualizer(map_data, path):
    grid = map_data[f"floor{path[0][2]}"]["floor_data"]
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "-1":
                print("-1", end=" ")
            elif (i, j, path[0][2]) in path:
                print(" X", end=" ")
            else:
                print(grid[i][j], end=" ")
        print()


def find_path(map_data, dtree):
    Pnode.valid.clear()
    Pnode.valid.add("0")
    path = Pnode.a_star(map_data, dtree[0], dtree[1])
    for i in range(1, len(dtree) - 1):
        path.extend(Pnode.a_star(map_data, dtree[i], dtree[i + 1])[1:])
    return path


def print_visual_grid(map_data):
    visual_map = []
    for floor, floor_data in map_data.items():
        if floor.startswith("floor"):
            visual_map.append(make_grid(Boundary.N, Boundary.M, WIDTH))
            for i in range(Boundary.N):
                for j in range(Boundary.M):
                    if floor_data['floor_data'][i][j] == "-1":
                        visual_map[-1][i][j].make_barrier()
                    elif floor_data['floor_data'][i][j].startswith("T"):
                        visual_map[-1][i][j].make_end()
                    elif floor_data['floor_data'][i][j].startswith("A"):
                        visual_map[-1][i][j].make_start()
                    elif floor_data['floor_data'][i][j].startswith("K"):
                        visual_map[-1][i][j].make_key(floor_data['floor_data'][i][j])
                    elif re.search(r'^D(\d+)$', floor_data['floor_data'][i][j]) is not None:
                        visual_map[-1][i][j].make_door(floor_data['floor_data'][i][j])
                    elif floor_data['floor_data'][i][j] == "DO":
                        visual_map[-1][i][j].make_door("DO")
                    elif floor_data['floor_data'][i][j] == "UP":
                        visual_map[-1][i][j].make_door("UP")

    return visual_map


def level3(file):
    map_data = read_file(file)
    Boundary.N = map_data[f'floor{1}']['height']  # Row
    Boundary.M = map_data[f'floor{1}']['width']  # Column

    #  Start and End node
    start_node = map_data['atkds']['A1']
    end_node = map_data['atkds']['T1']
    # Calculate the total grid size
    total_grid_width = Boundary.M * (WIDTH // Boundary.M)
    total_grid_height = Boundary.N * (WIDTH // Boundary.N)

    # Calculate the starting position to center the grid
    grid_start_x = (WIDTH - total_grid_width) // 2
    grid_start_y = (WIDTH - total_grid_height) // 2

    Visualizer.grid_start_x = grid_start_x
    Visualizer.grid_start_y = grid_start_y

    # Create the visualizer
    visual_map = print_visual_grid(map_data)

    Visualizer.visual_grid = visual_map

    run = True
    playagain = False
    floor_index = 0
    total_floor = len(visual_map)
    while run:
        # Draw the visualizer
        command = draw_menu_level3(floor_index)
        if playagain:
            playagain = False
            Visualizer.visual_grid = print_visual_grid(map_data)

        draw(WIN, visual_map[floor_index], Boundary.N, Boundary.M, WIDTH, grid_start_x, grid_start_y)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                playagain = False
                pygame.quit()
            if pygame.MOUSEBUTTONDOWN:
                # Run search algorithm
                if command == 1:
                    playagain = True
                    DTREE = find_dtree(map_data)
                    for NODE in DTREE:
                        print(NODE.name)
                    print()
                    path = find_path(map_data, DTREE)
                    for NODE in path:
                        Visualizer.visual_grid[NODE[2] - 1][NODE[0]][NODE[1]].make_path()
                    visual_map[start_node[2] - 1][start_node[0]][start_node[1]].make_start()
                    visual_map[end_node[2] - 1][end_node[0]][end_node[1]].make_end()
                # Go up floor
                if command == 2:
                    playagain = False
                    if floor_index < total_floor - 1:
                        floor_index += 1
                    else:
                        floor_index = 0
                    command = -1
                # Go down floor
                if command == 3:
                    playagain = False
                    if floor_index > 0:
                        floor_index -= 1
                    else:
                        floor_index = total_floor - 1
                #  Exit menu
                if command == 0:
                    playagain = False
                    run = False


            pygame.display.flip()

    #
    # dtree = find_dtree(map_data)
    # return find_path(map_data, dtree)


def test():
    map_data = read_file('./level3/test.txt')
    Boundary.N = map_data[f'floor{1}']['height']
    Boundary.M = map_data[f'floor{1}']['width']
    start = timeit.default_timer()
    dtree = find_dtree(map_data)
    for e in dtree:
        print(e, end=" ")
    print()
    path = find_path(map_data, dtree)
    print(path)
    print(len(path) - 1)
    stop = timeit.default_timer()
    print('Time: ', stop - start)


