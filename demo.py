# demo.py

# Demo script using the drona_wrapper class

import time 

from dorna_wrapper.dorna_wrapper import Arm


testArm = Arm()

def picking():
    for i in [0,1]:    
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([3,8,4,5])
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([6,7,8])
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([7,6,5])
        testArm.grip(True)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([4,8,3,2])
        testArm.grip(False)
        testArm.waitForCompletion()
        testArm.goToMultiPositionIDs([9,3,8,9,2])

   
    
def motions():
    if testArm.isHomed:
        for i in [1,2,3]:
            testArm.grip(False)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['preOper'])
            testArm.goToMultiPositionNames(['PrePick','pick'])
            testArm.grip(True)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['preOper','rotation','drop'])
            testArm.grip(False)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['backOff'])
            testArm.goToMultiPositionNames(['drop'])
            testArm.grip(True)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['backOff'])
            testArm.goToMultiPositionNames(['preOper','PrePick','pick'])
            testArm.grip(False)
            testArm.waitForCompletion()
def shakes():
    if testArm.isHomed:
        ##for i in [1,2,3]:
            testArm.grip(False)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['preOper'])
            testArm.goToMultiPositionNames(['PrePick','pick'])
            testArm.grip(True)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['preOper','rotation'])
            d = 90
            
            
            testArm.adjustJoints({'j4':d})
            testArm.adjustAxis('x',100)
            testArm.adjustAxis('x',-10)
            testArm.adjustAxis('x',10)
            testArm.adjustAxis('x',-100)
            testArm.adjustJoints({'j4':-d})
            testArm.goToMultiPositionNames(['drop'])
            testArm.grip(False)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['backOff'])
            testArm.goToMultiPositionNames(['drop'])
            testArm.grip(True)
            testArm.waitForCompletion()
            testArm.goToMultiPositionNames(['backOff'])
            testArm.goToMultiPositionNames(['preOper','PrePick','pick'])
            testArm.grip(False)
            testArm.waitForCompletion()
            
      
   
'''
#testArm.robot._prnt=True
testArm.robot._log=[]
testArm.robot._log_id=1
testArm.home()

time.sleep(3)

testArm.goToPose(Arm.STANDING_POSE)
testArm.goToPose(Arm.FLAT_POSE)
testArm.goToPose(Arm.J04_CONFIG_POSE)
# testArm.robot.play({"command":"move", "prm":{'path':'line', 'movement':1, 'speed':5000, 'xyz':[30,0,0,0,0]}})

print(testArm.getPosition())

testArm.goToMultiPositionNames(['flat','pickingRight','prePowerDown'])

print("Completed Test Run, killing the connection")

testArm.kill()

print("killed")
'''
