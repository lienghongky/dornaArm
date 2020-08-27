# Dorna Arm Robot Controll Application
![Program](/sh.jpg)
# SCREIPT
##Run WEB GUI to controller Dorna Arm robot.
```
python main.py
```
##Initialize Dorna Arm robot and control robot by typing commands.
```
python demo.py
```
##Run GamePad control program to use xbox controllre to controler Dorna Arm robot.
```
python dornaGamepadControl.py
```
##Run Keyboard control program to control Dorna Arm robot with keyboard.
```
python dornaKeyboardControl.py
```
## Install LIBS

```
pip install flask
pip install tabulate
pip install rich
```
#Structure

##dorna_custom_api: customized Dorna Original api
##dorna_wraper: Class contain all new useful function
##configuration_store: Store all data and file used by dorna_wraper class
##position_store: Class for managing Data like position store cmd store ..
##template: containe all WEB GUI HTML, CSS, JS ...
 
