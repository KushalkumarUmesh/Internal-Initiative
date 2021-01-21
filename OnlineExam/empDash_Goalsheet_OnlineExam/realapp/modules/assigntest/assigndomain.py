"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: These are the domain methods for the Exam module. 
    a) getTests: Returns a set of lists containing Test-attributes for ALL tests.
    b) updateTest: Updates the Exam Object and all the Questions with the answers given

TODO: 
a) DONE-Move the NOTIFICATION stuff out and use the Notification module directly
b) current_user.username as passed as "assignedBy". This is currently not implemented, need to put it in
c) TEST the logic for prevention of reassignement

KNOWN BUGs: None
"""
import logging
#from realapp import db, app, testBank, csrf
import datetime as dt
from realapp import testBank
#from questionbank import  QuestionBank
from assignmodel import QuestionSet, ExamObj
from hrmsdomain import *
#import requests
from notification import getGroupSelectionList, notifyGroup, getEmailsInGroup, notify, getGroupName
from emailstrings import assignemail

#Leaving this in the assigndomain instead of calling HRMS-Domain directly, in case we use some other source in future
def getCandidateSelectionList() :
    return sorted(getEmailSetForSelect(), key=get2nd)

def get2nd(elem) :
    return elem[1]

def testAlreadyAssigned(test, email) :
    return ExamObj.query.filter_by(candiateEmail = email).filter_by(testName = test).filter_by(examStatus = 'Assigned').first()

#Called from assign assigntest, to do the test assignment
#TODO: TEST the logic for prevention of reassignement
def assignExam(obj, assignedBy) :
    if not obj.candiateEmail : # Email ID was specified
        #No group, no e-mail available
        return ("No assignments could be made as no group or individual selected")
#Prevent reassignment of the same test to the user before the 1st one is attempted
    if testAlreadyAssigned(obj.testName, obj.candiateEmail) :
        return("Test is already assigned to the candidate")

    obj.add() # Add it to the data base
    c = testBank.getQuestions(obj.testName,  exam=False) # Get a fresh set of questions.
    i =0
    while i < len(c) :  # Add each question to the DB
        qset_temp = QuestionSet(obj.examId,c.iloc[i].Question,c.iloc[i].OptionA,c.iloc[i].OptionB,c.iloc[i].OptionC, \
                    c.iloc[i].OptionD,c.iloc[i].DifficultyLevel,c.iloc[i].Correct, c.iloc[i].Description, "NA" )
        qset_temp.addNocommit()
        i += 1
    qset_temp.commit()

    #Send notification
    id=obj.examId
    retval =  notify(obj.candiateEmail,"Test:%s assigned to you." %(obj.testName), \
        assignemail % (obj.testName, obj.dtStart.strftime('%Y-%b-%d'), obj.dtDue.strftime('%Y-%b-%d'), id))
    print( assignemail % (obj.testName, obj.dtStart.strftime('%Y-%b-%d'), obj.dtDue.strftime('%Y-%b-%d'), id)) 
    #Need a nice page
    if retval :
        assignMsg = obj.candiateEmail + " has been notified."
    else :
        assignMsg = "However, " + obj.candiateEmail + " could not be notified due to an internal error."
    return ("Test assigned. %s"  % ( assignMsg))

#TODO: TEST the logic for prevention of reassignement
def assignExamToGroup(obj, assignedBy) :
    if not obj.candiateEmail : # Email ID was specified
        return("No Group Available")

    emailList = getEmailsInGroup(obj.candiateEmail)
    emailList = [ e.lower() for e in emailList ] # Convert all emails coming from group-notification server to lower-case
    numAssigned = len(emailList)

    if not numAssigned :
        return ("Group(%s) did not return any e-mails." % (obj.candiateEmail))

    numAssigned = 0 # Resetting and incrementing on each assignment. Bad-Practice, should use a different variable :-(
    for e in emailList :
    #Prevent reassignment of the same test to the user before the 1st one is attempted
        if testAlreadyAssigned(obj.testName, e) :
            continue # Silently ignore if the test is already assigne to a candidate
        numAssigned += 1
        gObj = ExamObj(testName = obj.testName)
        gObj.testName = obj.testName
        gObj.candiateEmail = e
        gObj.numQuestions =obj.numQuestions
        gObj.passNum = obj.passNum
        gObj.numAttemptsAllowed = obj.numAttemptsAllowed
        gObj.add() # Update the Exam Object
        c = testBank.getQuestions(gObj.testName,  exam=False) # Get a fresh set of questions.
        i =0
        while i < len(c) :  # Add each question to the DB
            qset_temp = QuestionSet(gObj.examId,c.iloc[i].Question,c.iloc[i].OptionA,c.iloc[i].OptionB,c.iloc[i].OptionC, \
                        c.iloc[i].OptionD,c.iloc[i].DifficultyLevel,c.iloc[i].Correct, c.iloc[i].Description, "NA" )
            qset_temp.addNocommit()
            i += 1
        qset_temp.commit() # Update the question-paper
    #Send Notification, Need to format this as a nice e-mail.
        id=obj.examId
        retval =  notify(e,"Test:%s assigned to you." %(obj.testName), \
            assignemail % (obj.testName, obj.dtStart.strftime('%Y-%b-%d'), obj.dtDue.strftime('%Y-%b-%d'), id))

    if retval :
        assignMsg = getGroupName(obj.candiateEmail) + " group has been notified."
    else :
        assignMsg = "Howevere, unfortunately, " + obj.candiateEmail + " could not be notified due to an internal error."
    return ("Test assigned to %d candidates. %s"  % (numAssigned, assignMsg))

"""
import json
from requests.auth import HTTPBasicAuth

notificationUrl = 'http://10.144.0.21:1111/'
getGroupurl = notificationUrl + 'admin/groups'
getEmailsInGroupurl = notificationUrl + 'admin/getAllEmailsInAGroup/'
sendEmailsToGroupurl = notificationUrl + 'send-email/group'

def getGroupSelectionList() :
    retList = []
    myResponse = requests.get(getGroupurl)
    if(myResponse.ok):
        jData = json.loads(myResponse.content)
        for j in jData :
            retList += [(j['groupId'], j['groupName'])]
    else :
        retList = []
    return retList


def notifyGroup(id, subject, body ) :
    headers = {'content-type': 'application/json'}
    obj =  {
            "body": body,
            "from": "onlineexam@msg-global.com",
            "groupId": id,
            "subject": subject,
            "templateId": "-1"
            }
    myResponse = requests.post(sendEmailsToGroupurl, data=json.dumps(obj), headers=headers)
    if(myResponse.ok):
        return (str(myResponse.content))
    else :
        print("Failed: " + str(myResponse.status_code))
        return (myResponse.content)
    

def getEmailsInGroup(id) :
    retList = []
    emailList = []
    myResponse = requests.get(getEmailsInGroupurl + str(id))
    if(myResponse.ok):
        jData = json.loads(myResponse.content)
        emaiList = jData['emailIds']
        groupId = jData['groupId']
        #print("emails=%s" % (emaiList))
    else :
        retList = []
    return emaiList

#    return [('group1','group1' ), ('group2','group2' ), ('group3','group3' )]
"""