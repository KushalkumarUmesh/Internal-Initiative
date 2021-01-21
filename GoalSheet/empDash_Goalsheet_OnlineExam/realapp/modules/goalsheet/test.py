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

from goalmodel import *
#from goalview import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://ks:Kambh12#@localhost:3306/goal_sheet"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "ZXFGHJKLPwefghjm"
app.config['WTF_CSRF_SECRET_KEY'] = 'srini random string'
#Start DB Session
db = SQLAlchemy(app)
db.drop_all()
db.create_all()




