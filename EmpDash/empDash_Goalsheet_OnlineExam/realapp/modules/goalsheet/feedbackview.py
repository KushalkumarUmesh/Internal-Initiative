"""
K.Srinivas, 18-Jul-2018

Project: Goal Sheet
Description: 

KNOWN BUGs: None
"""
import logging
import json
from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import required, DataRequired, Length
from flask_login import login_required, current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash, session
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
from feedbackdomain import *
from feedbackmodel import *


##########################################################################################################################
#### Display/Edit Goal-Sheet for end user ##############################
#Key screen allowing an employee to see this goals, set-his targets and send for approval
#Once Approved, He/She can only update tasks
@app.route('/goals/feedbackviewmanager', methods=['GET'])
@login_required  #Without login, we don't know who it is
def feedbackViewManager( year = '2018-2019') :
    year = session['year']
    if not current_user.is_admin and not current_user.is_dclead and not current_user.is_Manager :
        return render_template('goalsheet/message.html', message = "You are not authorized to access this page.")
    loggedInEmpEmail = current_user.username.lower()
    loggedInEmpId = getEmpIdIntByEmail(loggedInEmpEmail)

    empIdStr = request.args.get('empid')        
    if empIdStr and empIdStr.isdigit() : # If employee ID was  n
        empId = int(empIdStr)
    else :
        return render_template('goalsheet/message.html', message = "Internal Error.Please contact support with this message: Invalid empIdStr:" + str(empIdStr))
    return feedbackViewGeneric(empId,loggedInEmpId, loggedInEmpEmail,\
     current_user.is_admin , year, managerPage=True)


@app.route('/goals/feedbackview', methods=['GET'])
@login_required  #Without login, we don't know who it is
def feedbackView( year = '2018-2019') :
    year = session['year']

    loggedInEmpEmail = current_user.username.lower()
    loggedInEmpId = getEmpIdIntByEmail(loggedInEmpEmail)
    return feedbackViewGeneric(loggedInEmpId,loggedInEmpId, loggedInEmpEmail, current_user.is_admin , year)

def feedbackViewGeneric(empId,loggedInEmpId, loggedInEmpEmail,is_admin, year, managerPage=False ) :
    loginedInEmpId = getEmpIdIntByEmail(loggedInEmpId)
    empDict = getEmpDictbyEmpid(str(empId))
    empEmail = empDict['OFFICE_EMAIL_ID']

    #Get list of Goals, group-by-sectio
    (sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
    # Get All the Tasks for these goals, grouped nicely by goal-ID
    if not sheet :
        return render_template('goalsheet/message.html', message = "No Goals have been Assigned. Please contact your DC Lead.")
    msgDict = getEmpDictbyEmpid(sheet.assessingManager)

    empInfo = getGoalSheetHeader(empEmail, year)
    empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
        
    alltasks = getAllTasks(allgoals)

    #Set Authorization level = Check if its own item or someone else
    ownItem = False
    if (loginedInEmpId == sheet.empId) :
        ownItem = True
    authlevel = getAuthLevel(loggedInEmpId, ownItem, is_admin) # Get Auth Level
    #getComments
    (allSheetComments, allGoalComments, allTaskComments) = getAllComments(empId,sheet, allgoals, alltasks, authLevel = authlevel)
    #Render
    template = 'goalsheet/goalfeedback.html'
    if managerPage :  template = 'goalsheet/goalfeedbackmanager.html'
    return render_template(template, goalSheet = sheet,\
        goalSections = allgoalsections, \
        goals = allgoals, alltasks=alltasks, empInfo = empInfo, \
        sheetCmnts = allSheetComments, goalCmnts = allGoalComments, \
        taskCmnts = allTaskComments, num=len(allgoalsections))




#TODO: Visibility LEVEL needs to be implemented. For now, emp-visibility needs to be True
@app.route('/goals/getTaskEmpFeedback', methods=['GET'])
@login_required  #Without login, we don't know who it is
def getTaskEmpFeedback(year = '2018-2019') :
    year = session['year']

    empEmail = current_user.username.lower()
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
#    print("loginedInEmpId:" + str(loginedInEmpId))
    taskIdStr = request.args.get('Task_id')
    if taskIdStr.isdigit() :
        tId = int(taskIdStr)
    else:
        return ("Invalid Task")
    alltfs = GoalFeedback.query.filter_by(elementId = tId). \
                filter_by(visibleToEmp = True). \
                filter_by(elementType = 3). \
                all()
#    print("No. of comments: " + str(len(alltfs)))
    mydict = {str(o.id) : (o.dateRecorded.strftime("%d-%m-%y") , o.feedback) for o in alltfs }
#    print(mydict)
    return (json.dumps(mydict))
 

##################################################################################################
##################################################################################################
# To be deleted later after testing -Srini
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
# @app.route('/goals/xxxfeedbackview', methods=['GET'])
# @login_required  #Without login, we don't know who it is
# def xxxfeedbackView( year = '2018-2019') :
#     empIdStr = request.args.get('empid')        
#     if empIdStr and empIdStr.isdigit() : # If employee ID was  n
#         empDict = getEmpDictbyEmpid(empIdStr)
#         empEmail = empDict['OFFICE_EMAIL_ID']
#     else :
#         empEmail = current_user.username.lower()
#     empInfo = getGoalSheetHeader(empEmail, year)
#     empId = str(empInfo['EmployeeID'])

#     #Get list of Goals, group-by-sectio
#     (sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
#     # Get All the Tasks for these goals, grouped nicely by goal-ID
#     if not sheet :
#         return render_template('goalsheet/message.html', message = "No Goals have been Assigned. Please contact your DC Lead.")
#     msgDict = getEmpDictbyEmpid(sheet.assessingManager)
#     empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
        
#     alltasks = getAllTasks(allgoals)

#     #Set Authorization level = Check if its own item or someone else
#     ownItem = False
#     loginedInEmpId = getEmpIdIntByEmail(empEmail)
#     if (loginedInEmpId == sheet.empId) :
#         ownItem = True
#     authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
#     #getComments
#     (allSheetComments, allGoalComments, allTaskComments) = getAllComments(loginedInEmpId,sheet, allgoals, alltasks, authLevel = authlevel)
#     #Render
#     return render_template('goalsheet/goalfeedback.html', goalSheet = sheet,\
#         goalSections = allgoalsections, \
#         goals = allgoals, alltasks=alltasks, empInfo = empInfo, \
#         sheetCmnts = allSheetComments, goalCmnts = allGoalComments, \
#         taskCmnts = allTaskComments, num=len(allgoalsections))

# @app.route('/goals/xxxfeedbackviewmanager', methods=['GET'])
# @login_required  #Without login, we don't know who it is
# def xxxfeedbackViewManager( year = '2018-2019') :
#     loggedInEmpEmail = current_user.username.lower()

#     empIdStr = request.args.get('empid')
        
#     if empIdStr and empIdStr.isdigit() : # If employee ID was  n
#         empDict = getEmpDictbyEmpid(empIdStr)
#         empEmail = empDict['OFFICE_EMAIL_ID']
#     else :
#         return ("error")
#     empInfo = getGoalSheetHeader(empEmail, year)
#     empId = str(empInfo['EmployeeID'])
# #    print("empId = " + empId)
#     #Get list of Goals, group-by-sectio
#     (sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
#     # Get All the Tasks for these goals, grouped nicely by goal-ID
#     if not sheet :
#         return render_template('goalsheet/message.html', message = "No Goals have been Assigned. Please contact your DC Lead.")
#     msgDict = getEmpDictbyEmpid(sheet.assessingManager)
#     empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
        
#     alltasks = getAllTasks(allgoals)
#     #Set Flags
#     #Set Authorization level = Check if its own item or someone else
#     ownItem = False
#     loginedInEmpId = getEmpIdIntByEmail(loggedInEmpEmail)
#     if (loginedInEmpId == sheet.empId) :
#         ownItem = True
#     authlevel = getAuthLevel(loginedInEmpId, ownItem, current_user.is_admin) # Get Auth Level
#     print("getAuthLevel:" + str(authlevel))
#     (allSheetComments, allGoalComments, allTaskComments) = getAllComments(int(empIdStr),sheet, allgoals, alltasks, authLevel = authlevel)
#     #Render
#     return render_template('goalsheet/goalfeedbackmanager.html', goalSheet = sheet,\
#         goalSections = allgoalsections, \
#         goals = allgoals, alltasks=alltasks, empInfo = empInfo, \
#         sheetCmnts = allSheetComments, goalCmnts = allGoalComments, \
#         taskCmnts = allTaskComments, num=len(allgoalsections))

