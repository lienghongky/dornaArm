from dorna import Dorna
from copy import deepcopy
import enum
import json

robot = Dorna("/home/pi/Desktop/config.yaml")
"""=======================
    DEFINE CONST
    ======================
"""
COORDINATE = ["x","y","z"]
JOINTS     = ["j0","j1","j2","j3","j4"]
PRM_TEMPLATE ={'path':'joint','movement':1}

"""=======================
    DEFINE POSITIONS HERE
    ======================
"""
FLAT={'path':'joint','movement':0,'j0':0,'j1':0,'j2':0,'j3':0,'j4':0}
HOME={'path':'joint','movement':0,'j0':0,'j1':145,'j2':-90,'j3':-45,'j4':0}
ZERO={'path':'joint','movement':1,'j0':0,'j1':0,'j2':0,'j3':0,'j4':0}


"""============================================================
    CONNECT to ROBOT and HOME the JOINT for J0 to J3 one by one
    ===========================================================
"""
def connectAndHomes():
    
    robot.connect()
    robot.home("j0")
    robot.home("j1")
    robot.home("j2")
    robot.home("j3")
    
"""===================================================================
    GET CURRENT POSITION AS XYZ SYSTEM
    ==================================================================
"""  
def posXYZ():
    return robot.position('xyz')

"""===================================================================
    GET CURRENT POSITION AS JOINTS SYSTEM
    ==================================================================
"""  
def pos():
    return robot.position()

"""===================================================================
    MOVE ROBOT to Certaint position without relate to current position
    ==================================================================
"""  
def go(position=HOME):
    print("Go to ",position)
    tmpcmd={"command":"move", "prm":position}
    robot.play(tmpcmd)

    
    
"""==================================================
    ADJUST the joint relatively to current position
    =================================================
"""
#pass in joint and value as parameter ex:adjust("j0",10)
def adjust(joint, degrees:float,relatively=True):
    # creates a position-movement description that can be fed to go(). 
    tempPath=deepcopy(PRM_TEMPLATE)
    for j in JOINTS:
        if j == joint:
            
            tempPath[j]=degrees
            break
    tempPath["movement"]= 1 if relatively else 0
    go(tempPath)
    return tempPath  

#pass in joints object as parameter ex:adjust({"j1":0,"j2":0})
def adjustJoints(joints,relatively=True):
    # creates a position-movement description that can be fed to go().
    tempPath=deepcopy(PRM_TEMPLATE)
    print(joints)
    for key in joints:
        for validJoint in JOINTS:
            if key == validJoint:
                tempPath[validJoint]=joints[key]
            
    tempPath["movement"]= 1 if relatively else 0
    go(tempPath)
    return tempPath

    
"""==================================================
    MOVE to Coordinate
    =================================================
"""
#pass in axis and value as parameter
#ex:moveToPosition('z',10)
def moveAxis(axis, degrees,relatively=True):
    tempPath=deepcopy(PRM_TEMPLATE)
    tempPath['path'] = 'line'
    
    for c in COORDINATE:
        if c == axis:
            tempPath[c]=degrees
            break
    tempPath["movement"]= 1 if relatively else 0
    go(tempPath)
    return tempPath

#pass in coordinate object as parameter
#ex:moveToCoordinate({'x':10,'y':20,'z':10})
def moveToCoordinate(coor,relatively=True):
    tempPath=deepcopy(PRM_TEMPLATE)
    tempPath['path'] = 'line'
    
    for key in coor:
        for validJoint in COORDINATE:
            if key == validJoint:
                tempPath[validJoint]=coor[key]
    tempPath["movement"]= 1 if relatively else 0            
    go(tempPath)
    return tempPath


def pickIt():
    adjustJoints({'j1':45,'j2':-90,'j3':45,'j4':0},False)
    moveToCoordinate({'x':15,'y':0,'z':3.5},False)
    moveToCoordinate({'x':16,'y':0,'z':10},False)
    adjust('j0',180)
    moveToCoordinate({'x':4,'y':0,'z':-5})
    moveToCoordinate({'x':0,'y':0,'z':-3})
    moveToCoordinate({'x':-5,'y':0,'z':8})
    adjust('j0',-180)
    moveToCoordinate({'x':15,'y':0,'z':3.5},False)
    go()