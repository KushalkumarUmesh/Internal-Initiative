"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: This is ONLY a test file, for debugging purposes.

TODO: None

KNOWN BUGs: None
"""

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import *
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from werkzeug import secure_filename

#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.dialects.mysql import BIT, LONGBLOB, TINYBLOB

#Login Implimentation
#from flask_login import LoginManager
#from flask_login import UserMixin


#My modules/and stuff
"""
import sys
sys.path.insert(0,'modules/masterdata')
sys.path.insert(0,'shared/candidateinterface')
sys.path.insert(0,'../..')

import QuestionBank
import TestBank
import CandidateInteface
from ReadConfig.AppConfig import AppConfig
#Create our own items and get ready
#TODO: ALl DB Parameters need to come from the XLS-FILE..but that gets more UNSAFE from security perspective
appC = AppConfig("C:\\Users\\kambhs\\Desktop\\Projects\\OnlineExam\\OnlineExamConfig.xlsx")
questionsBanks = QuestionBank(appC)
testBank = TestBank(appC)
testBank.setQuestionBank(questionsBanks)
"""

app = Flask(__name__)

#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://ks:Kambh12#@localhost:3306/alchemy1"
#app.config['SECRET_KEY'] = "ZXFGHJKLPwefghjm"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['WTF_CSRF_SECRET_KEY'] = 'srini random string'

#Start DB Session
#db = SQLAlchemy(app)

@app.route('/upload', methods=['GET'])
def upload() :
    if request.method == 'GET' :
        return  """
                <html>
                <body>
                
                    <form action = "http://localhost:5000/uploader" method = "POST" 
                        enctype = "multipart/form-data">
                        <input type = "file" name = "file" />
                        <input type = "submit"/>
                    </form>
                    
                </body>
                </html>
                """

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
#      f.save(f.filename)
      return 'file uploaded successfully'

# Replicate QuestionAns form and add a Submit button
class listEdit(FlaskForm) :
    submit = SubmitField('Submit') #   
    oks = FieldList(FormField(BooleanField()), min_entries=100)


@app.route('/')
@app.route('/home')
def home() :
    return redirect("/media/online tax-paying information.txt")

@app.route('/media/<path:filename>', methods=['GET','POST'])
def send_foo(filename):
    return send_from_directory('.', filename, as_attachment=True)


# Basic Qustion-Answer Form, relicated in QuestionForm
#class QuestionAns(FlaskForm) :
#    ques = ""
#    answer = RadioField('Label')
#    rememberme = BooleanField("Keep me logged in")
#    rememberme = TextField("Keep me logged in")



if __name__ == "__main__" :
    app.run(debug=True)


