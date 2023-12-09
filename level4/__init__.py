import copy
import math
import random
import re
from queue import Queue, PriorityQueue

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
    F = None


# Visual grid
class Visualizer:
    visual_map = None
    visual_grid = None
    grid_start_x = None
    grid_start_y = None
    visited_score = 0



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
        return self.cost() < other.cost()

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
                if (x, y, z) == Dnode.vgoal:
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

    def reconstruct_path(self, start: str, goal: str):
        path = []
        node = self
        while node:
            path.append((None, node.value[0], node.value[1], Pnode.level))
            node = node.parent
        path.reverse()
        path[0] = (start, path[0][1], path[0][2], path[0][3])
        path[len(path) - 1] = (goal, path[len(path) - 1][1], path[len(path) - 1][2], path[len(path) - 1][3])
        return path

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
            if current_node.value not in visited:
                if current_node.value == Pnode.vgoal:
                    x = current_node.reconstruct_path(start.name, goal.name)
                    return x
                visited.add(current_node.value)
                for child in current_node.children():
                    index = next((i for i, e in enumerate(frontier.queue) if e.value == child.value), -1)
                    if child.value not in visited and index == -1:
                        frontier.put(child)
                    elif index != -1 and frontier.queue[index].cost() > child.cost():
                        frontier.queue.pop(index)
                        frontier.put(child)
        return None


def find_dtree(map_data, start: str, goal: str, keys=None, debug=False):
    Dnode.map_data = map_data
    Dnode.goal = goal
    Dnode.vgoal = map_data['atkds'][Dnode.goal]
    start = Dnode(start, map_data['atkds'][start])
    if keys is not None:
        start.keys = keys
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if debug:
            print(current_node)
        if (current_node.value, tuple(current_node.keys)) not in visited:
            if current_node.name == Dnode.goal:
                # Visualizer.visual_grid[current_node.value[2] - 1][current_node.value[0]][current_node.value[1]].make_end()
                return current_node.reconstruct_path()
            visited.add((current_node.value, tuple(current_node.keys)))
            for child in current_node.children():
                index = next(
                    (i for i, e in enumerate(frontier.queue) if e.value == child.value and e.keys == child.keys),
                    -1)
                if (child.value, tuple(child.keys)) not in visited and index == -1:
                    frontier.put(child)
                    # Visualizer.visual_grid[child.value[2] - 1][child.value[0]][child.value[1]].make_start()
                elif index != -1 and frontier.queue[index].cost() > child.cost():
                    frontier.queue.pop(index)
                    frontier.put(child)
    return None


def find_path(map_data, dtree):
    Pnode.valid.clear()
    Pnode.valid.add("0")
    for key in map_data['atkds'].keys():
        if key.startswith("A") or key.startswith("T"):
            Pnode.valid.add(key)
    path = Pnode.a_star(map_data, dtree[0], dtree[1])
    for i in range(1, len(dtree) - 1):
        path.extend(Pnode.a_star(map_data, dtree[i], dtree[i + 1])[1:])
    return path


class Agent:
    map_data = None

    def __init__(self, start, goal, path=None, current=0, keys=None):
        self.start = start
        self.goal = goal
        self.path = path
        self.keys = keys
        self.__current = current
        if self.path is None:
            dtree = find_dtree(Agent.map_data, self.start, self.goal)
            self.keys = dtree[-1].keys
            self.path = find_path(Agent.map_data, dtree)


    def cell(self):
        return self.path[self.__current][1], self.path[self.__current][2], self.path[self.__current][3]

    def makecopy(self):
        return Agent(self.start, self.goal, self.path.copy(), self.__current, self.keys.copy())

    def move(self, agents):
        if self.__current < len(self.path) - 1:
            self.__current += 1
            for agent in agents:
                if self.start != agent.start:
                    if self.cell() == agent.cell():
                        self.__current -= 1
                        return 0
            if self.start != 'A1' and self.__current == len(self.path) - 1:
                Agent.map_data['atkds'][self.start] = self.path[self.__current][1:]
                Agent.map_data[f'floor{self.path[self.__current][3]}']['floor_data'][self.path[self.__current][1]][self.path[self.__current][2]] = self.start
                Agent.map_data[f'floor{self.path[0][3]}']['floor_data'][self.path[0][1]][self.path[0][2]] = '0'
                while True:
                    x = random.randint(0, Boundary.N - 1)
                    y = random.randint(0, Boundary.M - 1)
                    z = random.randint(1, Boundary.F)
                    if Agent.map_data[f'floor{z}']['floor_data'][x][y] == '0':
                        Agent.map_data['atkds'].update({self.goal: (x, y, z)})
                        Agent.map_data[f'floor{z}']['floor_data'][x][y] = self.goal
                        self.__current = 0
                        self.path = find_path(Agent.map_data, find_dtree(Agent.map_data, self.start, self.goal, self.keys))
                        break
                return 1
        return 2

    def is_at_goal(self):
        return self.__current == len(self.path) - 1

    def __str__(self):
        return self.start + " " + str(self.cell())


class Anode:
    n = None
    combinations = None

    def __init__(self, agents, parent=None, t=0, combination='1111111111'):
        self.parent = parent
        self.agents = agents
        self.combination = combination
        self.t = t

    def __lt__(self, other):
        return self.t + self.h() < other.t + other.h()

    def h(self):
        dec = int(self.combination, 2)
        # return dec flipped
        return dec ^ (2 ** (len(self.combination) + 1) - 1)

    def __str__(self):
        agents = [str(agent) for agent in self.agents]
        return " ".join(agents) + " " + str(self.t)

    def __copy_agents(self):
        agents = []
        for agent in self.agents:
            agents.append(agent.makecopy())
        return agents

    def children(self):
        children = []
        for combination in Anode.combinations:
            move = 0
            agents = self.__copy_agents()
            for i, agent in enumerate(agents):
                if combination[move] == '1':
                    agent.move(agents)
                move += 1
            children.append(Anode(agents, self, self.t + 1, combination))
        return children

    def reconstruct_path(self):
        path = []
        node = self
        while node is not None:
            Visualizer.visited_score += 1
            for i in range(Anode.n):
                pygame.time.wait(100)
                draw_menu_level3(node.agents[i].cell()[2] - 1)
                draw(WIN, Visualizer.visual_grid[node.agents[i].cell()[2] - 1], Boundary.N, Boundary.M, WIDTH,
                     Visualizer.grid_start_x,
                     Visualizer.grid_start_y)
                Visualizer.visual_grid[node.agents[i].cell()[2] - 1][node.agents[i].cell()[0]][node.agents[i].cell()[1]].make_visited()
                pygame.display.update()
            path.append(node)
            node = node.parent
        return path[::-1]


def mapf(map_data):
    Boundary.N = map_data['floor1']['height']
    Boundary.M = map_data['floor1']['width']
    Boundary.F = map_data['floor_count']
    Agent.map_data = copy.deepcopy(map_data)
    count = 0
    agents = []
    for agent in map_data['atkds'].keys():
        if agent.startswith('A'):
            agents.append(Agent(agent, 'T' + agent[1:]))
            count += 1
    agents.sort(key=lambda x: x.start)
    Anode.n = count
    Anode.combinations = sorted([bin(i)[2:].zfill(count) for i in range(2 ** count)][1:])
    start = Anode(agents)
    frontier = PriorityQueue()
    frontier.put(start)
    visited = set()
    while not frontier.empty():
        current_node = frontier.get_nowait()
        if tuple([agent.cell() for agent in current_node.agents]) not in visited:
            if current_node.agents[0].cell() == current_node.agents[0].path[-1][1:]:
                return current_node.reconstruct_path()
            visited.add(tuple([agent.cell() for agent in current_node.agents]))
            for child in current_node.children():
                index = next((i for i, e in enumerate(frontier.queue) if tuple([agent.cell() for agent in e.agents]) == tuple([agent.cell() for agent in child.agents])), -1)
                if tuple([agent.cell() for agent in child.agents]) not in visited and index == -1:
                    frontier.put(child)
                elif index != -1 and frontier.queue[index].t > child.t:
                    frontier.queue.pop(index)
                    frontier.put(child)
    return None

def print_visual_grid(map_data):
    visual_map = []
    for floor, floor_data in map_data.items():
        # Check if the data is a floor
        if re.search(r'^floor\d+$', floor) is not None:
            visual_map.append(make_grid(Boundary.N, Boundary.M, WIDTH))
            for i in range(Boundary.N):
                for j in range(Boundary.M):
                    if floor_data['floor_data'][i][j] == "-1":
                        visual_map[-1][i][j].make_barrier()
                    elif floor_data['floor_data'][i][j].startswith("T"):
                        visual_map[-1][i][j].make_closed_agent(floor_data['floor_data'][i][j])
                    elif floor_data['floor_data'][i][j].startswith("A"):
                        visual_map[-1][i][j].make_agent(floor_data['floor_data'][i][j])
                    elif floor_data['floor_data'][i][j].startswith("K"):
                        visual_map[-1][i][j].make_key(floor_data['floor_data'][i][j])
                    elif re.search(r'^D(\d+)$', floor_data['floor_data'][i][j]) is not None:
                        visual_map[-1][i][j].make_door(floor_data['floor_data'][i][j])
                    elif floor_data['floor_data'][i][j] == "DO":
                        visual_map[-1][i][j].make_door("DO")
                    elif floor_data['floor_data'][i][j] == "UP":
                        visual_map[-1][i][j].make_door("UP")

    return visual_map


def level4(url):
    map_data = read_file(url)
    Boundary.N = map_data[f'floor{1}']['height']  # Row
    Boundary.M = map_data[f'floor{1}']['width']  # Column

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
    Visualizer.visual_grid = visual_map


    while run:
        # Draw the visualizer
        command = draw_menu_level3(floor_index)
        if playagain:
            playagain = False
            Visualizer.visual_grid = print_visual_grid(map_data)

        print_score(Visualizer.visited_score)

        draw(WIN, visual_map[floor_index], Boundary.N, Boundary.M, WIDTH, grid_start_x, grid_start_y)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                playagain = False
                pygame.quit()
            if pygame.MOUSEBUTTONDOWN:
                if command == 1:
                    playagain = True
                    Visualizer.visited_score = 0
                    map_data = read_file(url)
                    visual_map = print_visual_grid(map_data)
                    Visualizer.visual_grid = visual_map
                    solution = mapf(map_data)

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






def test():
    map_data = read_file('test.txt')
    solution = mapf(map_data)

    for e in solution:
        print(e)

# test()