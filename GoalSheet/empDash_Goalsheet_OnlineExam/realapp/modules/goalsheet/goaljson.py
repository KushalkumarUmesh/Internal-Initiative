"""
K.Srinivas, 06-Jul-2018

Project: Goal Sheet
Description: This contains the AJAX-responses for Goal-Sheet and also call-backs for 
various sheet-level actions to implement the work-flow. Could be implemented as AJAX
or direct calls.

TODO: 

KNOWN BUGs: None
"""
from flask import request, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
import logging
from realapp import app, db
from feedbackdomain import *
from goalmodel import *
from goaldomain import *
from hrmsdomain import getEmpIdByEmail
import documentdomain as dd
from realapp import cache
import json
#from flask.ext.api import status

#from flask import send_from_directory, render_template, redirect, request, flash
"""
from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import required, DataRequired, Length
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from goaldomain import *
import os
from hrmsdomain import *
import datetime as dt
from dateutil import parser
from goalflags import * 
"""

@app.route("/goals/tasklevelupdate", methods=('GET','POST'))
@login_required
def tasklevelupdate():
#    print ("IN tasklevelupdate")
    if request.method == "POST" : 
        content = request.get_json(silent=True)
        taskIdStr = content['Task_id']
        taskStatusStr = content['Status']
        feedback = content['Feedback']

    if request.method == "GET" : 
        taskIdStr = request.args.get('Task_id')
        taskStatusStr = request.args.get('Status')
        feedback = request.args.get('Feedback')
                
    #Get Task Task
    task = Task.query.filter_by(id = int(taskIdStr)).first()
    task.completionstatus = taskStatusStr #Update Task Status
    db.session.commit()
    # Get ID, comments, Approved/Returned
    if feedback :
        giverEmpId = getEmpIdByEmail(current_user.username)
        recordTaskFeedback(task, feedback, giverEmpId = giverEmpId)

    return "Updated"

@app.route("/goals/taskfileupload", methods=['POST'])
@login_required
def taskfileupload():
    empEmail = current_user.username.lower()
    if request.method == "POST" : 
        taskId = request.form['Task_id']
        #print(request.form)       
        #print(request.files['fileToSave'].filename) 
        dd.saveFile(request.files['fileToSave'], empEmail, app.config['DOCTYPE_TASK'] , taskId)
    return "File Uploaded"

@app.route("/goals/sheetfileupload", methods=['POST'])
@login_required
def sheetFileUpload():
    empEmail = current_user.username.lower()
    if request.method == "POST" : 
        sheetId = request.form['Sheet_id']
        dd.saveFile(request.files['fileToSave'], empEmail, app.config['DOCTYPE_SHEET'] , sheetId)
    return "File Uploaded"


@app.route("/goals/taskfilemeta/<taskId>", methods=['GET'])
@login_required
def taskFileMeta(taskId):
    (uploadFolder, storedfileName,fileName ) = dd.getFileByTypeAndId(app.config['DOCTYPE_TASK'] , taskId) 
    if not uploadFolder :
        return "No File Available"
    else :
        return fileName

@app.route("/goals/sheetfilemeta/<sheetId>", methods=['GET'])
@login_required
def sheetFileMeta(sheetId):
    (uploadFolder, storedfileName,fileName ) = dd.getFileByTypeAndId(app.config['DOCTYPE_SHEET'] , sheetId) 
    if not uploadFolder :
        return "No File Available"
    else :
        return fileName

@app.route("/goals/taskfiledownload/<taskId>", methods=['GET'])
@login_required
def taskFileDownload(taskId):
    (uploadFolder, storedfileName,fileName ) = dd.getFileByTypeAndId(app.config['DOCTYPE_TASK'] , taskId) 
    if not uploadFolder :
        return "File Not Found", 404

    return send_from_directory(uploadFolder, storedfileName, attachment_filename=fileName, as_attachment=True)

@app.route("/goals/sheetfiledownload/<sheetId>", methods=['GET'])
@login_required
def sheetFileDownload(sheetId):
    (uploadFolder, storedfileName,fileName ) = dd.getFileByTypeAndId(app.config['DOCTYPE_SHEET'] , sheetId) 
    if not uploadFolder :
        return "File Not Found", 404

    return send_from_directory(uploadFolder, storedfileName, attachment_filename=fileName, as_attachment=True)


@app.route("/goals/goallevelupdate", methods=['POST'])
def goallevelupdate():
#    print ("IN goallevelupdate")
    content = request.get_json(silent=True)
    goalIdStr = content['Goal_id']
    goalStatusStr = content['Status']
    feedback = content['Feedback']
    #Get Task Task
    goal = Goal.query.filter_by(id = int(goalIdStr)).first()
    goal.completionstatus = goalStatusStr #Update Task Status
    #Update All tasks in this goal to "Approved" IF the status is approved, else do nothing
    if goalStatusStr == "Approved" :
        setStatusInAllTasksInGoal(goal.id, status = "Approved" )
    db.session.commit()
    # Get ID, comments, Approved/Returned
    if feedback :
        giverEmpId = getEmpIdByEmail(current_user.username)
        recordGoalFeedback(goal, feedback, giverEmpId = giverEmpId)
#    print (content)
    return "Updated"

#Not Used
#@app.route('/goals/goaltargetupdate/<int:goalId>', methods=('GET', 'POST'))
@app.route('/goals/goaltargetupdate', methods=('GET', 'POST'))
@login_required  #Without login, we don't know who it is
def goalTargetUpdate() :     #Lets not take assessment year for now, but we default it nicely
    #get Goal-by-ID
    id=request.args.get('id')
    gl = getGoalById(id)
    #print(str(request.args.get))
    if request.args.get('target') :
        #print(str("Updating Target"))
        gl.targetSet = request.args.get('target')
    db.session.commit()
    return gl.targetSet

@app.route('/goals/goalSheetAction', methods=['GET'])
@login_required  #Without login, we don't know who it is
def sheetActionl() :
    goalSheetId = request.args.get('goalSheetId')
    if goalSheetId.isdigit() :
        sheetId = int(goalSheetId)
    else :
        return ("Invalid Sheet ID")
        
    sheet = getGoalSheet(sheetId)
    actionId = request.args.get('actionId')

    ownItem = False
    empEmail = current_user.username.lower() # 2nd time?
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == sheet.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
    mgmtLevel = getMgmtRelationship(sheet, empEmail, loggedInEmpId=loginedInEmpId  )

    if actionId == "1" : # Submit for approval
    # Goalsheet status changed to PendingApproval
    # Trigger e-mail to manager/employee
        requestGoalSheetApproval(sheet)

    if actionId == "2" : # Request Feeback Review by Employee
    # Goalsheet status changed to PendingReview
    # Trigger e-mail to manager/employee
        pendingReviewGoalSheet(sheet)

    if actionId == "4" : # DC-Lead provides Feedback to Employee    
    # Goalsheet status changed to Approved
    # Trigger e-mail to manager/employee
    #Need to implement AUTH level
        if current_user.is_dclead or current_user.is_Manager : # must be a DC-Lead or manager        
            managerSubmitFeedbackGoalSheet(sheet)

    if actionId == "5" : # Employee Submits self Assessment
        submitSelfAssessment(sheet)

    print("GoalSheetAction:" + str(goalSheetId) + ":" + str(actionId))
    db.session.commit()
    return redirect(url_for('goalsetupdate'))
    return "Unknown Action"

#Method to SAVE Task-level evaluation
#Note that the same method works for both the self and finalevaluation.
#The reason for doing this is that authorization check is ANYWAY needed
@app.route('/goals/taskRatingUpdate', methods=['POST'])
@login_required  #Without login, we don't know who it is
def taskRatingUpdate() :
    #Validate User? Is it required ?
    content = request.get_json(silent=True)
    taskIdStr = request.form['Task_id']
    taskRating = request.form['Task_rating']
    taskAssessment = request.form['Task_assessment']
    taskComment = None
#    print("request-form" + str(request.form))

    if 'Task_comment'  in request.form.keys() :
        taskComment = request.form['Task_comment']

    if not taskIdStr :
        return None #Silently ignore
    if not taskRating :
        return None #Silently ignore
    if not taskAssessment :
        return None #Silently ignore
        
    #Get Task
    task = Task.query.filter_by(id = int(taskIdStr)).first()
    if not task :
        return None #Silently ignore

    # We find out if the user who is doing the update is the owner or someone higher
    empEmail = current_user.username.lower() # 2nd time?
    ownItem = False
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == getGoalSheetOwner(task.goalSheetId)) :
        ownItem = True
    authLevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level

    if authLevel >= 3 : # HR/MGMT/Admin
        task.l3Rating = taskRating  
        task.l3Assessment = taskAssessment  
    elif authLevel == 2 : # DC-Lead
        task.l2Rating = taskRating  
        task.l2Assessment = taskAssessment  
    elif authLevel == 1 : # 1st Level Manager
        task.l1Rating = taskRating  
        task.l1Assessment = taskAssessment  
    else : # Must be owner as authLevel is ZERO
        task.selfRating = taskRating  
        task.selfAssessment = taskAssessment  

    #Save the TaskComment, if available
    db.session.commit() # Task is committed at this point
    if not taskComment :  return "Updated"

    #Some Comment was given
#    print("Saving feedback at authLevel:"+ str(authLevel))
    recordTaskFeedback(task, taskComment, visibleToEmp = False, visiblityLevel=authLevel ,  giverEmpId = loginedInEmpId  )

    return "Updated with Comments"

@cache.memoize(timeout=1800)
def getGoalSheetOwner(sheetId) :
    gs = getGoalSheet(sheetId)
    if not gs :
        return None
    return gs.empId

#Method to serve and save Sheet-Level Assessment
#This method handles bit of a complex logic in terms of displaying and saving emp. assessment
#At the end, it also changes the sheet status, which causes the flags to change on refresh
@app.route('/goals/goalSheetRatingList', methods=('GET','POST'))
@login_required  #Without login, we don't know who it is
def goalSheetRatingList() :
    #Get Auth Level of the logged-in user
    empEmail = current_user.username.lower()
    user = current_user.username
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    authLevel = getAuthLevel(empEmail, False, current_user.is_admin) # Get Auth Level

    if authLevel == 0 : 
        print("Not authorized")
        return "Not authorized" # Silently ignore

    if request.method == "GET" : 
        sheetId = request.args.get('Sheet_id')
        if not sheetId :
            print("SheetiD NOT FOUND:" + str(sheetId))
            return ("SheetiD NOT FOUND:" + str(sheetId))
        sheetFeedbackList = [] #Define empty List
        rating = 0
        gs = getGoalSheetById(int(sheetId) )
        if not gs : #Goal-sheet not found
            print("NOT FOUND GS with ID:" + str(sheetId))
            return ("NOT FOUND GS with ID:" + str(sheetId))
        mgmtLevel = getMgmtRelationship(gs, empEmail, loggedInEmpId=loginedInEmpId)
#        print("GS-Found:" + str(sheetId))

        #We have two tasks: Get and set the correct rating for return, get the comments from current or previous level
        #Get the rating 
        if mgmtLevel == 1 :
            rating = gs.l1Rating
        elif mgmtLevel == 2 :
            rating = gs.l2Rating
        elif mgmtLevel == 3 :
            rating = gs.l3Rating
        else :
            print("Invalid AUTH level:" + str(mgmtLevel) + ":" + empEmail)
            return ("Invalid AUTH level:" + str(mgmtLevel))
        #UI needs this as an INT :-(
        if rating == "Not Rated" :
            rating = 0
        else :
            rating  = int(rating)

        if mgmtLevel == 2 and not rating : # 2nd level is viewing it while first level has give the rating
            rating = gs.l1Rating
        elif mgmtLevel == 3 and not rating : # 2nd level is viewing it while 2nd or 1st level has give the rating
            rating = gs.l2Rating
            if rating == "Not Rated" or not rating :
                rating = gs.l1Rating # fill with 1st level

        #2nd time, as it might have been switched to a lower level
        if rating == "Not Rated" :
            rating = 0
        
        #Get the comments 
        if authLevel > 1 : # If the auth-level is greater than one, get one below that level
#            print("Getting previous feedback...")
            #First check if a comment was already given at your level
            sheetFeedbackList = getGoalFeedback(gs.empId,False, authLevel, sheetId,1) # List of goal-feedbacks GoalFeedback
            if not sheetFeedbackList : #If not get it from one below
                sheetFeedbackList = getGoalFeedback(gs.empId,False, authLevel-1, int(sheetId),1) # List of goal-feedbacks GoalFeedback
            if not sheetFeedbackList and authLevel > 2 : #If not get it from two below
                sheetFeedbackList = getGoalFeedback(gs.empId,False, authLevel-2, sheetId,1) # List of goal-feedbacks GoalFeedback
        else : # Show 1st level manager's own feedback
            sheetFeedbackList = getGoalFeedback(gs.empId,False, authLevel, sheetId,1) # List of goal-feedbacks GoalFeedback

        if  sheetFeedbackList : # Take the last one
            sheetRatingInfo = [int(rating), sheetFeedbackList[-1].feedback]
        else :            
            sheetRatingInfo = [int(rating), ""]
#        print("Rating Info=" + str(sheetRatingInfo))
        return json.dumps(sheetRatingInfo)
    else : #Assume POST
        sheetId = request.form['Sheet_id']
        sheetRating = request.form['Sheet_rating']
        sheetComments = request.form['Sheet_comments']
        gs = getGoalSheetById(int(sheetId) )
        if not gs : #Goal-sheet not found
            print("NOT FOUND GS with ID:" + str(sheetId))
            return "Invalid Goal-Sheet ID"

        mgmtLevel = getMgmtRelationship(gs, empEmail, loggedInEmpId=loginedInEmpId)

        #Update Sheet Status
        if mgmtLevel == 1 :
            gs.l1Rating = sheetRating
            gs.status = "Pending-2ndLevel"
        elif mgmtLevel == 2 :
            gs.l2Rating = sheetRating
            gs.status = "Pending-MGMT"
        elif mgmtLevel == 3 :
            gs.l3Rating = sheetRating
            gs.status = "Completed"
        else :
            print("Invalid AUTH level:" + str(mgmtLevel) + ":" + empEmail)
            return ("Invalid AUTH level:" + str(mgmtLevel))
        
#        print("Updating the following:" + str(sheetId) + ":" + str(sheetRating)  +":" + str(sheetComments))
        recordSheetFeedback(gs, sheetComments, visibleToEmp = False,visiblityLevel=authLevel ,  giverEmpId = loginedInEmpId  )
        #Set-up notifications ??
        return "Updated"



#Method to Serve Comments for Task-level evaluation
#Return a json list with: name, comment and date
#For testing only, using GET
#@app.route('/goals/gettaskcomments/<taskIdStr>', methods=['GET'])
@app.route('/goals/gettaskcomments', methods=['POST'])
@login_required  #Without login, we don't know who it is
#def getTaskCommentsJson(taskIdStr) :
def getTaskCommentsJson() : #For POST
    taskIdStr = request.form['Task_id'] # For POST
    empEmail = current_user.username.lower()
    authLevel = getAuthLevel(empEmail, False, current_user.is_admin) # Get Auth Level, OwnItem is False

    #getTaskComments is specifically written for this purpose
    commentsList = getTaskComments(int(taskIdStr), authLevel=authLevel)
    return json.dumps(commentsList)
