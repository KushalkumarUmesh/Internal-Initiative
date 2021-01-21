"""
K.Srinivas, 16-Apr-2018

Project: Goal Sheet
Description: This contains the views for displaying a goal-sheet to the user, the core end-screen, will need serious interface from HRMS

TODO: 
TASK:
a) Task Completion Status: Implement a Select box, with a default
b) For each URL, check that logged-in User is the owner of the item OR the DC of the item of admin
c) DONE:Task-Creation needs to be moved to Domain Module, so that date-Assigned, etc. are filled in
d) Prevent Task-updates after approval, except for status change and personal notes. Adding is allowed.
e) Create an "abandoned" Status for a task, with notes

TODO:GOAL-SHEET:
a) DONE: Goal-Sheet: Implement a "Request for Approval" button
b) DONE: UI-Needs to be good, fix the Emp-Data Part
c) Implement restrictions on work-flow: who is allowed to change what and when

KNOWN BUGs: 
a) In taskupdate, the "task" object flags should be set BEFORE the form-object is created.
They way it is written appears to confuse some method somewhere.

NOTE: All manager/management related views moved to goaldisplaymanagers.py
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import required, DataRequired, Length
from flask_login import login_required, current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for, session
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from realapp import app, db, RepresentsInt
from goaldomain import *
import os
from hrmsdomain import *
import datetime as dt
from dateutil import parser
from goalflags import * 
from hrmsempdata import getEmpDictbyEmail, getEmpDictbyEmpid

##########################################################################################################################
#### Display/Edit Goal-Sheet for end user ##############################

class DocumentUploadForm(FlaskForm) :
    submit = SubmitField('Upload') #   

#Key screen allowing an employee to see the goals, set-his targets and send for approval
@app.route('/goals/goalsetupdate', methods=('GET', 'POST'))
@login_required  #Without login, we don't know who it is
def goalsetupdate(year = '2018-2019') :     #Lets not take assessment year for now, but we default it nicely
    year = session['year']
    form = DocumentUploadForm()
    empEmail = current_user.username.lower()
    empInfo = getGoalSheetHeader(empEmail, year)
    empId = str(empInfo['EmployeeID'])
    if not RepresentsInt(empId) :
        app.logger.info("EmpID obtained is not INT:email Id:" + empEmail)
    #Get list of Goals, group-by-sectio
    (sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
    # Get All the Tasks for these goals, grouped nicely by goal-ID
    if not sheet :
        return render_template('goalsheet/message.html', message = "No Goals have been Assigned. Please contact your DC Lead.")
    msgDict = getEmpDictbyEmpid(sheet.assessingManager)
    empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
        
    alltasks = getAllTasks( allgoals)
    #Set Flags based on Authorization level = Check if its own item or someone else
    ownItem = False
    empEmail = current_user.username.lower()
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == sheet.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
    setGoalSheetFlags(sheet, alltasks, authlevel) # Set Goal-Level flags
    setAllGoalsFlags(allgoals,authlevel) # Set Goal-Level flags
    setAllTasksFlags(alltasks,authlevel) # Set Task-level Flags

    return render_template('goalsheet/goalsheetshow.html', goalSheet = sheet, goalSections = allgoalsections, \
        goals = allgoals, alltasks=alltasks, empInfo = empInfo, num=len(allgoalsections), form=form)

##########################################################################################################################
#### Task Management s##############################
class TaskForm(FlaskForm) :
    id = IntegerField()
    description = StringField(u'Description', validators=[DataRequired(), Length(max=200)],  widget=TextArea() )
    manadator = BooleanField(u'Priority',[validators.required(), validators.length(max=200)],  default = True )
    dateStart  = DateTimeField('Start Date(DD-MM-YY)', [validators.required()],  format='%d-%m-%y')
    dateEnd  = DateTimeField('Complete By(DD-MM-YY)', [validators.required()], format='%d-%m-%y')
    personalNotes = StringField(u'Comments' , widget=TextArea())
    completionstatus = SelectField(u'Select Status', choices=[], default ='' )
    enable_activity_edit = False
    enable_status_change = True
    enable_edit =True
    enable_update = False
    completionCheckBox = BooleanField(u'Completed',  default = False )
    submit = SubmitField('Add/Update') #   

#Display a List of Tasks for a given Goal, and allow add, update and delete
@app.route('/goals/tasksaddupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def tasksListAdd(id) : # id is the id of the GoalSection, goes as is into the object creation
    table = 'Task'
    cname = eval(table)
    goal = Goal.query.filter_by(id = id).first()

    #Set Authorization level = Check if its own item or someone else
    ownItem = False
    empEmail = current_user.username.lower()
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == goal.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level

    setGoalFlags(goal, authlevel)
    goalTitle = goal.title
    form = TaskForm(request.form)  # Create an itemList from request.form, in case of post
    form.completionstatus.choices = getTaskStatusForSelect() 
    form.enable_edit = goal.enable_edit # If the goal allows for adding tasks
    if request.method == "POST" : #and form.validate_on_submit():
        obj = createTask(goal, cstatus = "Identified")
        setTaskFlags(obj, authlevel)
        if authorizeTaskCreateOrUpdate(obj, form, goal, is_create=True) :
            obj.completionstatus = "Identified" # Needed as UI is sending it in Approved status
    #        print("Data" + str(request.form))
            if taskValid(request, goal, obj) :
                db.session.add(obj) # Add it to the data base
                db.session.commit()
    form = TaskForm()  # Create an itemList from request.form, in case of post
    form.completionstatus.choices = getTaskStatusForSelect() 
    form.enable_edit = goal.enable_edit # If the goal allows for adding tasks
    allTasks = cname.query.filter_by(goalId = int(id)).all()

    #Set Flags
    setTaskListFlags(allTasks,authlevel) # Set Task-level Flags
    return render_template('goalsheet/taskshowlist.html', itemSet = allTasks, form = form, goalTitle = goalTitle, parentid=id )

#Update a Given Task, ID is provided. Goal-ID and SHeet ID are already available, so no need for anything else
@app.route('/goals/tasksupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def tasksUpdate(id) : # id is the id of the GoalSection, goes as is into the object creation
    table = 'Task'
    cname = eval(table)
    empEmail = current_user.username.lower()
    task = Task.query.filter_by(id = id).first()
    goal = Goal.query.filter_by(id = task.goalId).first()

    #Set Authorization level = Check if its own item or someone else
    ownItem = False
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == goal.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
#    app.logger.info("Auth:" + str(authlevel) + ":" + str(ownItem))

    setTaskFlags(task, authlevel)
    setGoalFlags(goal,authlevel)
    goalTitle = goal.title
    if request.method == "POST" :
        form = TaskForm(request.form)  # Create an itemList from request.form, in case of post
        if authorizeTaskCreateOrUpdate(task, form, goal) :
            if taskValid(request, goal, task) :
                db.session.commit()
                return redirect(url_for('tasksListAdd', id=task.goalId))
    #Get the Task AGAIN from DB, discard all changes
    task = Task.query.filter_by(id = id).first()            
    form = TaskForm(obj=task)  # Create an itemList from request.form, in case of post
    form.completionstatus.choices = getTaskStatusForSelect()
    form.completionstatus.data = task.completionstatus
    if (task.completionstatus == "Completed" ) :
        form.completionCheckBox.data = True
    allTasks = cname.query.filter_by(goalId = task.goalId).all()
    #Set Flags
    setTaskListFlags(allTasks,authlevel) # Set Task-level Flags
    form.enable_edit = task.enable_update # If the goal allows for adding tasks
#    form.enable_update = task.enable_update # If the goal allows for adding tasks
    form.enable_activity_edit = task.enable_activity_edit # If the goal allows for adding tasks
    form.enable_status_change = task.enable_status_change # If the goal allows for adding tasks
    return render_template('goalsheet/taskshowlist.html', itemSet = allTasks, form = form, goalTitle = goalTitle, parentid=id )

#DONE: Make this ADMIN only Once the goalsheet is approved
#TODO: Remove Feedback and AskFeedback objected linked to this task
@app.route('/goals/taskdelete/<int:id>', methods=('GET', 'POST'))
@login_required
def taskDelete(id) : # id of the GoalSection is passed here
    table = 'Task'
    cname = eval(table)

    task = Task.query.filter_by(id = id).first()
    goal = Goal.query.filter_by(id = task.goalId).first()
    parentid = task.goalId

#Verify if the person is authorized to DELETE
    empEmail = current_user.username.lower()
    ownItem = False
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == goal.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
    setTaskFlags(task, authlevel)
    if not task.enable_delete :
        flash("Unauthorized change requested.")
        return redirect(url_for('tasksListAdd', id=parentid))
        
    item = cname.query.filter_by(id = id ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    db.session.commit()

    #Delete Feedbacks linked to this task
    #Delete AskFeedbacks linked to this task

    return redirect(url_for('tasksListAdd', id=parentid))

def authorizeTaskCreateOrUpdate(task, form, goal, is_create=False) :
#If neither activit nor enable_edit is present, submit cannot be done
    if not (task.enable_activity_edit or goal.enable_edit ) :
    	return False

    objectChanged = False
# Desc, Dates and Mandatory
    if (goal.enable_edit and is_create) or task.enable_update : #Goal-level flag, Create New is allowed
        #Description       
        task.description = form.description.data
        #Date
        task.dateStart = form.dateStart.data
        task.dateEnd = form.dateEnd.data
        #Mandatory
        task.manadator = form.manadator.data
        objectChanged = True
    
#Activity
    if (goal.enable_edit and is_create) or task.enable_update or task.enable_activity_edit  :
        task.personalNotes = form.personalNotes.data
        objectChanged = True

#Status - Anything
    if task.enable_status_change :
        task.completionstatus = form.completionstatus.data
        objectChanged = True
    elif task.enable_activity_edit and form.completionCheckBox.data :
        if task.completionstatus == "Approved" :
            task.completionstatus = "Completed"
            objectChanged = True

    return objectChanged


#My Own validator for response from Task pages. This became essential for :
#b) Dates need to be validated to be with-in the range of the Goal-Dates
def taskValid(request, goal, task) :
    error_found = 0
    err_str = ""

    if (task.dateStart < goal.dateStart  or \
        task.dateEnd > goal.dateEnd  or \
        task.dateStart >  task.dateEnd) :
        error_found = 1
        err_str += "Task Dates must be between the Goal start/end dates, end-date must be after start-date."

    if error_found :
        flash(err_str)
        return False

    return True


