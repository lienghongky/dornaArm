# demo.py

# Demo script using the drona_wrapper class

import time 

from dorna_wrapper import *

testArm = arm()
testArm.home()

time.sleep(3)

testArm.goToPose(arm.STANDING_POSE)
testArm.goToPose(arm.FLAT_POSE)
testArm.goToPose(arm.HOME_POSE)

print(testArm.getPosition())

print("Completed Test Run")

