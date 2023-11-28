import copy
from collections import OrderedDict
from queue import Queue


def flood_fill(grid: list[list[str]], n, m, start: (int, int)):
    queue = Queue()
    queue.put(start)
    visited = set()
    doors = OrderedDict()
    keys = OrderedDict()
    while not queue.empty():
        x, y = queue.get()
        if (x, y) not in visited:
            visited.add((x, y))
            if grid[x][y].startswith("A") or grid[x][y] == "UP" or grid[x][y] == "DO":
                return None
            elif grid[x][y].startswith("D"):
                doors.update({grid[x][y]: (x, y)})
            elif grid[x][y].startswith("K"):
                keys.update({grid[x][y]: (x, y)})
            if x > 0 and grid[x - 1][y] != "-1":
                queue.put((x - 1, y))
            if x < n - 1 and grid[x + 1][y] != "-1":
                queue.put((x + 1, y))
            if y > 0 and grid[x][y - 1] != "-1":
                queue.put((x, y - 1))
            if y < m - 1 and grid[x][y + 1] != "-1":
                queue.put((x, y + 1))
            if (x, y + 1) in visited and (x + 1, y) in visited:
                queue.put((x + 1, y + 1))
            if (x + 1, y) in visited and (x, y - 1) in visited:
                queue.put((x + 1, y - 1))
            if (x, y - 1) in visited and (x - 1, y) in visited:
                queue.put((x - 1, y - 1))
            if (x - 1, y) in visited and (x, y + 1) in visited:
                queue.put((x - 1, y + 1))
    return doors, keys


def build_decision_tree(map_data, start: (int, int, int), task: (int, int, int)):

    return