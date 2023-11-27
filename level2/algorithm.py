import psutil
from queue import PriorityQueue
from queue import Queue
import math

class agent:
    def __init__(self, position = [], path = [], cost = 0):
        self.keys = []
        self.position = position
        self.path = path
        self.cost = cost

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    # Return a default value (e.g., None) if the value is not found
    return None
       
class algo_lv2:
    def __init__(self, path = [], gameMap = [[]]):
        self.path = path 
        self.gameMap = gameMap
        self.decisionTree = []
        self.keys = {}
        self.doors = {}
        self.goal = ()
        self.agent = None
        
    def findGoalandKeys(self):
        for i in range (len(self.gameMap)):
            for j in range (len(self.gameMap[0])):
                if(self.gameMap[i][j] == "T1"):
                    self.doors[self.gameMap[i][j]] = (i,j) #merge with "D" later
                elif("K" in self.gameMap[i][j]):
                    self.keys[self.gameMap[i][j]] = (i,j)
                elif("D" in self.gameMap[i][j]):
                    self.doors[self.gameMap[i][j]] = (i,j)
                elif("A" in self.gameMap[i][j]):
                    self.agent = agent([i,j])
        
        
    def findRoom(self, agent_pos, explored_nodes, doors_position, isOpen, current):
        if (agent_pos in explored_nodes):
            return
        
        explored_nodes.add(agent_pos) #switch to set() later
        
        if(self.gameMap[agent_pos[0]][agent_pos[1]] == "-1"):
            return
        
        isRoom = self.checkingRoom(self.gameMap, agent_pos, current)
        
        if (isRoom == False):
            isOpen[0] = True
            doors_position.clear()
            return
        elif(isRoom == True):  
            
            self.findRoom((agent_pos[0] - 1, agent_pos[1]), explored_nodes, doors_position, isOpen, current)
            if(isOpen[0] == True):
                return None     
                
            self.findRoom((agent_pos[0] + 1, agent_pos[1]), explored_nodes, doors_position, isOpen, current)
            if(isOpen[0] == True):
                return None  
            
            self.findRoom((agent_pos[0], agent_pos[1] - 1), explored_nodes, doors_position, isOpen, current)
            if(isOpen[0] == True):
                return None  
            
            self.findRoom((agent_pos[0], agent_pos[1] + 1), explored_nodes, doors_position, isOpen, current)
            if(isOpen[0] == True):
                return None 
            
        else:
            doors_position.append(isRoom)
        
    def checkingRoom(self, gameMap, agent_position, current):
        if(agent_position[0] == 0 or agent_position[0] == len(gameMap) - 1 or agent_position[1] == 0 or agent_position[1] == len(gameMap[0]) - 1):
            return False
        if(current[0] == True):
            current[0] = False
            return True
        
        if("D" in gameMap[agent_position[0]][agent_position[1]]):
            return gameMap[agent_position[0]][agent_position[1]]
        if("A" in gameMap[agent_position[0]][agent_position[1]]):
            return False  
        return True    
        
    def getNeighbors(self, agent):
        neighbors = []
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        
        for dx, dy in directions:
            x, y = agent.position[0] + dx, agent.position[1] + dy
            if 0 <= x < len(self.gameMap) and 0 <= y < len(self.gameMap[0]) and self.gameMap[x][y] != '-1':
                neighbors.append((x,y))
        for dx, dy in diagonal_directions:
            x, y = agent.position[0] + dx, agent.position[1] + dy
            if 0 <= x < len(self.gameMap) and 0 <= y < len(self.gameMap[0]) and self.gameMap[x][y] != '-1':
                if self.gameMap[x][agent.position[1]] != '-1' and self.gameMap[agent.position[0]][y] != '-1':
                    neighbors.append((x, y))
        return neighbors      
    
    def calculateDistence(position1, position2):
        return math.sqrt((position2[0] - position1[0])**2 + (position2[1] - position1[1])**2)
    
    def heuristicCalculation(self, agent, expanding):
        distance = []
        for node in expanding:
            distance.append(self.calculateDistence(agent, node))
        return min(distance)

        
    def astar(self, decisionTree):
        frontier = PriorityQueue()
        explored = set()
        parent = {}
        expanding = []
        order = {}
        
        expanding.extend(x[0] for x in self.decisionTree if not x[1])
        
        frontier.put((0, self.agent.position))
        while not frontier.empty():
            
            agent = frontier.get_nowait()
            
            if(agent == self.goal): 
                break
            
            if (agent in explored):
                continue
            explored.add(agent)
            
            if (agent in expanding):
                # self.agent.keys.append(neighbor)
                expanding.remove(agent)
                if (agent in order):
                    expanding.append(order[agent])
                else:
                    for node in self.decisionTree:
                        newDestination = find_key_by_value(node[1], agent)
                        if (newDestination is not None and newDestination not in expanding and newDestination not in explored):
                            expanding.append(newDestination)
                            order[newDestination] = node[0]
                            
                                            
            neighbors = self.getNeighbors(agent)
            
            for neighbor in neighbors:
                if (neighbor in parent):
                    continue 
                                        
                heuristic = self.heuristicCalculation(neighbor, expanding)
                frontier.put((heuristic, neighbor))
                
    def exploreDoor(self, door, foundDoors):
        door_list = []
        
        door_position = []
        self.findRoom(agent_pos=self.doors[door], explored_nodes=set(), doors_position=door_position, isOpen=[False], current=[True])
        if(door in door_position):
            door_position.remove(door)
        
        
        for i in range (len(door_position)):   
            if (door_position[i] in foundDoors): 
                continue
            else: foundDoors.add(door_position[i])
            print(door)
            exploredDoor = self.exploreDoor(door=door_position[i], foundDoors=foundDoors)
            for x in exploredDoor:
                temp = [door,x]
                door_list.append(temp) 
                
        return door_list   
        
     
    def algorithm(self):
        self.findGoalandKeys()
        
        door_position = []
        door_position_list = []
        
        list = self.exploreDoor("D1", foundDoors=set())
        
        
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
                        
grid_example = [
    ["A1", "-1", "-1", "-1", "0"],
    ["0", "-1", "D3", "D4", "0"],
    ["K3", "-1", "0", "0", "-1"],
    ["0", "-1", "T1", "0", "-1"],
    ["0", "-1", "D1", "-1", "0"],
    ["0", "-1", "0", "-1", "0"],
    ["0", "-1", "D2", "-1", "0"],
    ["-1", "0", "K1", "0", "-1"],
    ["-1", "-1", "-1", "-1", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "0", "-1", "-1", "0"],
    ["0", "-1", "0", "K2", "-1"],
    ["0", "0", "D3", "D4", "-1"]
]      

test = algo_lv2(gameMap=grid_example)
test.algorithm()
        
    