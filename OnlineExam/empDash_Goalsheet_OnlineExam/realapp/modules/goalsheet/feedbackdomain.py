"""
K.Srinivas, 09-Jul-2018

Project: Goal Sheet
Description: These are the domain methods for the Goal Sheet Feedback. 

TODO: 
a) Use and Test these methods. These expected to be called from a VIEW via AJAX calls
b) 12-Dec: Update getAllComments to respect the visibility and authLevel flags
KNOWN BUGs: None
"""
from feedbackmodel import *
import datetime as dt
import goaldomain # getGoalSheet
from notification import notify
from hrmsdomain import getEmployeeEmail
from hrmsempdata import getEmployeeNameById, getEmpDictbyEmail,getEmpDictbyEmpid
from emailstrings import *
from realapp import db, ELEMENT_TYPE_SHEET, ELEMENT_TYPE_GOAL, ELEMENT_TYPE_TASK
from askfeedbackdomain import allAsksForUserByTaskId, allAsksByTaskId
from sqlalchemy.sql.expression import or_

def getAllComments(loginedInEmpId,sheet, allgoals, alltasks, visibleToEmp=True, authLevel=0) :
    allSheetComments = dict()
    allGoalComments = dict()
    allTaskComments = dict()
    #print("AuthLevel=" + str(authLevel))
    #print("loginedInEmpId=" + str(loginedInEmpId))
    allSheetComments = getGoalFeedback(loginedInEmpId,visibleToEmp,authLevel, sheet.id, ELEMENT_TYPE_SHEET)
    for sfs in allSheetComments :
        sfs.commentorName = getEmployeeNameById(sfs.giverEmpId)

    for gg in allgoals :
        for g in gg :
            gId = g.id
            allgfs = getGoalFeedback(loginedInEmpId,visibleToEmp,authLevel, gId,ELEMENT_TYPE_GOAL)
            for gfs in allgfs :
                gfs.commentorName = getEmployeeNameById(gfs.giverEmpId)
            allGoalComments[gId] = allgfs

    for k in alltasks.keys() :
        for t in alltasks[k] :
            tId = t.id
            alltfs = getGoalFeedback(loginedInEmpId,visibleToEmp,authLevel, tId,ELEMENT_TYPE_TASK)
            for tfs in alltfs :
                tfs.commentorName = getEmployeeNameById(tfs.giverEmpId)
            allTaskComments[tId] = alltfs
#        print("ALlTasks:" + str(allTaskComments) + len(alltfs) + ":" + str(tId)) 

    #  Add Ask Feedback Comments here to allTaskComments[tId]
            #Get e-mail from loginedInEmpId
            receiverEmail = getEmployeeEmail(loginedInEmpId)
            #get all Asks for this task - allAsksForUser(receiverEmail, year)
            allAsks =  allAsksForUserByTaskId(receiverEmail, sheet.assessmentYear, tId, authLevel=authLevel)
            for ask in allAsks :
                #Create a new GoalFeedback object (name, value pair)
                gfb = GoalFeedback()
                #get commentorName
                giverEmpDict = getEmpDictbyEmail(ask.giverEmail)
                if giverEmpDict :
                    gfb.commentorName = giverEmpDict["FIRST_NAME"] + " " + \
                        giverEmpDict["LAST_NAME"] 
                else :
                    gfb.commentorName = "Unknown"
                gfb.commentorName += ":" + ask.relationship       
                # Copy role:feedback, date
                gfb.feedback =  ask.feedback
                gfb.dateRecorded = ask.dateRecorded
                #Add the object to allTaskComments
                allTaskComments[tId].append(gfb)

    return (allSheetComments, allGoalComments, allTaskComments)
    
#Convenience Method for getting all comments
def getGoalFeedback(receiverEmpId,visibleToEmp,authLevel, elementId,elementType) :
    if visibleToEmp :
        gfl = GoalFeedback.query.filter_by(receiverEmpId = receiverEmpId). \
                filter_by(visibleToEmp = True ). \
                filter_by(elementId = elementId). \
                filter_by(elementType = elementType). \
                all() 
    else :
        gfl = GoalFeedback.query.filter_by(receiverEmpId = receiverEmpId). \
                filter( GoalFeedback.visiblityLevel <=  authLevel). \
                filter_by(elementId = elementId). \
                filter_by(elementType = elementType). \
                all() 
    return gfl

#Convenience Method for getting all comments
def getTaskFeedbackAtAuthLevel(receiverEmpId,authLevel, elementId) :
    gfl = GoalFeedback.query.filter_by(receiverEmpId = receiverEmpId). \
            filter( GoalFeedback.visiblityLevel ==  authLevel). \
            filter_by(elementId = elementId). \
            filter_by(elementType = ELEMENT_TYPE_TASK). \
            all() 
    return gfl

#Most Basic method for recording feedback
def recordSheetFeedback(sheet, feedback, visibleToEmp = True,visiblityLevel=0 , \
    dateRecorded = 0 ,  giverEmpId = 0  ) :

    gs = sheet
    elementType = 1 # Goal-Sheet
    elementId = sheet.id # Goal-Sheet
    receiverEmpId = gs.empId

    if not giverEmpId :
        giverEmpId = gs.assessingManager

    if not dateRecorded :
        dateRecorded = dt.datetime.now()

    assessmentYear= gs.assessmentYear
    
    recordFeedback(elementId, elementType, giverEmpId, receiverEmpId,feedback,\
          dateRecorded,  visibleToEmp = visibleToEmp, visiblityLevel = visiblityLevel, assessmentYear = assessmentYear)
    return

def recordGoalFeedback(goal, feedback, visibleToEmp = True, visiblityLevel=0 , \
    dateRecorded = 0, giverEmpId = 0) :
    gs = goaldomain.getGoalSheet(goal.goalSheetId)

    elementType = 2 # Goal
    elementId = goal.id # Goal-Sheet
    receiverEmpId = gs.empId

    if not giverEmpId :
        giverEmpId = gs.assessingManager

    if not dateRecorded :
        dateRecorded = dt.datetime.now()

    assessmentYear= gs.assessmentYear


    recordFeedback(elementId, elementType, giverEmpId, receiverEmpId,feedback,\
          dateRecorded,  visibleToEmp = visibleToEmp, visiblityLevel = visiblityLevel, assessmentYear = assessmentYear )

    return

def recordTaskFeedback(task, feedback, visibleToEmp = True, visiblityLevel=0 , \
    dateRecorded=0 , giverEmpId = 0) :
    gs = goaldomain.getGoalSheet(task.goalSheetId)
    elementType = 3 # Task
    elementId = task.id # Goal-Sheet
    receiverEmpId = gs.empId

    if not giverEmpId :
        giverEmpId = gs.assessingManager

    if not dateRecorded :
        dateRecorded = dt.datetime.now()

    assessmentYear= gs.assessmentYear


    recordFeedback(elementId, elementType, giverEmpId, receiverEmpId,feedback, dateRecorded, \
        visibleToEmp,visiblityLevel , assessmentYear)
    return



#Most Basic method for recording feedback
def recordFeedback(elementId,elementType,giverEmpId,receiverEmpId,feedback, dateRecorded, \
    visibleToEmp = True, visiblityLevel=0 , \
    assessmentYear='2018-2019'    ) :
#    assessmentYear = session['year'] #This needs to be seen
    gf = GoalFeedback()
    gf.elementId = elementId
    gf.elementType = elementType

    gf.giverEmpId = giverEmpId
    gf.receiverEmpId = receiverEmpId
    gf.feedback = feedback[0:999]

    gf.visibleToEmp = visibleToEmp
    gf.visiblityLevel = visiblityLevel
    
    gf.dateRecorded = dateRecorded
    gf.assessmentYear = assessmentYear

    db.session.add(gf)
    db.session.commit()
    return gf

#Get all the comments for at task, limited to Authlevel
#for use during assessment phase
def getTaskComments(taskId, authLevel) :
    #All Task Comments
    retList = []
    #Get Task Activity
    task = goaldomain.getTaskById(taskId)
    activity = "None"
    if task.personalNotes :
        activity = task.personalNotes
    if task :
        fbObj = {'name':'Activity', 'feedback':activity, 'date':task.dateEnd.strftime('%m-%d-%y') }
        retList.append(fbObj)
    else :
        fbObj = {'name':'Activity', 'feedback':"Error Task Not found" + str(taskId), 'date':"Not Found" }
        retList.append(fbObj)
    
    gfl = GoalFeedback.query.filter_by(elementId = taskId). \
            filter( GoalFeedback.visiblityLevel <=  authLevel). \
            filter_by(elementType = ELEMENT_TYPE_TASK). \
            all() 

    #Convert into a serializable list
    for f in gfl :
        giverEmpDict = getEmpDictbyEmpid(f.giverEmpId)
        if giverEmpDict :
            commentorName = giverEmpDict["FIRST_NAME"] + " " + \
                giverEmpDict["LAST_NAME"] 
        else :
            commentorName = "Unknown"
        fbObj = {'name':commentorName, 'feedback':f.feedback, 'date':f.dateRecorded.strftime('%m-%d-%y') }
        retList.append(fbObj)
    #All Ask-For-Feedbacks
    allAsks = allAsksByTaskId(taskId,visibleToEmp=True,authLevel=authLevel )
    #Process Ask-For-Feedbacks into GoalFeedback Objects for display
    for ask in allAsks :
        #get commentorName
        giverEmpDict = getEmpDictbyEmail(ask.giverEmail)
        if giverEmpDict :
            commentorName = giverEmpDict["FIRST_NAME"] + " " + \
                giverEmpDict["LAST_NAME"] 
        else :
            commentorName = "Unknown"
        commentorName += ":" + ask.relationship

        fbObj = {'name':commentorName, 'feedback':ask.feedback, 'date':ask.dateRecorded.strftime('%m-%d-%y') }
        #Add the object to allTaskComments
        retList.append(fbObj)


    return retList
