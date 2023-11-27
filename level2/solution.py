import psutil
from queue import PriorityQueue
from queue import Queue
import math
import copy


class agent:
    def __init__(self, position = [], path = [], cost = 0):
        self.keys = []
        self.position = position
        self.path = path
        self.cost = cost
        
class game:
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
                    self.goal = (i,j) #merge with "D" later
                elif("K" in self.gameMap[i][j]):
                    self.keys[self.gameMap[i][j]] = (i,j)
                elif("D" in self.gameMap[i][j]):
                    self.doors[self.gameMap[i][j]] = (i,j)
                elif("A" in self.gameMap[i][j]):
                    self.agent = agent([i,j])
        
    def findRoom(self, agent_pos, explored_nodes, doors, isFirstNode, isOpen):
        
        if(agent_pos[0] < 0 or agent_pos[0] >= len(self.gameMap) or agent_pos[1] < 0 or agent_pos[1] > len(self.gameMap[0])):
            return
        
                
        if(agent_pos in explored_nodes and isFirstNode == False):
            return 
        else: explored_nodes.add(agent_pos)
        
        if(self.gameMap[agent_pos[0]][agent_pos[1]] == "-1"):
            return 
        
        if("D" in self.gameMap[agent_pos[0]][agent_pos[1]] and isFirstNode == False):
            doors.append(agent_pos)
            return
        
        if(self.isRoom(agent_pos=agent_pos) == False):
            isOpen[0] = True
            doors.clear()
            return
                
        self.findRoom((agent_pos[0] - 1, agent_pos[1]), explored_nodes, doors, False, isOpen)  
        if(isOpen[0] == True):
            return None    
            
        self.findRoom((agent_pos[0] + 1, agent_pos[1]), explored_nodes, doors, False, isOpen)
        if(isOpen[0] == True):
            return None   
        
        self.findRoom((agent_pos[0], agent_pos[1] - 1), explored_nodes, doors, False, isOpen)
        if(isOpen[0] == True):
            return None   
        
        self.findRoom((agent_pos[0], agent_pos[1] + 1), explored_nodes, doors, False, isOpen)
        if(isOpen[0] == True):
            return None   
        
    def isRoom(self, agent_pos): 
        if ((self.gameMap[agent_pos[0]][agent_pos[1]] == "0" or "A" in self.gameMap[agent_pos[0]][agent_pos[1]]) and (agent_pos[0] == 0 or agent_pos[0] == len(self.gameMap) - 1 or agent_pos[1] == 0 or agent_pos[1] == len(self.gameMap[0]) - 1)):
            return False
        if ("A" in self.gameMap[agent_pos[0]][agent_pos[1]]):
            return False
        else: return True
        
    def exploreDoor(self, door, foundDoors, explored):
        door_list = []
        
        door_position = []
        
        self.findRoom(agent_pos=door, explored_nodes=explored, doors=door_position, isFirstNode=True, isOpen=[False])
        
        if(not door_position):
            return [door]
        
        for i in door_position:
            if(i in foundDoors): continue
            else: foundDoors.add(i)
            
            explored_cur = copy.deepcopy(explored)
            
            exploredDoor = self.exploreDoor(i, foundDoors, explored_cur)
            
            for x in exploredDoor:
                door_list.append([door, x])
                
        return door_list
        
     
    def algorithm(self):
        self.findGoalandKeys()
        
        door_position = []
        door_position_list = []
        
        list = self.exploreDoor(self.goal, foundDoors=set(), explored=set())
        
        print(list)
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
    ["0", "-1", "-1", "D3", "-1"],
    ["K3", "-1", "0", "0", "-1"],
    ["0", "-1", "T1", "-1", "-1"],
    ["0", "-1", "0", "-1", "0"],
    ["0", "-1", "D2", "-1", "0"],
    ["0", "0", "D4", "-1", "0"],
    ["-1", "0", "D5", "-1", "0"],
    ["-1", "-1", "0", "-1", "0"],
    ["0", "0", "0", "-1", "0"],
    ["0", "0", "-1", "-1", "0"],
    ["0", "-1", "0", "K2", "-1"],
    ["0", "0", "0", "D4", "-1"]
]      

test = game(gameMap=grid_example)
test.algorithm()
        
    