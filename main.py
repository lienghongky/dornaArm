from flask import Flask,request,render_template,redirect,jsonify, make_response
from dorna_wrapper.dorna_wrapper import Arm
import json
app = Flask(__name__)
arm = Arm()
##OTHER FUCNTION
def resposePositions():
    arm.waitForCompletion()
    joint = json.loads(arm.getPosition('joint'))
    xyz = json.loads(arm.getPosition('xyz'))
    #pos = arm.getPosition(space)
    respose = {'success':True,'data':{'joint':joint,'xyz':xyz}}
    print("respose position ",respose)
    return make_response(json.dumps(respose),200)

#### GET ROBOT JOINTS AND XYZ
@app.route('/get_current_position/<string:space>',methods=['GET'])
def getCurrentPosition(space):
    pos = json.loads(arm.getPosition(space))
    #pos = arm.getPosition(space)
    respose = {'success':True,'data':pos}
    print("updating ",respose)
    return make_response(json.dumps(respose),200)

### POSITION AND COMMAND DATA FUNCTION
@app.route('/get_position',methods=['GET'])
def getPosition():
    joint = json.loads(arm.getPosition('joint'))
    xyz = json.loads(arm.getPosition('xyz'))
    #pos = arm.getPosition(space)
    respose = {'success':True,'data':{'joint':joint,'xyz':xyz}}
    print("updating ",respose)
    return make_response(json.dumps(respose),200)

@app.route('/update',methods=['POST'])
def update():
    json = request.json
    print('json',json)
    if json['id'] == None or json['id']=='':
        arm.positionStore.save(json['name'],json['position'],json['description'],json['space'])
    else:
        print("request ",request.json['id'])
        res = arm.positionStore.updateWithId(int(json['id']),json['name'],json['position'],json['description'],json['space'])
        print("updating ",res)
    return resposePositions()

@app.route('/delete/<int:id>')
def delete(id):
    print("Deleting ",id)
    res = arm.positionStore.deleteWithId(id)
    print("Deleting ",res)
    return redirect('/')
 
### GROUP COMMAND DATA FUNCTION 
@app.route('/save_command_group',methods=['POST'])
def save_command_group():
    data = request.json
    ids = data.get('ids',[])
    name = data.get('name','name')
    arm.positionStore.saveGroup(name,ids)
    cmd_groups = arm.positionStore.getCommandGroups()
    respose = {'success':True,'data':{'command_groups':cmd_groups}}
    print(respose)
    return make_response(json.dumps(respose),200)

@app.route('/get_command_groups',methods=['GET'])
def get_command_groups():
    cmd_groups = arm.positionStore.getCommandGroups()
    respose = {'success':True,'data':{'command_groups':cmd_groups}}
    return make_response(json.dumps(respose),200)

@app.route('/delete_command_group/<string:name>')
def delete_command_group(name):
    print("Deleting group ",name)
    res = arm.positionStore.deleteGroup(name)
    cmd_groups = arm.positionStore.getCommandGroups()
    respose = {'success':True,'data':{'command_groups':cmd_groups}}
    return make_response(json.dumps(respose),200)

### ROBOT MOVE FUNCETIONS
@app.route('/goto_position/<int:id>',methods=['POST'])
def gotoPosition(id):
    print("goto ",id)
    arm.goToPositionID(id)
    return  resposePositions()

@app.route('/goto_command_group/<string:name>',methods=['Get'])
def goto_command_group(name):
    print("goto command_group",name)
    ids = arm.positionStore.getCommandGroup(name).get('cmds',[])
    print(ids)
    arm.goToMultiPositionIDs(ids)
    return resposePositions()

@app.route('/goto_multi_positions',methods=['POST'])
def goto_Multi_Positions():
    data = request.json
    print("goto ",data)
    ids = data.get('ids',[])
    arm.goToMultiPositionIDs(ids)
    return  resposePositions()
@app.route('/grip',methods=['POST'])
def grip():
    cmd = request.json
    print(cmd)
    arm.grip(cmd['grip'])
    return  resposePositions()

@app.route('/adjust_joints',methods=['POST'])
def adjust_joints():
    cmd = request.json
    print('cmd ',cmd)
    arm.adjustJoints(cmd,False)
    return resposePositions()
@app.route('/adjust_axis',methods=['POST'])
def adjust_axis():
    cmd = request.json
    arm.adjustCoordinate(cmd,False)
    return resposePositions()
@app.route('/adjust_xyz',methods=['POST'])
def adjust_xyz():
    param = request.json
    cmd = param.get('cmd',None)
    print(param)
    if param.get('movement',0) == 0 :
        arm.adjustCoordinate(cmd)
    else:
        x = cmd.get('x',0)
        y = cmd.get('y',0)
        z = cmd.get('z',0)
        j0 = param.get('j0',None)
        arm.adjustArmCoordinateXYZ(x,y,z,j0)
    return resposePositions()
@app.route('/adjust_joint',methods=['POST'])
def adjust_joint():
    cmd = request.json
    print('cmd ',cmd)
    arm.adjustJoints(cmd,True)
    return resposePositions()

## 
@app.route('/home',methods=['POST'])
def home():
    arm.home()
    return resposePositions()

@app.route('/connect',methods=['POST'])
def connect():
    arm.connect()
   
    return resposePositions()

#### PAGE ROUTE
@app.route('/stack',methods=['GET','POST'])
def stack():
    #arm.connect()
    positions = arm.positionStore.getAllPositions()
    posCount = len(positions)
    config = json.loads(arm.robot.config())
    return render_template('stack.html',posCount=posCount,positions=positions,config=config)

@app.route('/config',methods=['GET','POST'])
def configPage():
    config = json.loads(arm.robot.config())   
    return render_template('config.html',config=config)

@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route('/',methods=['GET','POST'])
def index():
    #arm.connect()
    cmdGroups = arm.positionStore.getCommandGroups()
    cmdGroupsCount = len(cmdGroups)
    positions = arm.positionStore.getAllPositions()
    posCount = len(positions)
    config = json.loads(arm.robot.config())

    data = {'posCount':posCount,'positions':positions,'config':config,'cmdGroups':cmdGroups,'cmdGroupsCount':cmdGroupsCount}
    return render_template('index.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)