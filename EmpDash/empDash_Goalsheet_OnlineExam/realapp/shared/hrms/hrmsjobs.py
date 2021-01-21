"""
K.Srinivas, 15-May-2018

Project: Scheduled Jobs related to HRMS functionality
Description: For various jobs that need to be scheduled, plan to have one "scheduler" module (in modules/home) that
will centrally schedule various jobs. The jobs themselves will be in their respective module-directories.
For HRMS, the following is the starting points:
a) Send out Happy B'day E-mail E-mail to all employees
a) Send out Congratulatory Anniversary E-mail to all employees

TODO:
a) Done:10-Jul-2018: added notifyOnDataMissing

KNOWN BUGs: None
"""
import logging
import datetime as dt
from hrmsmodels import Employee
from hrmsdomain import getAllEmployees, getReportingManagerEmpNum, getDcLeadEmpNum, getEmployeeEmail
from realapp import app, db
from notification import *
from emailstrings import *
from hrmsempdata  import sendDataMissingMsgToAll

#For calling notifyOnDate without any parameters from Scheduler
def notifyOnBirthDate() :
    return notifyOnDate(dateType="BDAY", ESC=0)

#For calling notifyOnDate without any parameters from Scheduler
def notifyOnWorkAnniversary() :
    return notifyOnDate(dateType="ANIV", ESC=0)

def notifyOnDataMissing() :
    retStr = sendDataMissingMsgToAll(sendEmailToEmp=True)
    db.session.close()
    return retStr

#Generic notifier by checking a date: Hapyy B'day, Anniversary, Passport Expiry, etc...
#BDAY=Birthday, ANIV= Anniversary
def notifyOnDate(dateType, ESC=0) :
    level1 = dict() # Collect lists for summary e-mail
    today = dt.date.today()
    if (dateType == 'BDAY') :
        body = bdayBody; subject = bdaySubject
        mBody = bdayManagerBody ; mSubject = bdayManagerSubject

    if (dateType == 'ANIV') :
        body = aniversaryBody; subject = aniversarySubject
        mBody = aniverasaryManagerBody; mSubject = aniverasaryManagerSubject

    #get all emps
    elist = getAllEmployees()
    #for each emp
    for e in elist :
        #check if today's date matches birthdate
        if not matchDate(e, dateType,today) :
            continue
        #send email to employee
        sendNotificationOnDate(e, body,subject, ESC )
        addToDict(level1, e, getReportingManagerEmpNum(e.EMPLOYEE_ID))
        addToDict(level1, e, getDcLeadEmpNum(e.EMPLOYEE_ID))
    #send summary e-mail to 1st and 2nd level managers
    sendSummaryToManagers(mBody,mSubject, level1)
    db.session.close()
    return "Notifications Sent"

#Return emails as per the dateType and ESCalation type; 0=No escalation, 1= 1st level, 2=2nd level
def sendNotificationOnDate(emp, body,subject, ESC=0 ) :
    message = htmlhead + body + hrmsfooter + htmlfooter
#    notify('srinivas.kambhampati@msg-global.com', subject , message ,  templateId="-1")
    notify(emp.OFFICE_EMAIL_ID, "BETA:" + subject , message ,  templateId="-1")
    return

def sendSummaryToManagers(body,subject, dict1) :
    for k in dict1.keys() :
        #Get e-mail from emp_Id of the manager
        managerEmail = getEmployeeEmail(k)
        emlist = ''
        for e in dict1[k].keys() : #Emp Objects
            emlist += "<p>" + e.OFFICE_EMAIL_ID + "</p>"
        #Send e-mail to manager
        message = htmlhead + body + emlist + hrmsfooter + htmlfooter
        notify(managerEmail, subject, message, templateId="-1" )
    #Add myself for manager notifications, for testing only, to be removed later
        notify('srinivas.kambhampati@msg-global.com', "SentTo:" + managerEmail, message, templateId="-1" )
    return

def addToDict(dictName, emp, manager_id) :
    if manager_id not in dictName.keys() :
        dictName[manager_id] = dict()
    #Avoid Duplicates
    if manager_id in dictName.keys() and emp in dictName[manager_id].keys() :
        return # Employee is ALREADY added
    dictName[manager_id][emp] = 1
    #print("Manager ID:%s, emp-email:%s" % (manager_id, emp.OFFICE_EMAIL_ID))
    return

#Return True if today's date matches the date-field
# DATE_OF_JOINING , 
def matchDate(emp, dateType, todayDate ) :
    if not emp:
        return False        
    if not emp.DATA_OF_BIRTH : #Employee Date of Joining is not available
        return False
    if not emp.DATE_OF_JOINING : #Employee Date of Joining is not available
        return False
    emp_bday = emp.DATA_OF_BIRTH.day
    emp_bmonth = emp.DATA_OF_BIRTH.month
    emp_jday = emp.DATE_OF_JOINING.day
    emp_jmonth = emp.DATE_OF_JOINING.month

    today_day = todayDate.day
    today_month = todayDate.month
    
    if (dateType == 'BDAY' and today_day == emp_bday and today_month == emp_bmonth ) :
#    if (dateType == 'BDAY' and today_day == emp_day) :
        return True

    if (dateType == 'ANIV' and today_day == emp_jday and today_month == emp_jmonth ) :
#    if (dateType == 'ANIV' and today_day == emp_jday) :
        return True
    return False

