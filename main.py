from dorna import Dorna
from copy import deepcopy
import enum
import json
import time

#robot = Dorna("/home/pi/Desktop/config.yaml")
"""=======================
    DEFINE CONST
    ======================
"""
COORDINATE = ["x","y","z","a","b"]
JOINTS     = ["j0","j1","j2","j3","j4"]
PRM_TEMPLATE ={'path':'joint','movement':1}

"""=======================
    DEFINE POSITIONS HERE
    ======================
"""
FLAT={'path':'joint','movement':0,'j0':0,'j1':0,'j2':0,'j3':0,'j4':0}
HOME={'path':'joint','movement':0,'j0':0,'j1':145,'j2':-90,'j3':-45,'j4':0}
ZERO={'path':'joint','movement':1,'j0':0,'j1':0,'j2':0,'j3':0,'j4':0}

""" ===========================================================
===============================================================
***** Class Approach ****************************************
===============================================================
    ===========================================================
"""

class Direction(enum.Enum):
    FORWARD = 'x'
    BACKWARD = '-x'
    RIGHT = 'y'
    LEFT = '-y'
    UP = 'z'
    DOWN = '-z'
class Arm(object):
    def __init__(self):
        self.robot =  Dorna("./config.yaml")
        
    def go(self,position=HOME):
        print("Go to ",position)
        tmpcmd={"command":"move", "prm":position}
        self.robot.play(tmpcmd)
        
    """============================================================
        CONNECTION AND HOMING THE ROBOT
        ===========================================================
    """
    def connect(self):
        return self.robot.connect()
    def dis(self):
        return self.robot.disconnect()
    def connectAndHomeIfneed(self):
        
        self.robot.connect()
        self.homeIfneed()
        
    def connectAndHomes(self):
        
        self.robot.connect()
        self.robot.home("j0")
        self.robot.home("j1")
        self.robot.home("j2")
        self.robot.home("j3")
    def isConnected(self):
        device = json.loads(r.robot.device())
        if device['connection'] == 2:
            return True
        else:
            return False
    def isHomed(self):
        if not self.isConnected():
            print("Robot is not connected")
            return False
            
        homed = json.loads(self.robot.homed())
        for key in homed:
            if homed[key] == 1:
                print(key," is homed")
            else:
                print(key," is not homed yet")
    def homes(self):
        self.robot.home("j0")
        self.robot.home("j1")
        self.robot.home("j2")
        self.robot.home("j3")  
        
    def homeIfneed(self):
        if not self.isConnected():
            print("Robot is not connected")
            return False
        homed = json.loads(self.robot.homed())
        for key in homed:
            if homed[key] == 1:
                print(key," is homed")
            else:
                print("Homing ",key)
                self.robot.home(key);
    """===================================================================
    GET CURRENT POSITION AS XYZ SYSTEM
    ==================================================================
    """  
    def posXYZ(self):
        return json.loads(self.robot.position('xyz'))

    """===================================================================
        GET CURRENT POSITION AS JOINTS SYSTEM
        ==================================================================
    """  
    def pos(self):
        return json.loads(self.robot.position())
    """==============================================
    ADJUST the joints
    =================================================
    """
    #pass in joint and value as parameter ex:adjust("j0",10)
    def adjust(self,joint, degrees:float,relatively=True):
        # creates a position-movement description that can be fed to go(). 
        tempPath=deepcopy(PRM_TEMPLATE)
        for j in JOINTS:
            if j == joint:
                
                tempPath[j]=degrees
                break
        tempPath["movement"]= 1 if relatively else 0
        self.go(tempPath)
        return tempPath  

    #pass in joints object as parameter ex:adjust({"j1":0,"j2":0})
    def adjustJoints(self,joints,relatively=True):
        # creates a position-movement description that can be fed to go().
        tempPath=deepcopy(PRM_TEMPLATE)
        print(joints)
        for key in joints:
            for validJoint in JOINTS:
                if key == validJoint:
                    tempPath[validJoint]=joints[key]
                
        tempPath["movement"]= 1 if relatively else 0
        self.go(tempPath)
        return tempPath

        
    """==================================================
        MOVE with x,y,z Coordinate System
        =================================================
    """
    #pass in axis and value as parameter
    #ex:moveToPosition('z',10)
    def adjustAxis(self,axis, degrees,relatively=True):
        tempPath=deepcopy(PRM_TEMPLATE)
        tempPath['path'] = 'line'
        
        for c in COORDINATE:
            if c == axis:
                tempPath[c]=degrees
                break
        tempPath["movement"]= 1 if relatively else 0
        self.go(tempPath)
        return tempPath
    
    """==================================================
        MOVE with xyz Coordinate System
        =================================================
    """
    #pass in coordinate object as parameter
    #ex:moveToCoordinate({'x':10,'y':20,'z':10})
    def adjustCoordinate(self,coor,relatively=True):
        tempPath=deepcopy(PRM_TEMPLATE)
        tempPath['path'] = 'line'
        
        for key in coor:
            for validJoint in COORDINATE:
                if key == validJoint:
                    tempPath[validJoint]=coor[key]
        tempPath["movement"]= 1 if relatively else 0            
        self.go(tempPath)
        return tempPath
    """==================================================
        wait 
        =================================================
    """
    def wait(self,value):
        time.sleep(value)
    def goHome(self):
        self.go(HOME)
    def goFlat(self):
        self.go(FLAT)
    """==================================================
        MOVE tools head relatively to current angle
        =================================================
    """
    def adjustHead(self,angle):
        self.adjust('j3',angle)
        return self.pos()[3]
    """==================================================
        MOVE tools head to specific Angle
        =================================================
    """
    def setHeadAngle(self,angle):
        self.adjust('j3',angle,False)
        return self.pos()[3]
    """==================================================
        MOVE with specific directin
        =================================================
    """   
    def move(self,direct:Direction.FORWARD,value:float):
        if direct == Direction.FORWARD:
            self.adjustAxis('x',value)
        if direct == Direction.BACKWARD:
            moveAxis('x',value * -1)
        if direct == Direction.UP:
            self.adjustAxis('z',value)
        if direct == Direction.DOWN:
            self.adjustAxis('z',value * -1)
        if direct == Direction.LEFT:
            self.adjustAxis('y',value)
        if direct == Direction.RIGHT:
            self.adjustAxis('y',value * -1)
            
    """==================================================
        MOVE move to a coordiation
        ex:moveTo((1,2,6)) x=1,y=2,z6
        =================================================
    """ 
    def moveTo(self,xyz):
        self.adjustCoordinate({'x':xyz[0],
                               'y':xyz[1],
                               'z':xyz[2]},False)

    """==================================================
        Collection of Motion
    """
    def pickIt(self):
        self.adjustJoints({'j1':45,'j2':-90,'j3':45,'j4':0},False)
        self.adjustCoordinate({'x':15,'y':0,'z':3.5},False)
        self.wait(10)
        self.adjustCoordinate({'x':16,'y':0,'z':10},False)
        self.adjust('j0',180)
        self.adjustCoordinate({'x':4,'y':0,'z':-5})
        self.adjustCoordinate({'x':0,'y':0,'z':-3})
        self.wait(10)
        self.adjustCoordinate({'x':-5,'y':0,'z':8})
        self.adjust('j0',-180)
        self.adjustCoordinate({'x':15,'y':0,'z':3.5},False)
        self.wait(10)
        self.go()
        
        
    def preHit(self):
        self.adjustJoints({'j0':0,'j1':45,'j2':-123,'j3':78,'j4':0},False)
        self.adjustCoordinate({'x':-10,'y':0,'z':0})
        self.adjustCoordinate({'x':60,'y':0,'z':0})
    def hit(self):
        self.adjustCoordinate({'x':1,'y':0,'z':0})
        for i in [0,1,2,3,4]:
            self.adjustCoordinate({'x':-60,'y':0,'z':0})
            self.adjustCoordinate({'x':60,'y':0,'z':0})
            self.wait(10)
            self.adjustCoordinate({'x':-10,'y':0,'z':0})

        self.adjustCoordinate({'x':-10,'y':0,'z':0})
    def preHitTop(self):
        self.adjustJoints({'j0':0,'j1':45,'j2':-123,'j3':78,'j4':0},False)
        self.adjustCoordinate({'x':0,'y':0,'z':80})
        self.adjustCoordinate({'x':80,'y':0,'z':0,'a':-90})
        self.adjustCoordinate({'x':0,'y':0,'z':14})
    def hitTop(self):
        self.adjustCoordinate({'x':0,'y':0,'z':-1})
        for i in [0,1,2,3,4]:
            self.adjustCoordinate({'x':0,'y':0,'z':20})
            self.adjustCoordinate({'x':0,'y':0,'z':-20})
            self.wait(6);
        
    def prRight(self):
        self.adjustJoints({'j0':0,'j1':45,'j2':-123,'j3':78,'j4':0},False)
        
    def hitRight(self):
        self.adjustCoordinate({'x':0,'y':1,'z':0})
        for i in [0,1,2,3,4]:
            self.adjustCoordinate({'x':0,'y':-20,'z':0})
            self.adjustCoordinate({'x':0,'y':20,'z':0})
            self.wait(6);   
           
        
        
        
        
        
        
    