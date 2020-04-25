import yaml
import enum
import os
import os.path
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
    
    def __init__(self,filePath=None):
        #Loading Positions
        self.positionPath = os.path.join(os.path.dirname(__file__),"../position_store/positions.yaml")
        if filePath != None:
            self.positionPath = filePath
        fileData = self.loadFile()
        if fileData:
            self.positions = fileData['positions'] if fileData['positions'] else []
            self.idFactory = fileData['idFactory'] if fileData['idFactory'] else {'lastId':0,
                              'issuedIdCount':0}
            self.saveFile(self.getFileTemplate(self.positions,self.idFactory))
            print(self.loadFile())
        else :
            self.positions =  []
            self.idFactory =  {'lastId':0,
                              'issuedIdCount':0}
            self.saveFile(self.getFileTemplate(self.positions,self.idFactory))
            print(self.loadFile())
            
    def loadFile(self):
        if os.path.isfile(self.positionPath):
            with open(self.positionPath,'r') as stream:
                fileData = yaml.load(stream, Loader=yaml.SafeLoader)
                return fileData
            
    def saveFile(self,fileTemplate):
        with open(self.positionPath,'w') as stream:
            yaml.dump(fileTemplate,stream)
            
    def getFileTemplate(self,positions,idFactory=None):
        template = {'positions':positions,
                    'idFactory':(idFactory if idFactory != None else self.idFactory)}
        return template
    def getNewId(self):
        return self.idFactory['lastId']+1
    def commitId(self,latestID):
        self.idFactory['lastId'] = latestID
        self.idFactory['issuedIdCount'] = self.idFactory['issuedIdCount']+1
        self.saveFile(self.getFileTemplate(self.getAllPositions(),self.idFactory))
        
    def getAllPositions(self):
        fileData = self.loadFile()
        if fileData == None:
            return []
        if fileData['positions'] != None:
            self.positions = fileData['positions']
            return self.positions
        else:
            return []
    def getPostion(self,name):
        for pos in self.getAllPositions():
            if pos['name'] == name:
                return Position(name,pos['position'],pos['description'],pos['space'])
        return None
    def getPostionById(self,i):
        for pos in self.getAllPositions():
            cId = pos.get('id',None)
            if cId == i:
                    name = pos.get('name','')
                    position = pos.get('position',[])
                    des = pos.get('description','')
                    space = pos.get('space','joint')
                    return Position(name,position,des,space)
        return None
    def updateList(self,newList):
        self.saveFile(self.getFileTemplate(newList))
        
    def save(self,name,position,description,space):
        newId = self.getNewId()
        tempPos = {'id':newId,
                   'name':name,
                   'position':position,
                   'description':description,
                   'space':space
                   }
        if os.path.isfile(self.positionPath):
            self.positions = self.getAllPositions()
            if self.positions:
                for pos in self.positions:
                    if pos['name'] == name:
                        print("Name is already existed, try other name!")
                        return -1
                self.positions.append(tempPos)
                self.updateList(self.positions)
                self.commitId(newId)
                print(tempPos," is saved!")
                return 1
   
       #In the case where there no file found create new file and save that postion
        self.updateList([tempPos])
        self.commitId(newId)
        print(tempPos," is saved!")
        return 1
    def delete(self,name):
        if os.path.isfile(self.positionPath):
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
            