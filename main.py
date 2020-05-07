from flask import Flask,request,render_template,redirect,jsonify, make_response
from dorna_wrapper.dorna_wrapper import Arm
import json
app = Flask(__name__)
arm = Arm()
def resposePositions():
    joint = json.loads(arm.getPosition('joint'))
    xyz = json.loads(arm.getPosition('xyz'))
    #pos = arm.getPosition(space)
    respose = {'success':True,'data':{'joint':joint,'xyz':xyz}}
    print("updating ",respose)
    return make_response(json.dumps(respose),200)

@app.route('/get_current_position/<string:space>',methods=['GET'])
def getCurrentPosition(space):
    pos = json.loads(arm.getPosition(space))
    #pos = arm.getPosition(space)
    respose = {'success':True,'data':pos}
    print("updating ",respose)
    return make_response(json.dumps(respose),200)


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
    return make_response(jsonify('{success:true}'),200)

@app.route('/delete/<int:id>')
def delete(id):
    print("Deleting ",id)
    res = arm.positionStore.deleteWithId(id);
    print("Deleting ",res)
    return redirect('/')

@app.route('/goto_position/<int:id>',methods=['POST'])
def gotoPosition(id):
    print("goto ",id)
    arm.goToPositionID(id)
    return  resposePositions()
@app.route('/adjust_joint',methods=['POST'])
def adjust_joint():
    cmd = request.json
    arm.adjustJoints(cmd,False)
    return resposePositions()
@app.route('/home',methods=['POST'])
def home():
    arm.home()
    return make_response(jsonify('{success:true}'),200)

@app.route('/connect',methods=['POST'])
def connect():
    arm.connect()
   
    return resposePositions()


@app.route('/',methods=['GET','POST'])
def index():
    #arm.connect()
    positions = arm.positionStore.getAllPositions()
    posCount = len(positions)
    config = json.loads(arm.robot.config())

    
    return render_template('fixed.html',posCount=posCount,positions=positions,config=config)
if __name__ == '__main__':
    app.run(debug=True)