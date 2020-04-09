import yaml
import enum
import os
from tabulate import tabulate

class Direction(enum.Enum):
    FORWARD = 'x'
    BACKWARD = '-x'
    RIGHT = 'y'
    LEFT = '-y'
    UP = 'z'
    DOWN = '-z'
class Position:
    PATH_JOINT = 'joint'
    PATH_LINE = 'line'

    SPACE_JOINT = 'joint'
    SPACE_XYZ = 'xyz'

    def __init__(self,name,position,description,space='joint'):

        """
        CLASS DEFINING A POSE IN JOINT SPACE

        Position is a list of the joint positions in this pose.
        Description is a human-readable description of the pose.
        """

        # TODO add type info (joint or xyz) and any other descriptors.
        self.name = name
        self.space=space # 'joint' space or 'xyz' space 
        self.position=position
        self.description=description
        self.path = self.PATH_JOINT if space == self.SPACE_JOINT else self.PATH_LINE


class PositionStore:
    PATH = "./positions.yaml"
    def __init__(self,filePath=None):
        if filePath != None:
            self.PATH = filePath
        if os.path.isfile(self.PATH):
            with open(self.PATH,'r') as stream:
                self.positions = yaml.load(stream, Loader=yaml.SafeLoader)
                print(self.positions)
    def getAllPositions(self):
        if os.path.isfile(self.PATH):
            with open(self.PATH,'r') as stream:
                self.positions = yaml.load(stream, Loader=yaml.SafeLoader)
                return self.positions
        else:
            return []
    def getPostion(self,name):
        for pos in self.getAllPositions():
            if pos['name'] == name:
                return Position(name,pos['position'],pos['description'],pos['space'])
        return None
    def updateList(self,newList):
        with open(self.PATH,'w') as wstream:
            yaml.dump(newList,wstream)
                    
    def save(self,name,position,description,space):
        tempPos = {'name':name,
                   'position':position,
                   'description':description,
                   'space':space
                   }
        if os.path.isfile(self.PATH):
            with open(self.PATH) as stream:
                self.positions = yaml.load(stream, Loader=yaml.SafeLoader)
                if self.positions != None:
                    for pos in self.positions:
                        if pos['name'] == name:
                            print("Name is already existed, try other name!")
                            return -1
                    self.positions.append(tempPos)
                    self.updateList(self.positions)
                    print(tempPos," is saved!")
                    return 1
       
        with open(self.PATH,'w') as stream:
            yaml.dump([tempPos],stream)
            print(tempPos," is saved!")
            return 1
    def delete(self,name):
        if os.path.isfile(self.PATH):
                for pos in self.getAllPositions():
                    if pos['name'] == name:
                        self.positions.remove(pos)
                        self.updateList(self.positions)
                        print(name," deleted!")
                        return 1
        else:
           print(name," position not found!")
           return -1
    def update(self,name,position=None,description=None,space=None):
        for pos in self.getAllPositions():
            if pos['name'] == name:
                tempPos = pos
                tempPos['position'] = position if position != None else pos['position']
                tempPos['description'] = description if description != None else pos['description']
                tempPos['space'] = space if space != None else pos['space']
                index = self.positions.index(pos)
                self.positions[index] = tempPos
                self.updateList(self.positions)
                print("updated!")
                return 1
        print(name," not found!")
        return -1
    def showAllPositions(self):
        print(tabulate(self.getAllPositions(),
                 headers='keys',tablefmt='fancy_grid'))
            