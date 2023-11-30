import psutil
from queue import PriorityQueue
from queue import Queue
import math
import copy
class agent:
    def __init__(self, position = [], path = [], cost = 0, explored = set()):
        self.keys = []
        self.position = position
        self.path = path
        self.cost = cost
        self.explored = explored
        
class game:
    def __init__(self, path = [], gameMap = [[]]):
        self.path = path 
        self.gameMap = gameMap
        self.decisionTree = []
        self.keys = {}
        self.doors = {}
        self.goal = ()
        self.agent = None
    def findKeys(self):
        for i in range (len(self.gameMap)):
            for j in range (len(self.gameMap[0])):
                if("K" in self.gameMap[i][j]):
                    self.keys[self.gameMap[i][j][1:]] = (i,j)
        
    def findGoalandKeys(self):
        self.findKeys()
        for i in range (len(self.gameMap)):
            for j in range (len(self.gameMap[0])):
                if(self.gameMap[i][j] == "T1"):
                    self.goal = (i,j) #merge with "D" later
                elif("D" in self.gameMap[i][j]):
                    self.doors[(i,j)] = self.keys[self.gameMap[i][j][1:]]
                elif("A" in self.gameMap[i][j]):
                    self.agent = (i,j)
                    
    def findDoors(self, pos):
        frontiers = [pos, 0]
        
        while (frontiers):
            cur_pos = frontiers.pop(0)
            
            if(cur_pos[0] < 0 or cur_pos[0] >= len(self.gameMap) or cur_pos[1] < 0 or cur_pos[1] > len(self.gameMap[0])):
                continue
            
            if (cur_pos == self.agent):
                return {} # No doors
            
            
            
            
            
    