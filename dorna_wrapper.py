from dorna import Dorna

import time
import datetime

import sys
import os
import platform

import configparser

class pose:

    def __init__(self,position,description):

        """
        CLASS DEFINING A POSE IN JOINT SPACE

        Position is a list of the joint positions in this pose.
        Description is a human-readable description of the pose.
        """

        # TODO add type info (joint or xyz) and any other decriptors.

        self.position=position
        self.description=description

class arm:

    """
    WRAPPER CLASS FOR A SINGLE DORNA ARM.

    Exposes simple utility functions for connection and homing, movement, and IO.
    LIENG Hongky and Leo JOFEH @ Bespokh.com, 2020
    """

    # Utility constants

    WORKING_DIRECTORY = os.getcwd()
    DEFAULT_CONFIG = "./config.yaml"

    DEFAULT_SPEED = 1000

    ABSOLUTE = 0
    RELATIVE = 1

    # Utility lists

    JOINTS = ['j0','j1','j2','j3','j4']

    # Utility poses

    HOME_POSE = pose([0,135,-90,-45,0],"the HOME (resting) position")
    FLAT_POSE = pose([0,0,0,0,0],"the FLAT (outstretched) position")
    
    # Initialisation

    def __init__(self,port=None,config=None):

        """
        INITIALISE THE ARM OBJECT.

        If no port is specified (e.g. /dev/tty0 or COM3) then it will auto-detect the appropriate port.
        If no configuration file is specified then it will attempt to load "/home/pi/Desktop/config.yaml"
        """

        # Attempt to load a Dorna object with a configuration file, default to the desktop config if none is entered manually.

        config = config if config!= None else self.DEFAULT_CONFIG

        try:
            self.robot=Dorna(config)
            print("Loaded configuration file")
        except:
            print("Failed to load configuration file, please re-instantiate the arm object with a valid config.")
            return 0

        # Attempt to connect the arm, defaulting to auto-port-detection.

        try:
            self.robot.connect()
        except:
            print("Connection failed, please re-instantiate the arm object with a valid port.")
            return 0

        # This function either exits with a live arm reporting device status, or fails with 0 and advises the user.

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
        print("Completed move")

    def getMovementCommand(self,pose,space='joint',movement=ABSOLUTE,speed=DEFAULT_SPEED):

        """
        CREATE A SINGLE MOVEMENT COMMAND DICTIONARY FOR USE WITH OTHER FUNCTIONS.

        Returns a single movement command in the format required for robot native play function.
        """

        # TODO fix for all movement types

        jointspaceDictionary={'path':space,'movement':movement, 'speed':speed}
        for index, joint in enumerate(self.JOINTS):
            jointspaceDictionary[joint]=pose.position[index]

        return {"command":"move","prm":jointspaceDictionary}

