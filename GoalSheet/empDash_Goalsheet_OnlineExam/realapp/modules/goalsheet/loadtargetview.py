"""
K.Srinivas, 12-Jun-2018

Project: BCS Projects
Description: This is special one-time use program to upload "targetSet" field from XLS-files to the goals
Approach is as follows:
a) loadfromxls.py handles all the XLS-file reading part, from hard-coded directory structure
b) This application calls methods from loadfromxls and updates the goals in DB by referring HRMS-emp-data
c) This is written to be incrementally re-executable. Once processed, the goal-sheet XLS is moved to "processed".
    Re-executing with the same data causes goal-sheets to be deleted and re-assigned.
d) On the URL, dc=True/False and notify=True/False are evaluated and handled accordingly.

TODO: 
a) Implement "notify=True/False".
b) need to re-excute for final run with notify=True

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
from goaldomain import deleteGoalSheet, assignTemplate, getAllGoalsAndSections, createTask
from notification import notify

#Temp, ONE-TIME use Target for uploading Targets-Set from XLS-files to DB
#Lot of Hard-Coding, not expected to be used more than once
@app.route('/goals/uploadtargets', methods=['GET'])
def uploadTargets() :
    dc = request.args.get('dc')
    print("dc=" + dc)
    dc = eval(dc)
    #Read and process all files, link to HRMS data
    (flist, empList, valDictList) = getValidatedList(dc)
    ## Now we have empNo both in File and HRMS
    print("Processing %d employees..." %(len(flist)))
    for i in range(0, len(flist) )  : # Loop through all legitimate entries
        #Delete goal-sheet if it exists
#        print("Deleting...")
        deleteGoalSheetIfPresent(empList[i])
        #Select Template (dc=True)
        tempId = 1 # Line Employees
        if dc : tempId = 2 # DC Leads
        #Assign goal-sheet
        managerEmail ="srinivas.kambhampati@msg-global.com" # Assigning manager
#        print("Assigning...")
        assignTemplate(empList[i].OFFICE_EMAIL_ID, tempId, managerEmail, '2018-2019', notify=False)
        #Update target-set from valDict
        #get the goals
        (sheet, allgoalsections , allgoals) = getAllGoalsAndSections(empList[i].EMPLOYEE_ID, '2018-2019')
        if not allgoals:
            app.logger.info("No Goals, something went wrong:" + flist[i])
            continue
        if sheet :
            goalSheetId =  sheet.id
        else :
            app.logger.info("No Goalsheet, something went wrong:" + flist[i])
            continue
        print("Updating targets in:" + flist[i])
        for gs in allgoals : #set the target for each goal
            for g in gs :
                gid = g.id
                tarSet = valDictList[i][g.templateId] # Template ID is the Master-Goal ID
                if tarSet:
                    tarSet = str(tarSet)
                    g.targetSet =tarSet[0:498] # Limit it to first 500 Chars, ignore the rest.(Only Rahul)
                    # Add targetSet as a task [Feedback from Sridhar]
                    db.session.add(createTask(g, desc =tarSet[0:998] ,  cstatus = "Approved"))
        db.session.commit() # Save all goals
        moveFileToProcessed(flist[i], dc)
    return str(flist)

#If a goal-sheet/goal exists for a person, delete it, recursively.
def deleteGoalSheetIfPresent(emp) :
    deleteGoalSheet(emp.OFFICE_EMAIL_ID) # Simply ignore the return string
    return

def getValidatedList(dc) :
    flist = readGoalFiles(dc)
    retList = []
    retEmpList = []
    valDictList = []
    app.logger.info("processing %d files..." % (len(flist)))
    for goalFile in flist :
        (valDict, empNo) = readGoalSheetFile(goalFile, dc)
        if empNo :
            #Get emp Object?
            emp = getEmployeebyId(empNo)
            if not emp :
                print("File %s : Emp. not in HRMS:%s" % (goalFile, empNo))
                continue
        else :
            print("No emp. no in file:%s" % (goalFile))
            continue
        retList += [goalFile]
        retEmpList += [emp]
        valDictList += [valDict]
    return (retList, retEmpList, valDictList)


#To notify ALL employees once again that a goal-sheet is assigned to them
from emailstrings import *
@app.route('/goals/resendnotification', methods=['GET'])
def notifyAllGoalSheet() :
    empMessage =  goalAssignResend %('2018-2019') 
    gsList = getGoalSheetsAll()
    for sheet in gsList:
        eid =  str(sheet.empId)

        emp = getEmployeebyId(sheet.empId)
        if emp :
            empEmail = emp.OFFICE_EMAIL_ID
            print("Notifying:" + str(empEmail))
            notify(empEmail,goalEmailSubject, empMessage ,  templateId="-1")
    return("Done")

    