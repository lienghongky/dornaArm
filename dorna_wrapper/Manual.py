from pynput.keyboard import Key,KeyCode, Listener
from dorna_wrapper import *
import json
import keyboard

rate = 1
arm = Arm()
cmds = []
shouldListen = True
def setRate():
    print("rate:",rate)
def execute():
    print ("loop")
    while len(cmds)>0:
        for cmd in cmds:
            arm.adjustJoint(cmd['joint'],cmd['value'])
            cmds.remove(cmd)
            print("running")
            arm.waitForCompletion()
            print('next')
       
def fireAdjustCmd(joint,value):
    cmd = {'joint':joint,'value':value}
    cmds.append(cmd)
    print(cmds)
    execute()
    
def onPress(key):
    global shouldListen
    if not shouldListen:
        return
    keycode = None
    try:
        keycode = key.char
    except AttributeError:
        pass
    #print('{0} pressed'.format(key))
    if key == Key.right:
        fireAdjustCmd('j0',1*rate)
    if key == Key.left:
        fireAdjustCmd('j0',-1*rate)
    if key == Key.up:
        fireAdjustCmd('j1',1*rate)
    if key == Key.down:
        fireAdjustCmd('j1',-1*rate)
    if keycode == '8':
        fireAdjustCmd('j2',1*rate)
    if keycode == '2':
        fireAdjustCmd('j2',-1*rate)
    if keycode == '6':
        fireAdjustCmd('j4',1*rate)
    if keycode == '4':
        fireAdjustCmd('j4',-1*rate)
    if key == Key.page_up:
        fireAdjustCmd('j3',1*rate)
    if key == Key.page_down:
        fireAdjustCmd('j3',-1*rate)
        
def onRelease(key):
    keycode = None
    global rate
    global arm
    global shouldListen
    if not shouldListen:
        return
    try:
        keycode = key.char
    except AttributeError:
        pass
    #print('{0} release'.format(key))
    if keycode == '+':
        
        rate = rate+1
        print("rate:",rate)
    if keycode == '-':
        rate = rate-1 if rate-1>=0 else 0
        print("rate:",rate)
    if key == Key.home:
        arm.home()
    if key == Key.space:
        arm.robot.halt()
    if keycode == 's':
        shouldListen = False
        print("enter positon Name: ")
        name = input()
        print("enter positon Description: ")
        des = input()
        print("enter space Space(xyc/joint): ")
        sp = input()
        arm.saveCurrentPosition(name,des,sp)
        arm.showAllPositions()
        shouldListen = True
    if key==Key.esc:
        
        return False
    
with Listener(on_press = onPress,
              on_release = onRelease) as listener:
    listener.join()

