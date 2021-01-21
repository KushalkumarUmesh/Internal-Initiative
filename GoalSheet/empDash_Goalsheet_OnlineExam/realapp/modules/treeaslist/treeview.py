"""
K.Srinivas, 12-Jun-2018

Project: Demo Tree view project for "skills" tree
Description: Parent-child relationship in a single list

TODO: 

KNOWN BUGs: None
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required ,  current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from realapp import app, db
from loadfromxls import *
from hrmsdomain import getEmployeebyId
from goaldomain import deleteGoalSheet, assignTemplate, getAllGoalsAndSections


#Temp, ONE-TIME use Target for uploading Targets-Set from XLS-files to DB
#Lot of Hard-Coding, not expected to be used more than once
@app.route('/skills/show', methods=['GET'])
@app.route('/skills/show/<int:id>', methods=['GET'])
def uploadTargets(id = -1) :
