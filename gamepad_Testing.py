# gamepad_demo.py

# demos the gamepad controls using xbox_controller

from xboxcontroller.controller import *
arm='tester'
c = xbox_controller(arm)
c.control_loop()

print('\n\ncompleted\n')

