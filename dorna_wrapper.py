from dorna import Dorna

import time
import datetime

import json

import sys
import os
import platform

import configparser

class pose:
    PATH_JOINT = 'joint'
    PATH_LINE = 'line'

    SPACE_JOINT = 'joint'
    SPACE_XYZ = 'xyz'

    def __init__(self,position,description,space='joint'):

        """
        CLASS DEFINING A POSE IN JOINT SPACE

        Position is a list of the joint positions in this pose.
        Description is a human-readable description of the pose.
        """

        # TODO add type info (joint or xyz) and any other descriptors.
        
        self.space=space # 'joint' space or 'xyz' space 
        self.position=position
        self.description=description
        self.path = self.PATH_JOINT if space == self.SPACE_JOINT else self.PATH_LINE

class arm:

    """
    WRAPPER CLASS FOR A SINGLE DORNA ARM.

    Exposes simple utility functions for connection and homing, movement, and IO.
    LIENG Hongky and Leo JOFEH @ Bespokh.com, 2020
    """

    # Utility constants

    DEFAULT_CONFIG = "./config.yaml"

    DEFAULT_SPEED = 6000

    ABSOLUTE = 0
    RELATIVE = 1

    SPACE_JOINT = 'joint'
    SPACE_XYZ = 'xyz'

    PATH_JOINT = 'joint'
    PATH_LINE = 'line'

    # Utility lists

    JOINTS = ['j0','j1','j2','j3','j4']
    AXISES = ['x','y','z','a','b']

    # Utility poses

    HOME_POSE = pose([0,135,-90,-45,0],"the HOME (resting) position",SPACE_JOINT)
    FLAT_POSE = pose([0,0,0,0,0],"the FLAT (outstretched) position",SPACE_JOINT)
    STANDING_POSE = pose([0,90,0,0,0],"the STANDING (vertical) position",SPACE_JOINT)
    
    # Initialisation

    def __init__(self,port=None,config=None):

        """
        INITIALISE THE ARM OBJECT.

        If no port is specified (e.g. /dev/tty0 or COM3) then it will auto-detect the appropriate port.
        If no configuration file is specified then it will attempt to load "/home/pi/Desktop/config.yaml"
        """

        # Attempt to load a Dorna object with a configuration file, default to the desktop config if none is entered manually.

        config = config if config!= None else self.DEFAULT_CONFIG

        self.WORKING_DIRECTORY = os.getcwd()

        try:
            self.robot=Dorna(config)
            print("Loaded configuration file")
        except:
            print("Failed to load configuration file, please re-instantiate the arm object with a valid config.")
            return 0

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

    # TODO Adjustment function
    
