# demo.py

# Demo script using the drona_wrapper class

import time
import math
#from dorna_custom_api.api import Dorna
from dorna_wrapper.dorna_wrapper import Arm

config = "./configuration_store/config.yaml"
#robot=Dorna(config)
testArm = Arm()
testArm.connect()

def adjustXyzToJoint(x,z):
        l1 = 8
        l2 = 6
        j3 = 0
        
        
        L = math.sqrt(x**2 + z**2)
        print('L = ',L)
        
        q5 = math.acos((l1**2 + l2**2 - L**2)/(2*l1*l2))
        q2 = q5-math.pi
        q1 = math.acos((l1**2 + L**2 - l2**2)/(2*l1*L))
        q3 = math.atan2(z,x)

        qa=q1+q3
        j3 = math.radians(j3)-qa-q2


        print('q1 = ',q1)
        print('q2 = ',q2)
        print('q3 = ',q3)
        print('q5 = ',q5)
        print('qa = ',qa)
        print('j3 = ',j3)
        
        q1 = math.degrees(q1)
        q2 = math.degrees(q2)
        q3 = math.degrees(q3)
        q5 = math.degrees(q5)
        qa = math.degrees(qa)
        j3 = math.degrees(j3)
        
       
        print('\nq1 = ',q1)
        print('q2 = ',q2)
        print('q3 = ',q3)
        print('q5 = ',q5)
        print('qa = ',qa)
        print('j3 = ',j3)
        
        
        pos = {'j1':qa,'j2':q2,'j3':j3}
        #self.adjustJoints(pos)
        return pos
adjustXyzToJoint(1,10)

def picking():
    for i in [0,1]:    
        testArm.goToMultiPositionIDs([18,19])
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([18,19])
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([22,23])
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([22,23])
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([22,21,20])
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([21,20])
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([21,8])

