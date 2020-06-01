from dorna_custom_api.api import Dorna
from copy import deepcopy
import time
import datetime
import math
import json

import sys
import os
import os.path
import platform

import configparser

from dorna_wrapper.PositionStore import *

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)





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

    def connect(self):
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
        gpio = pose.gpio
        if gpio != None:
            pin = gpio.get('pin',None)
            value = gpio.get('value',0)
            if pin != None:
                if type(pin) is str:
                    self.robot.set_io({pin:value})
                else:
                    GPIO.output(pin, {0:False,1:True}[value])
                self.waitFor()
                return 'Set Io: '+str(pin)+' value: '+str(value)
        print(gpio)
        cmd = self.getMovementCommand(pose,speed=speed)
        print(cmd)
        self.robot.play(cmd)
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
            gpio = p.gpio
            if gpio != None:
                pin = gpio.get('pin',None)
                value = gpio.get('value',0)
                if pin != None:
                    if type(pin) is str:
                        self.robot.set_io({pin:value})
                    else:
                        GPIO.output(pin, {0:False,1:True}[value])
                    self.waitFor()
                    print('Set Io: '+str(pin)+' value: '+str(value))
                    continue
            
            #cmds.append(self.getMovementCommand(p,speed=speed))
            cmd = self.getMovementCommand(p,speed=speed)
            self.robot.play(cmd)
            self.waitForCompletion()
        '''
        if len(cmds)>0:
            self.robot.play(cmds)
            self.waitForCompletion()
            print("Completed move")
        '''
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
    def waitFor(self,duration=2):

        """
        RETURN ON COMPLETION OF THE CURRENT TASK QUEUE
        """
        time.sleep(duration)
        print('Done waiting for ',duration)
        return
    
    def getState(self):
        return json.loads(self.robot.device())['state']
    
    #Gripper
    def grip(self,grip=True,gripPressure=0):
        value = gripPressure if grip else 1
        self.robot.set_io({"out1":value,"out2":value,"out3":value,"out4":value})
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
        print('id :',i,' pos',pos.position)
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
                print(i," Position not Found")
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
                return
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
        MOVE with xyz Coordinate System Related to current rotation
        =================================================
    """
    #pass in coordinate object as parameter
    #ex:moveToCoordinate({'x':10,'y':20,'z':10})
    def adjustArmCoordinateXYZ(self,x,y,z,j0=None):
        currentPos = json.loads(self.robot.position('x'))
        joints = json.loads(self.robot.position('j'))
        j0 = {True:j0,False:joints[0]}[j0!=None]
        dx = x*math.cos(math.radians(joints[0]))
        dy = x*math.sin(math.radians(joints[0]))
        
        dy = dy+y*math.sin(math.radians(90-j0))
        dx = dx-y*math.cos(math.radians(90-j0))
        print({'dx':dx,'dy':dy})
        self.adjustCoordinate({'x':dx,'y':dy,'z':z})
    def adjustArmCoordinate(self,coor,relatively=True):
        
        currentPos = json.loads(self.robot.position('x'))
        x = coor.get('x',currentPos[0]) #+ currentPos[0]
        z = coor.get('z',currentPos[2]) #+ currentPos[2]
        jointConvert = self.xyzToJoint(x,z,coor.get('a',None))
        if jointConvert['status']==0:
            cjoint = json.loads(self.robot.position('j'))
            joint = jointConvert['joint']
            j1 = joint['j1']# - cjoint[1]
            j2 = joint['j2']# - cjoint[2]
            self.adjustJoints({'j1':j1,'j2':j2},False)
        return jointConvert
        
       
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


    """
    status: 0: valid and safe xyz
    status: 1: valid but not safe xyz
    status: 2: not a valid xyz
    """
    def xyzToJoint(self,x=None,z=None,a=None):
        config = self.robot._config
        delta_e = self.robot._delta_e
        l1 = self.robot._l1
        l2 = self.robot._l2
        bx = self.robot._bx
        bz = self.robot._bz
        
        limitJ0 = config['limit']['j0']
        limitJ1 = config['limit']['j1']
        limitJ2 = config['limit']['j2']
        limitJ3 = [-135,135]
        limitJ4 = [-360,360]
        
        
        x = {True: self.robot._mm_to_inch(x) , False: self.robot._mm_to_inch(json.loads(self.robot.position('x'))[0])}[x != None]
        z = {True: self.robot._mm_to_inch(z) , False: self.robot._mm_to_inch(json.loads(self.robot.position('x'))[2])}[z != None]
        j3 = {True:a,False:json.loads(self.robot.position('j'))[3]}[a != None]
        
        print(x,z)
        x -= bx#(bx + config["toolhead"]["x"] * math.cos(alpha))
        z -= bz#(bz + config["toolhead"]["x"] * math.sin(alpha))
        
        L = math.sqrt(x**2 + z**2)
        print('L=',L)
          # not valid
        if L > (l1 + l2) or l1 > (l2 + L) or l2 > (l1 + L):  # in this case Provided XZ not safe
            return {'joint':{'j1':None,'j2':None,'j3':None} ,'status': 2,'error':'invalid x or z or both'}

        # init status
        status = 0
        if L > (l1 + l2) - delta_e or self.robot._l1 > (l2 + L) - delta_e: # in this case XYZ not safe
            status = 1

        
        q5 = math.acos((l1**2 + l2**2 - L**2)/(2*l1*l2))
        q2 = q5-math.pi
        q1 = math.acos((l1**2 + L**2 - l2**2)/(2*l1*L))
        q3 = math.atan2(z,x)

        qa=q1+q3
        j3 = math.radians(j3)-qa-q2
        
        q1 = math.degrees(q1)
        q3 = math.degrees(q3)
        q5 = math.degrees(q5)
        
        j1 = math.degrees(qa)
        j2 = math.degrees(q2)
        j3 = -j1-j2
        
        if j3<limitJ3[0]:
            j3 = j3+180
        if j3>limitJ3[1]:
            j3=j3-180
        
       
        print('\nq1 = ',q1)
        print('q2/j2 = ',j2)
        print('q3 = ',q3)
        print('q5 = ',q5)
        print('qa/j1 = ',j1)
        print('j3 = ',j3)
        

        
        if j1<limitJ1[0] or j1>limitJ1[1] or j2<limitJ2[0] or j2>limitJ2[1] or j3<limitJ3[0] or j3>limitJ3[1]:
            return {'joint':{'j1':j1,'j2':j2,'j3':j3},'status': 1,'error':'Unsafe j1 or j2 or j3 or all'}
        
        #if L > (l1 + l2) or l1 > (l2 + L) or l2 > (l1 + L):  # in this case Provided XZ not safe
        #    return {'j1':None,'j2':None,'j3':None ,'status': 2}
        
        pos = {'joint':{'j1':j1,'j2':j2,'j3':j3},'status':0}
        #self.adjustJoints(pos)
        return pos
    
    ''''
    def xyz_to_joint(self,xyz):
        print("_xyz_to_joint INPUT: ",xyz)
        if any(xyz == None): # xyz contains None coordinate
            return {"joint": np.array([None for i in range(len(xyz))]), "status": 2}
        config = self.robot._config
        delta_e = self.robot._delta_e
        l1 = self.robot._l1
        l2 = self.robot._l2
        bx = self.robot._bx
        bz = self.robot._bz
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        alpha = xyz[3]
        beta = xyz[4]

        alpha = math.radians(alpha)
        beta = math.radians(beta)

        # first we find the base rotation
        teta_0 = math.atan2(y, x)

        # next we assume base is not rotated and everything lives in x-z plane
        x = math.sqrt(x ** 2 + y ** 2)

        # next we update x and z based on base dimensions and hand orientation
        x -= (bx + config["toolhead"]["x"] * math.cos(alpha))
        z -= (bz + config["toolhead"]["x"] * math.sin(alpha))

        # at this point x and z are the summation of two vectors one from lower arm and one from upper arm of lengths l1 and l2
        # let L be the length of the overall vector
        # we can calculate the angle between l1 , l2 and L
        L = math.sqrt(x ** 2 + z ** 2)
        L = np.round(L,13) # ???
        # not valid
        if L > (l1 + l2) or l1 > (l2 + L) or l2 > (l1 + L):  # in this case there is no solution
            return {"joint": np.array([None for i in range(len(xyz))]), "status": 2}

        # init status
        status = 0
        if L > (l1 + l2) - delta_e or self.robot._l1 > (l2 + L) - delta_e: # in this case there is no solution
            status = 1

        teta_l1_L = math.acos((l1 ** 2 + L ** 2 - l2 ** 2) / (2 * l1 * L))  # l1 angle to L
        teta_L_x = math.atan2(z, x)  # L angle to x axis
        teta_1 = teta_l1_L + teta_L_x
        # note that the other solution would be to set teta_1 = teta_L_x - teta_l1_L. But for the dynamics of the robot the first solution works better.
        teta_l1_l2 = math.acos((l1 ** 2 + l2 ** 2 - L ** 2) / (2 * l1 * l2))  # l1 angle to l2
        teta_2 = teta_l1_l2 - math.pi
        teta_3 = alpha - teta_1 -
        
        teta_4 = beta
        teta_0 = math.degrees(teta_0)
        teta_1 = math.degrees(teta_1)
        teta_2 = math.degrees(teta_2)
        teta_3 = math.degrees(teta_3)
        teta_4 = math.degrees(teta_4)


        if len(xyz) == 6:
            joint = np.array([teta_0, teta_1, teta_2, teta_3, teta_4, xyz[5]])
        else:
            joint = np.array([teta_0, teta_1, teta_2, teta_3, teta_4])

        print("_xyz_to_joint",joint)
        return {"joint": joint, "status": status}
    '''