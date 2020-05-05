from flask import Flask,request,render_template,redirect
from dorna_wrapper.dorna_wrapper import Arm
app = Flask(__name__)
arm = Arm()



@app.route('/update/<int:id>')
def delete(id):
    print("Deleting ",id)
    res = arm.positionStore.deleteWithId(id);
    print("Deleting ",res)
    
    return redirect('/')
@app.route('/delete/<int:id>')
def delete(id):
    print("Deleting ",id)
    res = arm.positionStore.deleteWithId(id);
    print("Deleting ",res)
    
    return redirect('/')
@app.route('/gotoposition',methods=['POST'])
def gotoPosition():
    if request.method == 'POST':
        #id = request.form.get('id')
        print(arm.getState())
        arm.home()
        return redirect('/')
@app.route('/a')
def indexA():
    positions = arm.positionStore.getAllPositions()
    posCount = len(positions)
    return render_template('fixed.html',posCount=posCount,positions=positions)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if request.form['goto_button']:
           id = request.form.get('id')
           print('id ',id)
           arm.goToPositionID(id)
    positions = arm.positionStore.getAllPositions()
    posCount = len(positions)
    return render_template('fixed.html',posCount=posCount,positions=positions)
if __name__ == '__main__':
    app.run(debug=True)