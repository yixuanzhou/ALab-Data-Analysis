import os
from flask import Flask,render_template,request,url_for,send_from_directory,redirect
from werkzeug import secure_filename
from flask import request
from calculateQ import baseQ

app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['lvm'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<imgPath>')
def index(imgPath):
    return render_template('index.html', filepath=imgPath)

@app.route('/process',methods=['GET','POST'])
def calculate():
    qname = request.args.get('name')
    res = baseQ(qname)
    result = {'result': res}    

@app.route('/upload',methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) 
        return redirect(url_for('index', imgPath=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = '../'+ app.config['UPLOAD_FOLDER']+filename
    return redirect(url_for('display',imgPath=filepath))        

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("4001")
    )
