# demo_gamepad.py

# Demonstration of using xbox360controller to control the dorna Arm

# You MUST run
# sudo xboxdrv --silent --detach-kernel-driver &
# from the terminal before using this

from xbox360controller import Xbox360Controller
import signal
import math

from dorna_wrapper.dorna_wrapper import Arm

testArm = Arm()
testArm.connect()
#testArm.home()
rate = 5

def on_button_pressed(button):
    global rate
    print('Button {0} was pressed {1}'.format(button.name,button))
    if button.name=='button_trigger_r':
        testArm.grip(True)
        testArm.waitForCompletion()
    elif button.name=='button_trigger_l':
        testArm.grip(False)
        testArm.waitForCompletion()
    if testArm.getState() != 0:
        return
    if button.name=='button_a':
        testArm.adjustJoint('j3',-rate,True)
        testArm.waitForCompletion()
    elif button.name=='button_y':
        testArm.adjustJoint('j3',rate,True)
        testArm.waitForCompletion()
    elif button.name=='button_b':
        testArm.adjustJoint('j4',-rate,True)
        testArm.waitForCompletion()
    elif button.name=='button_x':
        testArm.adjustJoint('j4',rate,True)
        testArm.waitForCompletion()
    else:
        print('No function attached to this button')
def on_trigger_moved(raw_axis):
 
    print('trigger {0} moved to {1}'.format(raw_axis.name, raw_axis.value))
    if raw_axis.name == 'trigger_l':
         print('')
    if raw_axis.name == 'trigger_r' and raw_axis.value ==1:
       testArm.showAllPositions()
    
def adjust_value(value):
    if value >0.8:
        return 1
    elif value <-0.8:
        return -1
    else: return 0
    
def on_axis_moved_l(axis):
    global rate
    x = adjust_value(axis.x)
    y = -adjust_value(axis.y)
    print('Axis {0} moved to x{1} y{2}'.format(axis.name, x, y))

    if y != 0 and testArm.getState()==0:
        testArm.adjustJoint('j2',rate*y)
    if x != 0 and y ==0:
        rate=rate+(x*0.1)
        if rate < 0:
            rate = 0
        print('RATE: ',rate)
def on_axis_moved_r(axis):
    global rate
    x = -adjust_value(axis.x)
    y = adjust_value(axis.y)
    print('Axis {0} moved to x{1} y{2}'.format(axis.name, x, y))
    if x != 0:
        rate = rate+(x*1)
        if rate < 0:
            rate = 0
        print('RATE: ',rate)
    
def on_hat_move(axis):
    print('state :',testArm.getState())
    if testArm.getState() != 0:
        return
    if axis.x!=0 and axis.y==0:
        testArm.adjustJoint('j0',rate*axis.x,True)
        testArm.waitForCompletion()
    elif axis.y!=0 and axis.x==0:
        testArm.adjustJoint('j1',rate*axis.y,True)
        testArm.waitForCompletion()
def on_mode(button):
    testArm.robot.halt()
def on_started(button):
    testArm.home()
def on_selected(button):
    print("enter positon Name: ")
    name = input()
    print("enter positon Description: ")
    des = input()
    print("enter space Space(xyz/joint): ")
    sp = input()
    arm.saveCurrentPosition(name,des,sp)
    arm.showAllPositions()
    
try:
    with Xbox360Controller(0, axis_threshold=0.2) as controller:
        
        controller.button_a.when_pressed = on_button_pressed
        controller.button_b.when_pressed = on_button_pressed
        controller.button_y.when_pressed = on_button_pressed
        controller.button_x.when_pressed = on_button_pressed
        
        controller.button_trigger_l.when_pressed = on_button_pressed
        controller.button_trigger_r.when_pressed = on_button_pressed
        controller.trigger_l.when_moved = on_trigger_moved
        controller.trigger_r.when_moved = on_trigger_moved
        
        controller.axis_l.when_moved = on_axis_moved_l
        controller.axis_r.when_moved = on_axis_moved_r
        
        controller.hat.when_moved=on_hat_move
        controller.button_select.when_pressed = on_selected
        controller.button_start.when_pressed = on_started
        controller.button_mode.when_pressed = on_mode
        
        signal.pause()
except KeyboardInterrupt:
    pass