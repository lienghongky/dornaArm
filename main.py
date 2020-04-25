from flask import Flask,request,render_template
from dorna_wrapper.dorna_wrapper import Arm
app = Flask(__name__)
arm = Arm()

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)