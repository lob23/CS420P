import math
import re
from queue import Queue, PriorityQueue
from utils.read_file import read_file


def octile_distance(source, target):
    dx = abs(source[0] - target[0])
    dy = abs(source[1] - target[1])
    return dx + dy + (math.sqrt(2) - 2) * min(dx, dy)


def chebyshev_distance(source, target):
    return max(abs(source[0] - target[0]), abs(source[1] - target[1]), abs(source[2] - target[2]))


class Boundary:
    N = None
    M = None


class Dnode:
    goal = None
    vgoal = None
    map_data = None

    def __init__(self, name, parent=None, g=0):
        self.parent = parent
        self.name = name
        self.keys = parent.keys.copy() if parent is not None else set()
        self.value = Dnode.map_data['atkds'][name]
        self.g = g
        if self.name.startswith("K") and self.name[1:] not in self.keys:
            self.keys.add(self.name[1:])

    def __lt__(self, other):
        return self.cost() < other.cost()

    def __str__(self):
        return self.name

    def h(self):
        return chebyshev_distance(self.value, Dnode.vgoal)

    def cost(self):
        return self.h() + self.g

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
        queue.put((self.value[0], self.value[1]))
        while not queue.empty():
            x, y = queue.get()
            if (x, y) not in visited:
                visited.add((x, y))
                if grid[x][y].startswith("T"):
                    return [Dnode(grid[x][y], self)]
                if (x, y) != (self.value[0], self.value[1]):
                    if grid[x][y] == "DO" or grid[x][y] == "UP":
                        children.append(Dnode(grid[x][y] + str(z), self, chebyshev_distance(self.value, (x, y, z))))
                    elif grid[x][y].startswith("K"):
                        children.append(Dnode(grid[x][y], self, chebyshev_distance(self.value, (x, y, z))))
                    elif re.search(r'^D(\d+)$', grid[x][y]) is not None:
                        children.append(Dnode(grid[x][y], self, chebyshev_distance(self.value, (x, y, z))))
                        continue
                if x > 0 and grid[x - 1][y] != "-1":
                    queue.put((x - 1, y))
                if x < Boundary.N - 1 and grid[x + 1][y] != "-1":
                    queue.put((x + 1, y))
                if y > 0 and grid[x][y - 1] != "-1":
                    queue.put((x, y - 1))
                if y < Boundary.M - 1 and grid[x][y + 1] != "-1":
                    queue.put((x, y + 1))
                if (x, y + 1) in visited and (x + 1, y) in visited and grid[x + 1][y + 1] != "-1":
                    queue.put((x + 1, y + 1))
                if (x + 1, y) in visited and (x, y - 1) in visited and grid[x + 1][y - 1] != "-1":
                    queue.put((x + 1, y - 1))
                if (x, y - 1) in visited and (x - 1, y) in visited and grid[x - 1][y - 1] != "-1":
                    queue.put((x - 1, y - 1))
                if (x - 1, y) in visited and (x, y + 1) in visited and grid[x - 1][y + 1] != "-1":
                    queue.put((x - 1, y + 1))
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
        return self.cost() < other.cost()

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
            current_node = frontier.get_nowait()
            if current_node.value not in visited:
                if current_node.value == Pnode.vgoal:
                    return current_node.reconstruct_path()
                visited.add(current_node.value)
                for child in current_node.children():
                    index = next((i for i, e in enumerate(frontier.queue) if e.value == child.value), -1)
                    if child.value not in visited and index == -1:
                        frontier.put(child)
                    elif index != -1 and frontier.queue[index].cost() > child.cost():
                        frontier.queue[index] = child
        return None


def find_dtree(map_data):
    Dnode.map_data = map_data
    Dnode.goal = 'T1'
    Dnode.vgoal = map_data['atkds'][Dnode.goal]
    start = Dnode('A1')
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if (current_node.name, tuple(current_node.keys)) not in visited:
            if current_node.name == Dnode.goal:
                return current_node.reconstruct_path()
            visited.add((current_node.name, tuple(current_node.keys)))
            for child in current_node.children():
                index = next((i for i, e in enumerate(frontier.queue) if e.name == child.name and e.keys == child.keys),
                             -1)
                if (child.name, tuple(child.keys)) not in visited and index == -1:
                    frontier.put(child)
                elif index != -1 and frontier.queue[index].cost() > child.cost():
                    frontier.queue[index] = child
    return None


def simple_visualizer(map_data, path):
    grid = map_data[f"floor{path[0][2]}"]["floor_data"]
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "-1":
                print("X", end=" ")
            elif (i, j, path[0][2]) in path:
                print("O", end=" ")
            else:
                print(" ", end=" ")
        print()


def find_path(map_data, dtree):
    Pnode.valid.clear()
    Pnode.valid.add("0")
    path = Pnode.a_star(map_data, dtree[0], dtree[1])
    for i in range(1, len(dtree) - 1):
        path.extend(Pnode.a_star(map_data, dtree[i], dtree[i + 1])[1:])
    return path


def level3(file):
    map_data = read_file(file)
    Boundary.N = map_data[f'floor{1}']['height']
    Boundary.M = map_data[f'floor{1}']['width']
    dtree = find_dtree(map_data)
    return find_path(map_data, dtree)

# MAP_DATA = read_file('./level3/test.txt')
# Boundary.N = MAP_DATA[f'floor{1}']['height']
# Boundary.M = MAP_DATA[f'floor{1}']['width']
# DTREE = find_dtree(MAP_DATA)
# for NODE in DTREE:
#     print(NODE.name)
# print()
# print(find_path(MAP_DATA, DTREE))
