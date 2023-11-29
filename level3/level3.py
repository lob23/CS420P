import re
from queue import Queue, PriorityQueue
from utils.read_file import read_file


def chebyshev_distance(source, target):
    return max(abs(source[0] - target[0]), abs(source[1] - target[1]), abs(source[2] - target[2]))


class Node:
    goal = None
    vgoal = None
    map_data = None
    n = None
    m = None

    def __init__(self, name, parent=None, g=0):
        self.parent = parent
        self.name = name
        self.keys = parent.keys.copy() if parent is not None else set()
        self.value = Node.map_data['atkds'][name]
        self.g = g
        if self.name.startswith("K") and self.name[1:] not in self.keys:
            self.keys.add(self.name[1:])

    def __lt__(self, other):
        return self.cost() < other.cost()

    def __str__(self):
        return self.name

    def h(self):
        return chebyshev_distance(self.value, Node.vgoal)

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
        grid = Node.map_data[f"floor{z}"]["floor_data"]
        queue.put((self.value[0], self.value[1]))
        while not queue.empty():
            x, y = queue.get()
            if (x, y) not in visited:
                visited.add((x, y))
                if grid[x][y].startswith("T"):
                    return [Node(grid[x][y], self)]
                if (x, y) != (self.value[0], self.value[1]):
                    if grid[x][y] == "DO" or grid[x][y] == "UP":
                        children.append(Node(grid[x][y] + str(z), self, chebyshev_distance(self.value, (x, y, z))))
                    elif grid[x][y].startswith("K") or re.search(r'^D(\d+)$', grid[x][y]) is not None:
                        children.append(Node(grid[x][y], self, chebyshev_distance(self.value, (x, y, z))))
                        if grid[x][y][1:] not in self.keys:
                            continue
                if x > 0 and grid[x - 1][y] != "-1":
                    queue.put((x - 1, y))
                if x < Node.n - 1 and grid[x + 1][y] != "-1":
                    queue.put((x + 1, y))
                if y > 0 and grid[x][y - 1] != "-1":
                    queue.put((x, y - 1))
                if y < Node.m - 1 and grid[x][y + 1] != "-1":
                    queue.put((x, y + 1))
                if (x, y + 1) in visited and (x + 1, y) in visited:
                    queue.put((x + 1, y + 1))
                if (x + 1, y) in visited and (x, y - 1) in visited:
                    queue.put((x + 1, y - 1))
                if (x, y - 1) in visited and (x - 1, y) in visited:
                    queue.put((x - 1, y - 1))
                if (x - 1, y) in visited and (x, y + 1) in visited:
                    queue.put((x - 1, y + 1))
        return children


def reconstruct_path(node):
    path = []
    while node:
        path.append(node.name)
        node = node.parent
    return path[::-1]


def find_path(map_data):
    Node.map_data = map_data
    Node.n = map_data[f'floor{1}']['height']
    Node.m = map_data[f'floor{1}']['width']
    Node.goal = 'T1'
    Node.vgoal = map_data['atkds'][Node.goal]
    start = Node('A1')
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if (current_node.name, tuple(current_node.keys)) not in visited:
            if current_node.name == Node.goal:
                return reconstruct_path(current_node)
            visited.add((current_node.name, tuple(current_node.keys)))
            for child in current_node.children():
                index = next((i for i, e in enumerate(frontier.queue) if e.name == child.name and e.keys == child.keys), -1)
                if (child.name, tuple(child.keys)) not in visited and index == -1:
                    frontier.put(child)
                elif index != -1 and frontier.queue[index].cost() > child.cost():
                    frontier.queue[index] = child
    return None


map_data = read_file('./level3/test.txt')
print(map_data)
print(find_path(map_data))
