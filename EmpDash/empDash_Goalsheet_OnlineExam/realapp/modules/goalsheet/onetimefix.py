"""
K.Srinivas, 6-12-2018

Project: Goal Sheet
Description: As we implement weights, scores, etc. one-time fix is needed for goal-sheet data.
This method is meant only for single-use activities.

TODO: 
a) Copy Weights to Goals
b) All Dates: 2019 to be changed to 31st Dec 2018
c) Assessing Managers: Update as per HRMS
d) In TASK-ADD/Delete: Add logic for weight update

KNOWN BUGs: None
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
from hrmsdomain import getReportingManagerEmpNum
from feedbackmodel import GoalFeedback

FIXDATE=True
FIXWEIGHT=True
FIXTASKS=True
FIXASSIGNMENT=True
FIXTEST=True

#Onetime Fix for Pending-2ndLevel .vs. Pending-MGMT.
#The bug-related to this one is unclear. As a quick-fix, all goal-sheets in Pending-2ndLevel will be changed to Pending-MGMT if the 2nd level
# has Auth-Level=3 (Sridhar/Sriram)
@app.route('/goals/fixpendingmgmt', methods=('GET', ))
@login_required 
def fixPendingMgmt(year = '2018-2019') :    
    empEmail = current_user.username.lower()
    if not current_user.is_admin :
        return render_template('goalsheet/message.html', message = "You are not authorized to execute one-time-fix.")
    #get all Goal-Sheets
    gsList = getGoalSheetsAll(year) 
    for gs in gsList :
        if gs.status == 'Pending-2ndLevel' : # If sheet is in pending2nd level
            #Get 2nd Level (how?)
                emp2nd = get2ndLineManager(gs.empId)
                srisri = int(emp2nd.EMPLOYEE_ID) # Check if sridhar or sriram
            #If 2nd Level auth-level = 3
                if srisri == 113 or srisri == 14 :
                    print ("GS:%d, %d, %d" % (gs.empId, gs.assessingManager, srisri))
                    #gs.status = 'Pending-MGMT'
                    #db.session.commit()
                else :
                    print ("NOT SRISRI GS:%d, %d, %d" % (gs.empId, gs.assessingManager, srisri))
    return ("Done check console")


@app.route('/goals/fixSridharEmpId', methods=('GET', ))
@login_required 
def fixSridharEmpId(year = '2018-2019') :    
    empEmail = current_user.username.lower()
    if not current_user.is_admin :
        return render_template('goalsheet/message.html', message = "You are not authorized to execute one-time-fix.")
    #get all Goal-Sheets
    gsList = getGoalSheetsAll() 
    for gs in gsList :
        if gs.assessingManager == 75 : # If sridhar is the assessing manager
            print("Updating Sridhar's empNum for Goal-Sheet:" + str(gs.empId) + ":" + str(gs.id) )
            if not FIXTEST :
                gs.assessingManager =  113 #Update it
    db.session.commit()
    #Get all feedback items
    gflRecv = GoalFeedback.query.filter_by(receiverEmpId = 75).all() 
    for fdb in gflRecv :
        print("Updating Sridhar's empNum for Feedback-giver:" + str(fdb.giverEmpId) + ":" + str(fdb.id) )
        if not FIXTEST :
            fdb.receiverEmpId = 113  # If sridhar, update
    db.session.commit()
    gflgivr = GoalFeedback.query.filter_by(giverEmpId = 75).all() 
    for fdb in gflgivr :
        print("Updating Sridhar's empNum for Feedback-receiver:" + str(fdb.receiverEmpId) + ":" + str(fdb.id) )
        if not FIXTEST :
            fdb.giverEmpId = 113  # If sridhar, update
    db.session.commit()
    #get all ask-For-Feedback
    #Not required, we use e-mail ID and not empID :-)
    return ("Done, please check console")


@app.route('/goals/onetimefix', methods=('GET', 'POST'))
@login_required 
def oneTimeFix(year = '2018-2019') :    
    #This method has done its job, prevent accidental run
#    return  "Blocked from further use"      
    #Get Info for the top-part : Emp-Name, number, Role, Designation, Department, Manager, IS_DC_LEAD?
    empEmail = current_user.username.lower()
    if not current_user.is_admin :
        return render_template('goalsheet/message.html', message = "You are not authorized to execute one-time-fix.")
    #get all Goal-Sheets
    # if not FIXTEST :
    #     gsList = getGoalSheetsAll() 
    # else :
    #     gsList = getGoalSheetsForDc('divakara.gajulapalli@msg-global.com') #For testing only
    #For each goal-sheet
    gst = getGoalSheetById(1333)
    gsList = [gst]
    for gs in gsList :

        print("Processing GS-ID:" + str(gs.id))
        if FIXASSIGNMENT :
            pass
            #Get HRMS-Reporting Manager ID
            managerID = getReportingManagerEmpNum(gs.empId)
            if not managerID :
                print("Reporting Manager Not found for Emp with ID:" + str(gs.empId))
            else :
                #Update Goal-Sheet assessing manager to the reporting manager
                gs.assessingManager = managerID

        sheetWeight = 0
        tId = gs.templateId # 1 for Emp, 2 for DC, others we don't know
    #get all goals, Sections
        (sheet, allgoalsections , allgoals) = getAllGoalsAndSectionsInSheet(gs)
    #For each goal (this comes in sections)
        for gSecIndx, goalsInSections in enumerate(allgoals) :
#            print("Processing SecInd:" + str(gSecIndx))
            sectionWeight = 0
            for g in goalsInSections :               
#                print("Processing goal:" + str(g.title))
                if FIXDATE : fixItemEndDate(g)
            #Update weight
                mg = getMasterGoalById(g.masterGoalId)
                if FIXWEIGHT :
                    if tId == 1 :
                        g.weight = mg.weight1 
                    elif tId == 2 :
                        g.weight = mg.weight2 
                    else :
                        g.weight = 0
#                    print("g.weight" + str(g.weight))
                    sheetWeight += g.weight
                    sectionWeight += g.weight
                #Else : 
                tList = getAllTasksInGoal(g.id)
                numTasks = len(tList)
                #Look at the number of tasks
                #Assign goal-weight/n to each task # What happens if a person adds a task AFTER the this one-time?
                if numTasks :
#                    print("" + str(numTasks))
                    if FIXWEIGHT : perTaskWeight = g.weight/numTasks
                else :
                #Check if even one task does'nt exist, add a task and assign full weight of the goal to the task
                    if FIXTASKS :
                        obj = createTask(g, cstatus = "Default")
                        obj.description = "Default Task:" + g.title
                        obj.score = 0
                        db.session.add(obj)
#                        print("Create Task:" + str(g.description))
                        tList.append(obj)
                    if FIXWEIGHT : perTaskWeight = g.weight
                #Update Weights for tasks
                for t  in tList :
                    if FIXDATE :  fixItemEndDate(t)
                    if FIXWEIGHT : t.weight = perTaskWeight
                db.session.commit()    #Doing one commit per sheet
        #For each goal-section:
            gSec = allgoalsections[gSecIndx]
            gSec.weight = sectionWeight
    #Get all goals, add-up the weights, update
        if FIXWEIGHT : gs.maxscore = sheetWeight
        db.session.commit()    #Doing one commit per sheet

    return render_template('goalsheet/message.html', message = "One-Time Fix ran successfully.")

#Goal or Task: dateEnd will be updated to 31Dec2018
def fixItemEndDate(gORt) : 
    calEndDate = dt.datetime(2018,12,31)
    if gORt.dateEnd > calEndDate :
        gORt.dateEnd = calEndDate
    return



@app.route('/goals/fixmgrs', methods=('GET', 'POST'))
@login_required 
def fixAssessingMgr(year = '2019') :    
    #This method has done its job, prevent accidental run
#    return  "Blocked from further use"      
    #Get Info for the top-part : Emp-Name, number, Role, Designation, Department, Manager, IS_DC_LEAD?
    empEmail = current_user.username.lower()
    if not current_user.is_admin :
        return render_template('goalsheet/message.html', message = "You are not authorized to execute one-time-fix.")
    #get all Goal-Sheets
    gsList = getGoalSheetsAll(year) 
    for gs in gsList :

        print("Processing GS-ID:" + str(gs.id))
        managerID = getReportingManagerEmpNum(gs.empId)
        if not managerID :
            print("Reporting Manager Not found for Emp with ID:" + str(gs.empId))
        else :
            #Update Goal-Sheet assessing manager to the reporting manager
            gs.assessingManager = managerID
        db.session.commit()
    return "Update completed"