"""
K.Srinivas, 18-Jul-2018

Project: Goal Sheet - Calendar View
Description: This contains the views for displaying a goal-sheet Calendar

TODO: NOT YET IMPLEMENTED
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import required, DataRequired, Length
from flask_login import login_required, current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from realapp import app, db
from goaldomain import *
import os
from hrmsdomain import *
import datetime as dt
from dateutil import parser
from goalflags import * 
from hrmsempdata import getEmpDictbyEmail, getEmpDictbyEmpid
from calendarmodel import *

class CalenderForm(FlaskForm) :
    id = IntegerField()
    phase = StringField(u'Phase', validators=[DataRequired(), Length(max=200)],)
    phaseType = SelectField(u'PhaseType ', choices=[], default ='' )
    empEmail = StringField(u'Employ Email', validators=[DataRequired(), Length(max=200)], )
    description = StringField(u'Description', validators=[DataRequired(), Length(max=200)],  widget=TextArea() )
    assessmentYear  = StringField(u'AssessmentYear', validators=[DataRequired(), Length(max=200)],  widget=TextArea() )
    dateStart =  DateTimeField('Start Date(DD-MM-YY)', [validators.required()],  format='%d-%m-%y')
    dateEnd =  DateTimeField('End Date(DD-MM-YY)', [validators.required()],  format='%d-%m-%y')
    authlevel = IntegerField()
    gs_enable_assignment = BooleanField(u'gs_enable_assignment',[validators.required(), validators.length(max=200)],  default = True )

    # Sheet-Flags
    gs_enable_mid_year_self = BooleanField(u'gs_enable_mid_year_self',[validators.required(), validators.length(max=200)],  default = True )
    gs_enable_mid_year_dc_approve = BooleanField(u'gs_enable_mid_year_dc_approve',[validators.required(), validators.length(max=200)],  default = True )
    gs_enable_end_year_self = BooleanField(u'gs_enable_end_year_self',[validators.required(), validators.length(max=200)],  default = True )
    gs_enable_end_year_dc_approve = BooleanField(u'gs_enable_end_year_dc_approve',[validators.required(), validators.length(max=200)],  default = True )
    gs_enable_end_year_closure =BooleanField(u'gs_enable_end_year_closure',[validators.required(), validators.length(max=200)],  default = True )
    # Goal-Flags
    goal_enable_task_approve = BooleanField(u'goal_enable_task_approve',[validators.required(), validators.length(max=200)],  default = True )
    goal_enable_edit = BooleanField(u'goal_enable_edit',[validators.required(), validators.length(max=200)],  default = True )
    goal_enable_approve = BooleanField(u'goal_enable_approve',[validators.required(), validators.length(max=200)],  default = True )

    # Task-Flags
    task_enable_update = BooleanField(u'task_enable_update',[validators.required(), validators.length(max=200)],  default = True )
    task_enable_delete = BooleanField(u'task_enable_delete',[validators.required(), validators.length(max=200)],  default = True )
    task_enable_activity_edit = BooleanField(u'task_enable_activity_edit',[validators.required(), validators.length(max=200)],  default = True )
    task_enable_status_change = BooleanField(u'task_enable_status_change',[validators.required(), validators.length(max=200)],  default = True )

    #submit btn
    submit = SubmitField()

@app.route('/goals/goalcal', methods=('GET','POST'))
@login_required  #Without login, we don't know who it is
def goalcal(year = '2018-2019') :
    year = session['year']
    table = 'GoalCalendar'
    cname = eval(table)
    allCals = cname.query.filter_by(assessmentYear = year).all()

    form = CalenderForm(request.form)  # Create an itemList from request.form, in case of post
    if request.method == "POST" : #and form.validate_on_submit():
        pass # Do nothing
    form = CalenderForm()  # Create an itemList from request.form, in case of post
    allCals = cname.query.filter_by(assessmentYear = year).all()
    return render_template('goalsheet/calshowedit.html', itemSet = allCals, form = form )


# @app.route('/goals/showCalendarSummary', methods=('GET','POST'))
# @login_required  #Without login, we don't know who it is
# def goalcal(year = '2018-2019') :
#     table = 'GoalCalendar'
#     cname = eval(table)
#     allCals = cname.query.filter_by(assessmentYear = year).all()
# authlevel
#     form = CalenderForm(request.form)  # Create an itemList from request.form, in case of post
#     if request.method == "POST" : #and form.validate_on_submit():
#         pass # Do nothing
#     form = CalenderForm()  # Create an itemList from request.form, in case of post
#     allCals = cname.query.filter_by(assessmentYear = year).all()
#     return render_template('goalsheet/calshowedit.html', itemSet = allCals, form = form )

