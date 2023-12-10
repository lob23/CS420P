import psutil
from queue import PriorityQueue
from queue import Queue
import math
import copy
from collections import deque
import os.path
import timeit
from utils.ui import *

def memoryMeasyrement():
    pid = os.getpid()
    proc = psutil.Process(pid)
    return proc.memory_info().rss / (1024 ** 2)

class Visualizer:
    visual_map = None
    grid_start_x = None
    grid_start_y = None
    rows = None
    columns = None
    visited = 0

    @staticmethod
    def print_visual_grid(grid):
        visual_grid = make_grid(Visualizer.rows, Visualizer.columns, WIDTH)
        for i in range((Visualizer.rows)):
            for j in range((Visualizer.columns)):
                if grid[i][j] == '-1':
                    visual_grid[i][j].make_barrier()
                elif grid[i][j].startswith('T'):
                    visual_grid[i][j].make_end()
                elif grid[i][j].startswith('D'):
                    visual_grid[i][j].make_door(grid[i][j])
                elif grid[i][j].startswith('K'):
                    visual_grid[i][j].make_key(grid[i][j])
                elif grid[i][j].startswith('A'):
                    visual_grid[i][j].make_start()

        return visual_grid

    @staticmethod
    def print_path(path):
        Visualizer.visual_map[path[0][0]][path[0][1]].make_start()
        for i in range(1, len(path)):
            Visualizer.visual_map[path[i][0]][path[i][1]].make_visited()
            draw(WIN, Visualizer.visual_map, Visualizer.rows, Visualizer.columns, WIDTH, Visualizer.grid_start_x,
                 Visualizer.grid_start_y)
            pygame.display.update()
        Visualizer.visual_map[path[-1][0]][path[-1][1]].make_visited()
        Visualizer.visited = len(path)


class game:
    def __init__(self, path=[], gameMap=[[]]):
        self.path = path
        self.gameMap = gameMap
        self.decisionTree = []
        self.keys = {}
        self.doors = {}
        self.goal = ()
        self.agent = None

    def findKeys(self):
        for i in range(len(self.gameMap)):
            for j in range(len(self.gameMap[0])):
                if ("K" in self.gameMap[i][j]):
                    self.keys[self.gameMap[i][j][1:]] = (i, j)

    def findGoalandKeys(self):
        self.findKeys()
        for i in range(len(self.gameMap)):
            for j in range(len(self.gameMap[0])):
                if (self.gameMap[i][j] == "T1"):
                    self.goal = (i, j)  # merge with "D" later
                elif ("D" in self.gameMap[i][j]):
                    if (self.gameMap[i][j][1:] not in self.keys.keys()):
                        self.doors[(i, j)] = []
                    else:
                        self.doors[(i, j)] = self.keys[self.gameMap[i][j][1:]]
                elif ("A" in self.gameMap[i][j]):
                    self.agent = (i, j)
        return True

    # def findRoom(self, agent_pos, explored_nodes, doors, isFirstNode, isOpen):

    #     if(agent_pos[0] < 0 or agent_pos[0] >= len(self.gameMap) or agent_pos[1] < 0 or agent_pos[1] > len(self.gameMap[0])):
    #         return

    #     if(agent_pos in explored_nodes and isFirstNode == False):
    #         return 
    #     else: explored_nodes.add(agent_pos)

    #     if(self.gameMap[agent_pos[0]][agent_pos[1]] == "-1"):
    #         return 

    #     if("D" in self.gameMap[agent_pos[0]][agent_pos[1]] and isFirstNode == False):
    #         doors.append(agent_pos)
    #         return

    #     if(self.isRoom(agent_pos=agent_pos) == False):
    #         isOpen[0] = True
    #         doors.clear()
    #         if ( "A" in self.gameMap[agent_pos[0]][agent_pos[1]]):
    #             doors.append(agent_pos)
    #         return

    #     self.findRoom((agent_pos[0] - 1, agent_pos[1]), explored_nodes, doors, False, isOpen)  
    #     if(isOpen[0] == True):
    #         return None    

    #     self.findRoom((agent_pos[0] + 1, agent_pos[1]), explored_nodes, doors, False, isOpen)
    #     if(isOpen[0] == True):
    #         return None   

    #     self.findRoom((agent_pos[0], agent_pos[1] - 1), explored_nodes, doors, False, isOpen)
    #     if(isOpen[0] == True):
    #         return None   

    #     self.findRoom((agent_pos[0], agent_pos[1] + 1), explored_nodes, doors, False, isOpen)
    #     if(isOpen[0] == True):
    #         return None   

    def findDoor_ver2(self, pos):
        beginMem = memoryMeasyrement()
        frontier = Queue()
        frontier.put((pos, ()))
        explored = set()
        exploredOrder = []
        route = {}
        route[tuple((pos, ()))] = None
        
        while(frontier):
            try:
                node = frontier.get_nowait()
            except:
                return None, beginMem
            
            if(node[0] == self.goal):
                res = self.tree_optain(route, node)
                return res, beginMem
                
            if(tuple(node) in explored):
                continue
            explored.add(node)

            children = self.get_neighbors(node[0])
            for child in children:
                
                if child in self.doors and tuple(self.doors[child]) not in node[1]:
                    continue
                if child in self.keys.values() and child not in node[1]:
                    key_list = list(copy.deepcopy(node[1]))
                    key_list.append(child)
                    frontier.put((child, tuple(key_list)))
                    if(tuple((child, tuple(key_list))) in route):
                        continue
                    route[tuple((child, tuple(key_list)))] = node
                    continue
                if(child, node[1]) not in explored:
                    frontier.put((child, node[1]))
                    if(tuple((child, node[1])) in route):
                        continue
                    route[tuple((child, node[1]))] = node

            # pygame.display.update()
        return None, beginMem
                
                
    
    def tree_optain(self, route, node):
        pack = []
        node = route[node]
        while node != None:
            pack.append(node[0])
            node = route[node]
        return pack
        
    def findDoor(self, pos):
        frontier = deque([[pos, 0]])
        explored = set()
        distenceDetermined = set()

        path = []
        routine = {}
        
        minimumByDoor = {}
        while (frontier):

            node, cost = frontier.popleft()
            if (node in explored):
                continue
            explored.add(node)

            neighbors = self.get_neighbors(node)

            for neighbor in neighbors:
                if (neighbor in self.doors or neighbor == self.agent or neighbor in self.keys.values() or neighbor == self.goal):
                    if (neighbor != pos):
                        if (self.gameMap[neighbor[0]][neighbor[1]] not in minimumByDoor):
                            path.append([neighbor, cost + 1])
                            minimumByDoor[self.gameMap[neighbor[0]][neighbor[1]]] = cost + 1
                        elif self.gameMap[neighbor[0]][neighbor[1]] in minimumByDoor and cost + 1 < minimumByDoor[self.gameMap[neighbor[0]][neighbor[1]]]:
                            for temp_node, temp_cost in path:
                                if self.gameMap[temp_node[0]][temp_node[1]] == self.gameMap[neighbor[0]][neighbor[1]]:
                                    path.remove([temp_node, temp_cost])
                                    break
                            path.append([neighbor, cost + 1])
                        if ((neighbor, pos) not in routine):
                            routine[(neighbor, pos)] = node

                else:
                    frontier.extend([[neighbor, cost + 1]])
                    if ((neighbor, pos) not in routine):
                        routine[(neighbor, pos)] = node
            
        return (path, routine)

    def exploreDoor(self, door_list, door):

        frontier = [[d, set()] for d in door]
        newExplored = set()
        # if(not door): return door_list

        while (frontier):
            currentDoor, explored_current = frontier.pop(0)
            if (currentDoor in door_list): continue

            if (currentDoor == self.agent): continue

            door_position = []

            # if currentDoor not in door:
            #     newExplored.add(self.doors[currentDoor])

            self.findRoom(agent_pos=currentDoor, explored_nodes=explored_current, doors=door_position, isFirstNode=True,
                          isOpen=[False])
            door_list[currentDoor] = door_position
            for d in door_position:
                frontier.append([d, copy.deepcopy(explored_current)])
                if (d in self.doors):
                    frontier.append([self.doors[d], copy.deepcopy(explored_current)])
                    
        self.backtrackPrunningImpossibleBranches(door_list, newExplored)
        return door_list

    def backtrackPrunningImpossibleBranches(self, path):
        frontier = []
        frontier.append(self.goal)
        
        explored = set()
        isInFrontier = set()
        needed = set()
        
        while (frontier):
            is_open = False
            node = frontier.pop(0)
            
            if (node in explored): continue
            explored.add(node)
            
            for p,q in path[node]:
                if(self.agent == p):
                    
                    is_open = True
                    
            if is_open == True:
                continue
            for p,q in path[node]:
                if(tuple(p) in self.doors):
                    if(self.doors[p] == []): 
                        continue
                    if(p not in needed):
                        needed.add(p)                    
                        frontier.append(p)
                        

                    if (self.doors[p] not in needed):
                        needed.add(self.doors[p])
                        frontier.append(self.doors[p])
                        
        needed.add(self.agent)
        needed.add(self.goal)
        
        return needed
            

    # def generatePath(self, door_list, coordinates, isFirst, found):

    #     path_list = []
    #     path = []
    #     for coordinate in coordinates:

    #         if(coordinate in self.doors or (coordinate == self.goal and isFirst[0] == True)):
    #             isFirst[0] = False
    #             if(coordinate == self.goal):
    #                 path = self.findOrderOfDoors(coordinate, door_list)
    #             else:
    #                 path = self.findOrderOfDoors(self.doors[coordinate], door_list)

    #             if(not path_list):
    #                 path_list = path
    #                 continue
    #             for p in path:
    #                 for previousPath in path_list:
    #                     previousPath.extend(p)

    #     if path_list:
    #         ret = []
    #         for partialPath in path_list:
    #             # if self.agent in partialPath:
    #             #     partialPath.remove(self.agent)
    #             furtherPaths = self.generatePath(door_list, partialPath, isFirst, found)
    #             if (furtherPaths):
    #                 for f in furtherPaths:
    #                     temp = copy.deepcopy(partialPath)
    #                     temp.extend(f)
    #                     ret.append(temp)
    #             else:
    #                 ret.append(partialPath)
    #         return ret    
    #     return path_list

    def generatePath(self, door_list, coordinate):
        if (coordinate == self.agent):
            return [[]]

        else:
            result = []
            for door in door_list[tuple(coordinate)]:
                furtherDoors = self.generatePath(door_list, door)
                for furtherDoor in furtherDoors:
                    temp = [door]
                    temp.extend(furtherDoor)
                    result.append(temp)
            return result

    def setKey(self, door_list, door_path, door_with_keys, startingPoint, completeList):
        isStart = False
        if (startingPoint == len(door_path) - 1):
            completeList.append(door_with_keys)
            return
        for i in range(0, len(door_with_keys)):
            if (tuple(door_with_keys[i]) not in door_list):
                continue

            if (door_with_keys[i] == door_path[startingPoint]):
                isStart = True

            if (isStart == True):
                for j in range(i + 1, len(door_with_keys)):
                    if (door_with_keys[j - 1] in door_list[self.doors[door_path[startingPoint]]]):
                        return
                    else:
                        temp = copy.deepcopy(door_with_keys)
                        temp.insert(j, door_list[self.doors[door_path[startingPoint]]])
                        self.setKey(door_list, door_path, temp, startingPoint + 1, completeList)

    def findOrderOfDoors(self, coordinate, door_list):
        path = []

        if (coordinate == self.agent):
            return [[]]

        for i in door_list[coordinate]:
            partialRoutes = self.findOrderOfDoors(i, door_list)
            for route in partialRoutes:
                temp = [coordinate]
                temp.extend(route)
                path.append(temp)
        return path

    def get_neighbors(self, node):
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        neighbors = []

        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(self.gameMap) and 0 <= y < len(self.gameMap[0]) and self.gameMap[x][y] != '-1':
                neighbors.append((x, y))
        for dx, dy in diagonal_directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(self.gameMap) and 0 <= y < len(self.gameMap[0]) and self.gameMap[x][y] != '-1':
                if self.gameMap[x][node[1]] != '-1' and self.gameMap[node[0]][y] != '-1':
                    neighbors.append((x, y))
        return neighbors

    def heuristic(self, position, target):
        dx = abs(position[0] - target[0])
        dy = abs(position[1] - target[1])
        return dx + dy + (math.sqrt(2) - 2) * min(dx, dy)

    def Astar(self, path_list, needed):
        frontier = PriorityQueue()
        frontier.put((self.heuristic(self.agent, self.goal), ([self.agent], 0)))
        i = 0
        pygame.time.wait(1000)
        while (frontier.not_empty):
            try:
                cur_cost, (cur_node, cost) = frontier.get_nowait()
            except:
                return (False, False)
            # i += 1
            # print("i", i)

            if (cur_node[-1] == self.goal):
                return cur_node

            if (tuple(cur_node[-1]) == self.agent and len(cur_node) > 1):
                continue

            adjacentNodes = path_list[tuple(cur_node[-1])]
            Visualizer.visual_map[cur_node[-1][0]][cur_node[-1][1]].make_visited_key_door()

            for node in adjacentNodes:
                
               
                if (tuple(node[0]) in self.doors.keys() and self.doors[tuple(node[0])] not in cur_node):
                    continue

                if (tuple(node[0]) in list(self.keys.values()) and tuple(node[0]) in cur_node):
                    continue
                
                temp = copy.deepcopy(cur_node)
                temp.append(node[0])
                frontier.put(((cost + node[1] + self.heuristic(node[0], self.goal)), (temp, cost + node[1])))
            draw(WIN, Visualizer.visual_map, Visualizer.rows, Visualizer.columns, WIDTH, Visualizer.grid_start_x,
                Visualizer.grid_start_y)
            pygame.display.update()
        return None

    def GBFS(self, path_list):
        frontier = PriorityQueue()

        frontier.put((self.heuristic(self.agent, self.goal), ([self.agent], 0)))
        i = 0

        while (frontier.not_empty):
            try:
                cur_cost, (cur_node, cost) = frontier.get_nowait()
            except:
                return (False, False)
            # i += 1
            # print("i", i)

            if (cur_node[-1] == self.goal):
                return cur_node

            if (tuple(cur_node[-1]) == self.agent and len(cur_node) > 1):
                continue

            adjacentNodes = path_list[tuple(cur_node[-1])]

            for node in adjacentNodes:

                if (tuple(node[0]) in self.doors.keys() and self.doors[tuple(node[0])] not in cur_node):
                    continue

                if (tuple(node[0]) in list(self.keys.values()) and tuple(node[0]) in cur_node):
                    continue

                temp = copy.deepcopy(cur_node)
                temp.append(node[0])
                frontier.put(((cost + node[1] + self.heuristic(node[0], self.goal) * 100), (temp, cost + node[1])))

        return None

    def UCS(self, path_list):
        frontier = PriorityQueue()

        frontier.put((0, [self.agent]))
        i = 0

        while (frontier.not_empty):
            try:
                cost, cur_node = frontier.get_nowait()
            except:
                return (False, False)
            # i += 1
            # print("i", i)

            if (cur_node[-1] == self.goal):
                return cur_node

            if (tuple(cur_node[-1]) == self.agent and len(cur_node) > 1):
                continue

            adjacentNodes = path_list[tuple(cur_node[-1])]

            for node in adjacentNodes:

                if (tuple(node[0]) in self.doors.keys() and self.doors[tuple(node[0])] not in cur_node):
                    continue

                if (tuple(node[0]) in list(self.keys.values()) and tuple(node[0]) in cur_node):
                    continue

                temp = copy.deepcopy(cur_node)
                temp.append(node[0])
                frontier.put(((cost + node[1]), temp))
        return None

    def algorithm(self):
        isSolvable = self.findGoalandKeys()
        if (isSolvable == False):
            print("unSolvable")
            return None
        # list = self.exploreDoor(door_list=door_position_list, door=[self.goal])
        # print(list)
        
        path, mem = self.findDoor_ver2(self.agent)

        # routine = {}
        # path, subroutine = self.findDoor(self.goal)
        # if (path == False and subroutine == False):
        #     return None
        # path_graph[self.goal] = path
        # routine.update(subroutine)
        # remainGraph = [path]

        # while (remainGraph):
        #     currentNode = remainGraph.pop(0)
        #     for x in currentNode:
        #         if (tuple(x[0]) in path_graph.keys()):
        #             continue
        #         temp, subroutine = self.findDoor(x[0])
        #         if (temp == False and subroutine == False):
        #             return None
        #         path_graph[x[0]] = temp
        #         remainGraph.append(temp)
        #         routine.update(subroutine)

        # if (not path_graph[self.goal]):
        #     print("UnSolvable")
        #     return None
        # print(path_graph)
        # needed = self.backtrackPrunningImpossibleBranches(path_graph)
        # # print(needed)
        # # for key, value_list in path_graph.items():
        # #     path_graph[key] = [item for item in value_list if tuple(item[0]) in needed]
            
        # # print(path_graph)
                    
        # shortestPath = self.Astar(path_graph, needed)
        
        # finalRoutine = self.getRoutine(routine, shortestPath)
        # if (not finalRoutine):
        #     print("UnSolvable")
        #     return None
        # print(finalRoutine)
        # # Print final routine to the screen
        # for explore in explored:
        #     Visualizer.visual_map[explore[0]][explore[1]].make_visited_key_door()
        #     draw(WIN, Visualizer.visual_map, Visualizer.rows, Visualizer.columns, WIDTH, Visualizer.grid_start_x,
        #          Visualizer.grid_start_y)
        #     pygame.display.update()
        if path:
            path.reverse()
            Visualizer.print_path(path)
        return path
        # return finalRoutine

    def getRoutine(self, routine, path):
        shortestRoutine = []
        for p in range(0, len(path) - 1):
            partialRoutine = self.getRoutineBetweenTwoNodes(routine, path[p], path[p + 1])
            shortestRoutine.extend(partialRoutine)
            shortestRoutine.pop()
        return shortestRoutine

    def getRoutineBetweenTwoNodes(self, routine, node, root):
        shortesRoutine = []
        shortesRoutine.append(node)
        if (node == root):
            return [root]
        shortesRoutine.extend(self.getRoutineBetweenTwoNodes(routine, routine[(node, root)], root))
        return shortesRoutine

        # path = self.generatePath(list, self.goal)
        # # print(path)
        # cpList = []
        # self.setKey(list, path[0], path[0], 0, cpList)
        # print(cpList)

        # self.decisionTree.append([self.goal, door_position])
        # # print(door_positions_list[-1][1])
        # # print(self.keys)
        # frontier = []
        # frontier.extend(x for x in door_position.values())
        # #print(frontier)
        # while(frontier):
        #     node = frontier.pop(0)
        #     door_position = {}
        #     self.findRoom(agent_pos=node, explored_nodes=[], doors_position=door_position, isOpen=[False])
        #     self.decisionTree.append([node, door_position])
        #     frontier.extend(x for x in door_position.values() if x not in frontier)

        # print(self.decisionTree)   


# 40x44   (10 keys/ 10 doors)
grid_example1 = [
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 1
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 2
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 3
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 4
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 5
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 6
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 7
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 8
    ["0", "0", "0", "A1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 9
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 10
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 11
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 12
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1", "-1", "D2",
     "D2", "-1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 13
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "D1", "0", "0", "0", "0",
     "0", "-1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 14
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "D1", "0", "K3", "0",
     "0", "0", "-1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1", "-1", "-1", "0", "0", "0", "0", "0", "0"],
    # 15
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1", "-1", "0",
     "0", "0", "-1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1", "0", "0", "-1", "0", "0", "0", "0", "0"],
    # 16
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1",
     "-1", "-1", "-1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "D4", "0", "K2", "-1", "0", "0", "0", "0",
     "0"],
    # 17
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-1", "-1", "-1", "0", "0", "0", "0", "0"],
    # 18
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 19
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "K4", "0", "0", "0", "0", "0", "0", "0", "-1", "D3", "-1", "-1", "D2", "-1", "-1", "0", "0", "0", "0", "0", "0"],
    # 20
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "-1", "-1", "-1", "0", "0", "0", "0", "0", "0", "-1", "0", "0", "0", "0", "0", "0"],
    # 21
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "-1", "0", "K1", "0", "0", "0", "0", "0", "0", "0", "-1", "0", "0", "0", "0", "0", "0"],
    # 22
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "-1", "0", "-1", "-1", "-1", "D1", "D2", "D1", "-1", "0", "-1", "0", "0", "0", "0", "0", "0", "0"],
    # 23
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "-1", "0", "1", "0", "0", "0", "-1", "-1", "0", "-1", "0", "-1", "0", "0", "0", "0", "0", "0"],
    # 24
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "-1", "0", "-1", "0", "0", "0", "T1", "0", "-1", "0", "0", "-1", "0", "0", "0", "0", "0", "0"],
    # 25
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "-1", "0", "0", "-1", "-1", "-1", "0", "-1", "0", "0", "-1", "0", "0", "0", "0", "0", "0", "0"],
    # 26
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "-1", "0", "0", "0", "0", "0", "-1", "0", "-1", "-1", "-1", "0", "0", "0", "0", "0", "0", "0"],
    # 27
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "-1", "-1", "-1", "-1", "D4", "D4", "D4", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 28
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 29
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 30
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 31
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 32
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 33
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 34
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 35
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 36
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 37
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 38
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    # 39
    ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
     "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    # 40
]


def convertFileToGrid(filename):
    if not os.path.isfile(filename):
        print('File does not exist.')
        return None
    else:
        # Open the file and read its content.
        with open(filename) as f:
            content = f.read().splitlines()

        # Display the file's content line by line.
        temp = ""
        gameMap = []
        counter = 0
        for line in content:
            if (counter <= 1):
                counter += 1
                continue
            row = []
            temp = ""
            for i in range(len(line)):
                if (line[i] == ','):
                    row.append(temp)
                    temp = ""
                    continue
                temp += line[i]
                if (i == len(line) - 1):
                    row.append(temp)
            gameMap.append(row)
        return gameMap


def main():
    gameMap = convertFileToGrid("./level2/input.txt")
    # print(gameMap)
    test = game(gameMap=gameMap)

    start = timeit.default_timer()

    print(len(test.algorithm()))

    stop = timeit.default_timer()

    print('Time: ', stop - start)

def level2(url):
    gameMap = convertFileToGrid(url)
    Visualizer.rows = len(gameMap)
    Visualizer.columns = len(gameMap[0])

    # Calculate the total grid size
    total_grid_width = Visualizer.columns * WIDTH
    total_grid_height = Visualizer.rows * WIDTH

    # Calculate the starting position to center the grid
    Visualizer.grid_start_x = (WIDTH * Visualizer.columns - total_grid_width) // 2
    Visualizer.grid_start_y = (WIDTH * Visualizer.rows - total_grid_height) // 2

    visual_map = Visualizer.print_visual_grid(gameMap)
    Visualizer.visual_map = visual_map

    draw(WIN, visual_map, Visualizer.rows, Visualizer.columns, WIDTH, Visualizer.grid_start_x, Visualizer.grid_start_y)

    pygame.display.update()
    # Initialize the pygame module
    run = True
    playagain = False
    command = -1
    while run:
        # redraw the screen when play again
        if playagain:
            playagain = False
            Visualizer.visual_map = Visualizer.print_visual_grid(gameMap)
        command = draw_menu_level2(Visualizer.visited)
        print_score(Visualizer.visited)
        draw(WIN, visual_map, Visualizer.rows, Visualizer.columns, WIDTH, Visualizer.grid_start_x,
             Visualizer.grid_start_y)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            if pygame.MOUSEBUTTONDOWN:
                if command == 1:
                    Visualizer.visited = 0
                    test = game(gameMap=gameMap)
                    start = timeit.default_timer()
                    result = test.algorithm()
                    stop = timeit.default_timer()
                    print('Time: ', stop - start)

                    if result:
                        print(len(result))
                    else:
                        print(result)
                        print("unsolvable")
                        Visualizer.visited = None
                    draw_menu_level2(Visualizer.visited)
                    playagain = True
                elif command == 0:
                    run = False
                    return
        pygame.time.delay(100)
        pygame.display.flip()

# Astar
# [(8, 3), (9, 4), (10, 5), (11, 6), (12, 7), (13, 8), (14, 9), (15, 10), (16, 11), (17, 12), (18, 13), (19, 14), (19, 15), (19, 16), (19, 17), (19, 18), (19, 19), (19, 20), (19, 21), (19, 22), (19, 23), (20, 24), (21, 25), (22, 25), (23, 25), (24, 25), (25, 25), (26, 25), (27, 25), (28, 26), (28, 27), (28, 28), (28, 29), (28, 30), (28, 31), (27, 31), (26, 31), (26, 30), (26, 29), (26, 28), (25, 27), (24, 27), (23, 27), (23, 28), (23, 29), (24, 30), (24, 31)]#
