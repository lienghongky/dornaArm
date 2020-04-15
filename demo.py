# demo.py

# Demo script using the drona_wrapper class

import time 

from dorna_wrapper.dorna_wrapper import Arm

testArm = Arm()
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

