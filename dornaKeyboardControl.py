import time
import json
import pygame
from pygame.locals import *
from dorna_wrapper.dorna_wrapper import Arm

pygame.init()
BLACK = (10,10,10)
WIDTH = 300
HEIGHT = 100
FONT = pygame.font.SysFont('Comic Sans MS',40)
TEXT = FONT.render("DORNA ARM ROBOT",False,(0,0,255))
window = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
window.fill(BLACK)
window.blit(TEXT,(0,0))

##ROBOT SECTION
rate = 1
arm = Arm()
cmds = []

def setRate(r):
    rate = r
    print('Rate: ',rate)
def fireAdjustJont(joint,value):
    if(arm.getState()==0):
        arm.adjustJoint(joint,value)
    #cmd = {'joint':joint,'value':value}
    #cmds.append(cmd)
def executeCmd():
    if len(cmds)>0:
        cmd = cmds[0]
        arm.adjustJoint(cmd['joint'],cmd['value'])
        cmds.remove(cmd)

key = pygame.K_ESCAPE
while True:
    
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            key = event.key
            if key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                arm.adjustAxis('z',-rate)
            if key == pygame.K_z:
                arm.adjustAxis('z',rate)
        if event.type == KEYUP:
            if event.key != pygame.K_PERIOD and event.key != pygame.K_COMMA:
                arm.robot.halt()
            key = pygame.K_ESCAPE
    time.sleep(0.05)
    #presseds = pygame.key.get_pressed()
    #key = [pygame.key.name(k) for k,v in enumerate(presseds) if v]
    #print("Key Press",pygame.key.name(key))
    if key == pygame.K_HOME:
        arm.home()
    if key == pygame.K_DOWN:
        fireAdjustJont('j1',rate)
    if key == pygame.K_UP:
        fireAdjustJont('j1',-rate)
    if key == pygame.K_LEFT:
        fireAdjustJont('j0',rate)
    if key == pygame.K_RIGHT:
        fireAdjustJont('j0',-rate)
        
    if key == pygame.K_PAGEUP:
        fireAdjustJont('j2',-rate)
    if key == pygame.K_PAGEDOWN:
        fireAdjustJont('j2',rate)
        
    if key == pygame.K_w:
        fireAdjustJont('j3',-rate)
    if key == pygame.K_s:
        fireAdjustJont('j3',+rate)
    if key == pygame.K_a:
        fireAdjustJont('j4',rate)
    if key == pygame.K_d:
        fireAdjustJont('j4',-rate)
        
    if key == pygame.K_PERIOD:
        rate = rate+0.1
        print('Rate:',rate)
    if key == pygame.K_COMMA:
        rate = rate-0.1
        print('Rate:',rate)
        
    if key==pygame.K_END:
        arm.robot.set_io({'laser':1})
    if key==pygame.K_DELETE:
        arm.robot.set_io({'laser':0})
        
    if key == pygame.K_INSERT:
        print("enter positon Name: ")
        name = input()
        print("enter positon Description: ")
        des = input()
        print("enter space Space(xyz/joint): ")
        sp = input()
        arm.saveCurrentPosition(name,des,sp)
        arm.showAllPositions()
        
            
    if(arm.getState()==0):
        executeCmd()
        
