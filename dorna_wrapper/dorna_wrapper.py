from dorna_custom_api.api import Dorna
from copy import deepcopy
import time
import datetime

import json

import sys
import os
import os.path
import platform

import configparser

from dorna_wrapper.PositionStore import *


class Arm:

    """
    WRAPPER CLASS FOR A SINGLE DORNA ARM.

    Exposes simple utility functions for connection and homing, movement, and IO.
    LIENG Hongky and Leo JOFEH @ Bespokh.com, 2020
    """

    # Utility constants

    # DEFAULT_CONFIG = "../configuration_store/config.yaml"

    DEFAULT_SPEED = 60000

    ABSOLUTE = 0
    RELATIVE = 1

    SPACE_JOINT = 'joint'
    SPACE_XYZ = 'xyz'

    PATH_JOINT = 'joint'
    PATH_LINE = 'line'

    # Utility lists

    JOINTS = ['j0','j1','j2','j3','j4']
    AXISES = ['x','y','z','a','b']
    PRM_TEMPLATE ={'path':'joint','movement':1}

    # Utility poses
    

    HOME_POSE = Position('home',[0,135,-90,-45,0],"the HOME (resting) position",SPACE_JOINT)
    FLAT_POSE = Position('flat',[0,0,0,0,0],"the FLAT (outstretched) position",SPACE_JOINT)
    STANDING_POSE = Position('standing',[0,90,0,0,0],"the STANDING (vertical) position",SPACE_JOINT)
    J04_CONFIG_POSE = Position('j04',[0,15,-100,0,0],"the FLAT (outstretched) position",SPACE_JOINT)
    # Initialisation

    def __init__(self,port=None,config=None):

        """
        INITIALISE THE ARM OBJECT.

        If no port is specified (e.g. /dev/tty0 or COM3) then it will auto-detect the appropriate port.
        If no configuration file is specified then it will attempt to load "/home/pi/Desktop/config.yaml"
        """

        # Attempt to load a Dorna object with a configuration file, default to the desktop config if none is entered manually.

        self.WORKING_DIRECTORY = os.getcwd()
        self.FILE_DIRECTORY = os.path.dirname(__file__)
        self.DEFAULT_CONFIG = os.path.join(self.FILE_DIRECTORY, "../configuration_store/config.yaml")
        
        self.positionStore = PositionStore()
        
        config = config if config!= None else self.DEFAULT_CONFIG

        try:
            print(config)
            self.robot=Dorna(config)
            print("Loaded configuration file")
        except:
            print("Failed to load configuration file, please re-instantiate the arm object with a valid config.")

        # Attempt to connect the arm, defaulting to auto-port-detection.

        try:
            self.robot.connect()
            print("Connected to robot")
        except:
            print("Connection failed, please re-instantiate the arm object with a valid port.")
            return 0

        # This function either exits with a live arm reporting device status, or fails with 0 and advises the user.
    
    def kill(self):
        self.robot.disconnect()
        self.robot.terminate()
    
    def home(self):

        """
        HOME AND LOAD CALIBRATION FOR THE ARM

        Perform a homing cycle with calibration from the pre-loaded configuration file.
        Assumes that the arm is near the 'rest' position when called. DANGEROUS IF NOT.
        It will perform homing and load the config even if all joints have already been homed.
        This will leave the arm in the exact 'rest' position, within ~1mm at the toolhead.
        """

        # Report the current homing state

        print("Current homing state: {}".format(self.robot.homed()))

        # Home each joint, even if it is already reported homed, except j4 which auto-homes with j3, and any other unhomable joint.

        for joint in self.JOINTS[0:4]: 
            print("Homing {}".format(joint))
            self.robot.home(joint)

        print("Homed all joints")

        self.goToPose(self.HOME_POSE)

        return

    def goToPose(self,pose,speed=DEFAULT_SPEED):

        """
        MOVE THE ARM DIRECTLY TO A KNOWN POSE IN JOINT SPACE.

        Move the arm to the absolute pose specified at the speed specified, defaulting to the default speed.
        """

        print("Moving to {}".format(pose.description))
        self.robot.play(self.getMovementCommand(pose,speed=speed))
        self.waitForCompletion()
        print("Completed move")
    def goToMultiPose(self,poses,speed=DEFAULT_SPEED):

        """
        MOVE THE ARM DIRECTLY TO A KNOWN POSE IN JOINT SPACE.

        Move the arm to the absolute pose specified at the speed specified, defaulting to the default speed.
        """
        cmds = []
        for p in poses:
            print("Moving to {}".format(p.name))
            cmds.append(self.getMovementCommand(p,speed=speed))
        if len(cmds)>0:
            self.robot.play(cmds)
            self.waitForCompletion()
            print("Completed move")

    def getMovementCommand(self,pose,movement=ABSOLUTE,speed=DEFAULT_SPEED):

        """
        CREATE A SINGLE MOVEMENT COMMAND DICTIONARY FOR USE WITH OTHER FUNCTIONS.

        Returns a single movement command in the format required for robot native play function.
        """

        # TODO fix for all movement types //DONE

        spaceDictionary={'path':pose.path,'movement':movement, 'speed':speed}
        if (pose.space == self.SPACE_JOINT):
            for index, joint in enumerate(self.JOINTS):
                spaceDictionary[joint]=pose.position[index]
        elif (pose.space == self.SPACE_XYZ):
            for index, axis in enumerate(self.AXISES):
                spaceDictionary[axis]=pose.position[index]


        return {"command":"move","prm":spaceDictionary}

    def getPosition(self,space=SPACE_JOINT):

        """
        RETURN THE CURRENT POSITION OF THE ARM IN THE SPECIFIED SPACE
        """

        return self.robot.position(space)

    def waitForCompletion(self):

        """
        RETURN ON COMPLETION OF THE CURRENT TASK QUEUE
        """

        while(json.loads(self.robot.device())['state']!=0):
            time.sleep(0.1)
            continue

        return
    
    def getState(self):
        return json.loads(self.robot.device())['state']
    
    #Gripper
    def grip(self,grip=True,gripPressure=0):
        value = gripPressure if grip else 1
        self.robot.set_io({"laser":value})
    #Saving positon
    def showAllPositions(self):
        self.positionStore.showAllPositions()
        
    def saveCurrentPosition(self,name,description,space="joint"):
        currentPosition = json.loads(self.robot.position(space))
        self.positionStore.save(name,
                                currentPosition,
                                description,
                                space)
        
    def deletePosition(self,name):
        self.positionStore.delete(name)
        
    def updatePosition(self,name,position,description,space):
        self.positionStore.update(name,
                                  position=position,
                                  depositionStorescription=description,
                                  space=space)
    def goToPositionID(self,i):
        pos = self.positionStore.getPostionById(i)
        if pos != None:
            self.goToPose(pos)
        else:
            print(i," Position not Found")
            
    def goToMultiPositionIDs(self,ids):
        poses = []
        for i in ids:
            pos = self.positionStore.getPostionById(i)
            if pos != None:
                poses.append(pos)
            else:
                print(name," Position not Found")
        if len(poses) > 0:
            self.goToMultiPose(poses)                              
    def goToPositionName(self,name):
        pos = self.positionStore.getPostion(name)
        if pos != None:
            self.goToPose(pos)
        else:
            print(name," Position not Found")
            
    def goToMultiPositionNames(self,names):
        poses = []
        for name in names:
            pos = self.positionStore.getPostion(name)
            if pos != None:
                poses.append(pos)
            else:
                print(name," Position not Found")
        if len(poses) > 0:
            self.goToMultiPose(poses)
    # TODO Adjustment function
    def calibrateAndSave(self,prm):
        self.robot.calibrate(prm)
        self.robot.save_config()
    def setJ04Zero(self):
        """
        SET ALL JOINTS TO ZERO AND SAVE CONFIG FILE TO THE ONE IN USED
        SHOULD ONLY BE CALL WHEN THE ARM IS IN FlAT POSITION(MANUALLY OR COMMENT)
        """
        self.robot.set_joint({'j0':0})
        self.robot.set_joint({'j4':0})
        self.robot.save_config()     
    def setAllZero(self):
        """
        SET ALL JOINTS TO ZERO AND SAVE CONFIG FILE TO THE ONE IN USED
        SHOULD ONLY BE CALL WHEN THE ARM IS IN FlAT POSITION(MANUALLY OR COMMENT)
        """
        self.robot.set_joint([0,0,0,0,0])
        self.robot.save_config()
        
    def isConnected(self):
        device = json.loads(self.robot.device())
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
    def go(self,position):
            print("Go to ",position)
            tmpcmd={"command":"move", "prm":position}
            self.robot.play(tmpcmd)
            
    #pass in joint and value as parameter ex:adjust("j0",10)
    def adjustJoint(self,joint, degrees:float,relatively=True):
        """
        ADJUST the joints
        """
        # creates a position-movement description that can be fed to go().
        
        tempPath=deepcopy(self.PRM_TEMPLATE)
        for j in self.JOINTS:
            if j == joint:
                
                tempPath[j]=degrees
                break
        tempPath["movement"]= 1 if relatively else 0
        self.go(tempPath)
        return tempPath  

    #pass in joints object as parameter ex:adjust({"j1":0,"j2":0})
    def adjustJoints(self,joints,relatively=True):
        # creates a position-movement description that can be fed to go().
        tempPath=deepcopy(self.PRM_TEMPLATE)
        
        for key in joints:
            for validJoint in self.JOINTS:
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
        tempPath=deepcopy(self.PRM_TEMPLATE)
        tempPath['path'] = 'line'
        
        for c in self.AXISES:
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
        tempPath=deepcopy(self.PRM_TEMPLATE)
        tempPath['path'] = 'line'
        
        for key in coor:
            for validJoint in self.AXISES:
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

    def writeGcodeDirectToPort(gc):
        '''
        Writes whatever gcode you pass as a string 'gc' to the function directly to the port.
        '''
        self.robot._port.write((gc + '\n').encode())
        return None
