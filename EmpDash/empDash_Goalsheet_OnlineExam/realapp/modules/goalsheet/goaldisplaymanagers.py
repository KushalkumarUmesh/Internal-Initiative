"""
K.Srinivas, 17-Dec-2018

Project: Goal Sheet
Description: goaldisplay.py has become too long. The file is being split into this one and all
views related to managers/admin,etc. are being moved here 

TODO: 
TASK:


KNOWN BUGs: 
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
from realapp import app, db, cache
from goaldomain import *
import os
from hrmsdomain import *
import datetime as dt
from dateutil import parser
from goalflags import * 
from hrmsempdata import getEmpDictbyEmail, getEmpDictbyEmpid
from feedbackdomain import getGoalFeedback, getTaskFeedbackAtAuthLevel

#NOT USED anymore, need to remove references
class SelectReporteeForm(FlaskForm) :
    reportee =  SelectField(u'Select reportee', choices=[], default ='' )
    selected = SubmitField('View Goals') #   
    comments = StringField(u'Comments', validators=[DataRequired(), Length(max=200)],  widget=TextArea() )
    rejectComments = StringField(u'Comments', validators=[DataRequired(), Length(max=200)],  widget=TextArea() )
    approve = SubmitField('Approve') #   
    reject = SubmitField('Return to Employee') #   


#Display Employee Goal Sheet to the manager
@app.route('/goals/goalsheetsformanager', methods=('GET', 'POST'))
@app.route('/goals/goalsheetsformanager/<emailId>', methods=('GET', 'POST'))
@login_required  #Without login, we don't know who it is
def goalSheetForManager(emailId="", year = '2018-2019') :     #Lets not take assessment year for now, but we default it nicely
    year = session['year']

    #Get Info for the top-part : Emp-Name, number, Role, Designation, Department, Manager, IS_DC_LEAD?
    empEmail = current_user.username.lower()
    user = current_user.username

    # Give Drop down of the employees with this person as the assessing manager
    form = SelectReporteeForm(request.form)
    if current_user.is_admin :
        form.reportee.choices = getEmailSetForSelect()  + [("","")] # Fill in e-mails
    elif current_user.is_dclead : # must be a DC-Lead
        form.reportee.choices = getEmpSetForSelect(user)  + [("","")] # Fill in e-mails
    elif current_user.is_Manager : # must be a DC-Lead
        form.reportee.choices = get1stLevelReporteesForSelect(user)  + [("","")] # Fill in e-mails
    else :
        return render_template('goalsheet/message.html', message = "You are not authorized to view others goals.")

    if emailId : #this is not blank
        user = emailId
        form.reportee.default= user

    comments = ""
    approved = False
    rejected = False
    if request.method == 'POST' :
        if 'selected' in request.form.keys():
            user = form.reportee.data.lower()
        elif 'approve' in request.form.keys() :
            approved = True            
#            user = form.reportee.data.lower()
            user = emailId
            comments = form.comments.data
        elif 'reject' in request.form.keys() :
            comments = form.rejectComments.data
#            user = form.reportee.data.lower()
            user = emailId
            if (not comments) or (not comments.strip() ):
                flash("Comments are Mandatory when returning a Goal Sheet.")
            else :
                rejected = True                        

    form.comments.data = "" # Reset the form in case this is not a POST
#    print("User=" + user)
    empInfo = getGoalSheetHeader(user, year)
    empId = str(empInfo['EmployeeID'])
    #Get list of Goals, group-by-sectio
    ( sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
    if not sheet :
        return render_template('goalsheet/message.html', message = "No goal sheet found for employee:" + user)
    # Get All the Tasks for these goals, grouped nicely by goal-ID
    msgDict = getEmpDictbyEmpid(sheet.assessingManager)
    empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
    alltasks = getAllTasks(allgoals)
    #Set Flags
    ownItem = False
    empEmail = current_user.username.lower() # 2nd time?
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == sheet.empId) :
        ownItem = True
    authlevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level
    mgmtLevel = getMgmtRelationship(sheet, empEmail, loggedInEmpId=loginedInEmpId  )
#    app.logger.info("Auth:" + str(authlevel) + ":" + str(ownItem))
    if approved :
        flash(approveGoalSheet(comments, sheet, mgmtLevel) )
        db.session.commit()
    if rejected :
        flash(returnGoalSheet(comments, sheet, mgmtLevel) )
        db.session.commit()

    setGoalSheetFlags(sheet,alltasks, authlevel) # Set Goal-Level flags
    setAllGoalsFlags(allgoals,authlevel) # Set Goal-Level flags
    setAllTasksFlags(alltasks,authlevel) # Set Task-level Flags
    #Render
    return render_template('goalsheet/managersheetshow.html', goalSheet = sheet,goalSections = allgoalsections, \
        goals = allgoals, alltasks=alltasks, form = form, empInfo = empInfo, num=len(allgoalsections), emp_level=(mgmtLevel >= 2) )


@app.route('/goals/goalsheetsformanager_reportees', methods=('GET', 'POST'))
@login_required  
def goalSheetsForManagerReportees(year = '2018-2019') :
    year = session['year']

    empEmail = current_user.username.lower()
    user = current_user.username
    authlevel = getAuthLevel(empEmail, False, current_user.is_admin) # Get Auth Level

    #SRINI: Switched from checking if admin/DC-Lead/1st Manager to auth-level
    if current_user.is_admin :
        gsList = getGoalSheetsAll(year) #All goal-sheets
    elif authlevel == 3 :
        gsList = getGoalSheetsAll(year) #All goal-sheets , Sridhar, Sriram and Suresh can see/act on all goal sheets ALL goal-sheets
#        gsList = getGoalSheetsForDc(empEmail) #All goal-sheets
    elif authlevel == 2 : # DC-Lead goal-sheets for this DC-Lead and 2nd level sheets
        gsList =  getGoalSheetsForDc(empEmail, year=year) #Shows Goal-sheets assigned to self and all reportees
    elif authlevel == 1: # Goal Sheets for this manager
        gsList = getGoalSheets(empEmail,year=year)
    else :
        app.logger.info("%s attempted to login as admin/manager." % (user) )
        return render_template('goalsheet/message.html', message = "You are not authorized to access this data.")

    for gs in gsList:
        msgDict = getEmpDictbyEmpid(gs.empId)
        if 'None' != msgDict :
            gs.empName =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]   
            gs.empEmail =  msgDict["OFFICE_EMAIL_ID"]
            gs.assessingManagerEmail = getEmployeeEmail(gs.assessingManager)   
        else :
            app.logger.error("Goal-sheet found for non-existing emp with ID:" + str(gs.empId))
    return render_template('goalsheet/manager_reportees.html',  gsList = gsList )

## show rating screen render################################
#@app.route('/goals/showrating', methods=('GET', ))
@app.route('/goals/showrating/<empId>', methods=('GET', ))
@login_required
def showrating(empId, year = '2018-2019') : #
    year = session['year']
    regularEmp=True
    #Get Info for the top-part : Emp-Name, number, Role, Designation, Department, Manager, IS_DC_LEAD?
    empEmail = current_user.username.lower()
    user = current_user.username
    if current_user.is_admin :
        regularEmp=False
        pass
#        gsList = getGoalSheetsAll(year) #All goal-sheets
    elif current_user.is_dclead : # DC-Lead goal-sheets for this DC-Lead and 2nd level sheets
        regularEmp=False
        pass
#        gsList =  getGoalSheetsForDc(empEmail) #Shows Goal-sheets assigned to self and all reportees
    elif current_user.is_Manager: # Goal Sheets for this manager
        regularEmp=False
        pass
#       gsList = getGoalSheets(empEmail)
    else :
        regularEmp=True #Just to be sure
        pass
        # app.logger.info("%s attempted to login as admin/manager." % (user) )
        # return render_template('goalsheet/message.html', message = "You are not authorized to access this page.")

    if empId : #this is not blank
        emp = getEmployeebyId(empId)
        if emp :
            user = emp.OFFICE_EMAIL_ID
        else :
            return render_template('goalsheet/message.html', message = "Given Employee could not be found")
    else :
        return render_template('goalsheet/message.html', message = "No user Email found in the URL")
        
    form = SelectReporteeForm() # ONLY FOR CSRF Token- FORM NOT USED

    empInfo = getGoalSheetHeader(user, year)
    empId = str(empInfo['EmployeeID'])
    #Get list of Goals, group-by-sectio
    ( sheet, allgoalsections, allgoals )  = getAllGoalsAndSections(empId, year)
    if not sheet :
        return render_template('goalsheet/message.html', message = "No goal sheet found for employee:" + user)
    # Get All the Tasks for these goals, grouped nicely by goal-ID
    msgDict = getEmpDictbyEmpid(sheet.assessingManager)
    empInfo['Manager'] =  msgDict["FIRST_NAME"] + ' ' + msgDict["LAST_NAME"]
    alltasks = getAllTasks(allgoals)
    #Set Flags
    ownItem = False
    empEmail = current_user.username.lower() # 2nd time?
    loginedInEmpId = getEmpIdIntByEmail(empEmail)
    if (loginedInEmpId == sheet.empId) :
        ownItem = True
    if regularEmp and not ownItem : #Regular employee trying to see someone else's ratings
        app.logger.info("%s attempted to view others ratings." % (empEmail) )
        return render_template('goalsheet/message.html', message = "You are not authorized to view others ratings.")
    
    authLevel = getAuthLevel(empEmail, ownItem, current_user.is_admin) # Get Auth Level

   #For each task blank-out: Name, self, 1st, DC, mgmt, pub: based on Auth level
   #Admin/Level-3 : Show Mgmt and Pub
   #Level-2: Mgmt, show DC-level
   #Level-1 : Show 1st level mgr
   #Level-0 : Show only self*
   #Create new tasks items as we cannot change the values of the objects retrieved from DB and
   #if we send the entire object, all ratings will be available to the user (though not displayeds)
    #Rating calculations
    sheetRatings = [0.0,0.0,0.0,0.0,0.0] # out of 70? Self, L1,L2,L3, Pub
    INDEX_SELF =0
    INDEX_L1 =1
    INDEX_L2 =2
    INDEX_L3 =3
    INDEX_PUB =4
    DEFAULTSTR = "NA"
    allTasksNew = dict()
    totalWeight =0.0
    for goalsInSection in allgoals : # Get each set of goals in a section
        for goal in goalsInSection : # get each goal in a set of goals for this section
            gId = goal.id
            goalWeight = goal.weight
            if goalWeight :
                totalWeight += goalWeight
#            print("goalWeight=" + str(goalWeight))
            allTasksNew[gId] = [] #Empty List
            for t in alltasks[goal.id] : #Tasks are grouped by goal-IDs
                tNew = Task()
                tNew.id = t.id
                tNew.description = t.description
                tNew.pubRating = DEFAULTSTR
                tNew.pubAssessment = DEFAULTSTR
                tNew.l3Rating = DEFAULTSTR
                tNew.l3Assessment = DEFAULTSTR
                tNew.l2Rating = DEFAULTSTR
                tNew.l2Assessment = DEFAULTSTR
                tNew.l1Rating = DEFAULTSTR
                tNew.l1Assessment = DEFAULTSTR
                tNew.selfRating = DEFAULTSTR
                tNew.selfAssessment = DEFAULTSTR
                tNew.popUpRating = DEFAULTSTR # For use in displaying the pop-up for editing
                tNew.popUpAssessment = DEFAULTSTR # For use in displaying the pop-up for editing
                if authLevel >= 3 : #Management
                    getLastAvailableRating(t, tNew,3)
                    tNew.pubRating = t.pubRating
                    tNew.pubAssessment = t.pubAssessment
                    sheetRatings[INDEX_PUB] += tNew.pubRating * tNew.pubAssessment * t.weight
                    sheetRatings[INDEX_L3] += tNew.l3Rating * tNew.l3Assessment * t.weight
                    if authLevel == 3 :
                        tNew.popUpRating =  tNew.l3Rating
                        tNew.popUpAssessment =  tNew.l3Assessment
                if authLevel >= 2 : #DC-Lead
                    getLastAvailableRating(t, tNew,2)
                    sheetRatings[INDEX_L2] += tNew.l2Rating * tNew.l2Assessment * t.weight
                    if authLevel == 2 : #DC-Lead
                        tNew.popUpRating =  tNew.l2Rating
                        tNew.popUpAssessment =  tNew.l2Assessment
                if authLevel >= 1 : #DC-Lead
                    getLastAvailableRating(t, tNew,1)
                    sheetRatings[INDEX_L1] += tNew.l1Rating * tNew.l1Assessment * t.weight
                    if authLevel == 1 : #DC-Lead
                        tNew.popUpRating =  tNew.l1Rating
                        tNew.popUpAssessment =  tNew.l1Assessment
                tNew.selfRating = t.selfRating
                tNew.selfAssessment = t.selfAssessment
                #Get the Last comment available, excluding the the self
                setLastAvailableTaskComment(sheet, t, tNew, authLevel) 
                sheetRatings[INDEX_SELF] += tNew.selfRating * tNew.selfAssessment * t.weight
                setRatingZEROToNR(tNew)
                allTasksNew[gId].append(tNew) # Add
    for i in range(len(sheetRatings)) :
        sheetRatings[i] /= 1000.0
#    print("TotalWeight=" + str(totalWeight))
    flags = getCalFlags(authLevel, sheet.status, year)
    ratingEditable = flags['gs_enable_end_year_closure']
#    for t in allTasksNew.keys() :
#        print ("Desc:" + t)
    if not authLevel :
        return render_template('goalsheet/empshowrating.html',goalSheet = sheet, goalSections = allgoalsections, \
            goals = allgoals, alltasks=allTasksNew,  empInfo = empInfo, authLevel = authLevel,\
            num=len(allgoalsections), sheetRatings= sheetRatings, totalWeight=totalWeight , form = form, ratingEditable = ratingEditable )
        
    return render_template('goalsheet/showrating.html',goalSheet = sheet, goalSections = allgoalsections, \
        goals = allgoals, alltasks=allTasksNew,  empInfo = empInfo, authLevel = authLevel,\
        num=len(allgoalsections), sheetRatings= sheetRatings, totalWeight=totalWeight , form = form, ratingEditable = ratingEditable )

#Prepopuate the ratings in the display-only task-ojbect(tNew) for each of the levels
#based on the last available value i.e. for level-3 we use Level-2 if available, else L1 if available, self if availale, in this order
#This only for showing and ensuring defaults
def getLastAvailableRating(t, tNew, authLevel) :
    if authLevel == 3 :
        tNew.l3Rating = t.l3Rating
        tNew.l3Assessment = t.l3Assessment
        if tNew.l3Rating == 0 : 
            tNew.l3Rating = t.l2Rating
            tNew.l3Assessment = t.l2Assessment
            if tNew.l3Rating == 0 : 
                tNew.l3Rating = t.l1Rating
                tNew.l3Assessment = t.l1Assessment
                if tNew.l3Rating == 0 : 
                    tNew.l3Rating = t.selfRating
                    tNew.l3Assessment = t.selfAssessment
        return
    if authLevel == 2 :
        tNew.l2Rating = t.l2Rating
        tNew.l2Assessment = t.l2Assessment
        if tNew.l2Rating == 0 : 
            tNew.l2Rating = t.l1Rating
            tNew.l2Assessment = t.l1Assessment
            if tNew.l2Rating == 0 : 
                tNew.l2Rating = t.selfRating
                tNew.l2Assessment = t.selfAssessment
        return
    if authLevel == 1 :
        tNew.l1Rating = t.l1Rating
        tNew.l1Assessment = t.l1Assessment
        if tNew.l1Rating == 0 : 
            tNew.l1Rating = t.selfRating
            tNew.l1Assessment = t.selfAssessment
        return
    return

#Set the tNew.popUpCommet to the highest-authLevel comment available, limited to the authLevel specified
#The purpose is to pre-populate the comment for the next level to edit and submit. In case its NOT edited
#the comment automatically propogates to the next level.
def setLastAvailableTaskComment(gs, t, tNew, authLevel) :
    taskId= t.id
    taskFeedbackList = None
    if not gs :
        print("No GS, something went wrong..")
        return
    if authLevel >= 3  : # If the auth-level is greater than one, get one below that level
        #First check if a comment was already given at your level
        taskFeedbackList = getTaskFeedbackAtAuthLevel(gs.empId, authLevel, taskId) # List of goal-feedbacks GoalFeedback
#        print("Getting previous feedback...found:" + str(len(taskFeedbackList)))
    if not taskFeedbackList and authLevel == 2 : #If not get it from one below
#        print("Getting authLevel == 2 feedback...")
        taskFeedbackList = getTaskFeedbackAtAuthLevel(gs.empId, authLevel, taskId) # List of goal-feedbacks GoalFeedback
    if not taskFeedbackList and authLevel == 1 : # If the auth-level is greater than one, get one below that level
#        print("Getting authLevel == 1 feedback...")
        taskFeedbackList = getTaskFeedbackAtAuthLevel(gs.empId, authLevel, taskId) # List of goal-feedbacks GoalFeedback
#   Self-Comments cannot be pre-populated as they can be many and visibility is true
    if taskFeedbackList :
        tNew.popUpComment =  taskFeedbackList[-1].feedback
#    print("Returning feedback...")

    return

#Method to set ZERO ratings to the string "NR" for display purposes only
def setRatingZEROToNR(t) :
    if not t.l1Rating :
        t.l1Rating = "NR"
    if not t.l1Assessment :
        t.l1Assessment = "NR"

    if not t.l2Rating :
        t.l2Rating = "NR"
    if not t.l2Assessment :
        t.l2Assessment = "NR"

    if not t.l3Rating :
        t.l3Rating = "NR"
    if not t.l3Assessment :
        t.l3Assessment = "NR"

    if not t.selfRating :
        t.selfRating = "NR"
    if not t.selfAssessment :
        t.selfAssessment = "NR"
    return
    