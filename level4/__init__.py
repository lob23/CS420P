import math
from queue import Queue, PriorityQueue
import re


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
                    children.append(Dnode(grid[x][y], (x, y, z), self, self.g + c))
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
            current_node = frontier.get_nowait()
            if current_node is not None and current_node.value not in visited:
                if current_node.value == Pnode.vgoal:
                    return current_node.reconstruct_path()
                visited.add(current_node.value)
                for child in current_node.children():
                    index = next((i for i, e in enumerate(frontier.queue) if e is not None and e.value == child.value), -1)
                    if child.value not in visited and index == -1:
                        frontier.put(child)
                    elif index != -1 and frontier.queue[index].cost() > child.cost():
                        frontier.queue[index] = None
                        frontier.put(child)
        return None


def find_dtree(map_data, agent, task):
    Dnode.map_data = map_data
    Dnode.goal = task
    Dnode.vgoal = map_data['atkds'][Dnode.goal]
    start = Dnode(agent, map_data['atkds'][agent])
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if current_node is not None and (current_node.value, tuple(current_node.keys)) not in visited:
            if current_node.name == Dnode.goal:
                return current_node.reconstruct_path()
            visited.add((current_node.value, tuple(current_node.keys)))
            for child in current_node.children():
                index = next(
                    (i for i, e in enumerate(frontier.queue) if e is not None and e.value == child.value and e.keys == child.keys),
                    -1)
                if (child.value, tuple(child.keys)) not in visited and index == -1:
                    frontier.put(child)
                elif index != -1 and frontier.queue[index].cost() > child.cost():
                    frontier.queue[index] = None
                    frontier.put(child)
    return None


def find_path(map_data, dtree):
    Pnode.valid.clear()
    Pnode.valid.add("0")
    path = Pnode.a_star(map_data, dtree[0], dtree[1])
    for i in range(1, len(dtree) - 1):
        path.extend(Pnode.a_star(map_data, dtree[i], dtree[i + 1])[1:])
    return path


class Agent:
    def __init__(self, name: str, start: (int, int, int), goal: (int, int, int), path: list[(int, int, int)]):
        self.name = name
        self.start = start
        self.goal = goal
        self.path = path