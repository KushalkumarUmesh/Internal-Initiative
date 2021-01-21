"""
Overall Approach is as follows: Re-write the entire BCS-CHeck program. DO it in this order:
0) Creat main loop and view-file
a) Create Holiday Table - Done
b) Write methods for:
    -IsHoliday?
    -Hours booked by Emp on a day, on a project : Total billable hours
    -Is the emp on leave today? Is the leave approved?
c) Write methods for Error recording: Need to define a table
d) Methods for error-detection
e) Aggregate metrics
    = For employee
    = For DC-Leads
    = For Org
    = YTD, MTD Values

TODO: 
a) Bug: Total claimed hours does not include hours booked on Sunday - Pragnya.Senapati@msg-global.com 
"""
import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import datetime
import os

from bcsorgstruct import *
from bcsdomain import *
from projdomain import *
from bcsmodel import *
import calendar
from emailstrings import *
from hrmsempdata import getEmpDictbyEmail
from notification import notify
from hrmsdomain import getAllEmployees

#### THIS NOT A VIEW FILE, views are being created only for testing to be moved to another file

#Method for genering error-log for each employee
#Overall structure is as follows:
# For Each employee, For each day:
# Get bookings, get leave info
# Calculate agreegates
# Calcuate Utiization


def validEmpBcsData(empEmail,month, year, mrange ) :
    messageBuffer = [] 
    bookedHours = 0 # Total billable and non-billable hours booked
    billableHours = 0 # Initialize total billable hours available
    totalLeaveHours = 0 # Total Leave approved
    totalLeaveAppliedHours = 0 # Total Leave Applied For (not yet approved)
    errorcount = 0

    projBillableHash = dict() # Is the project billable? Not used
    projNameHash = dict() # Project Name 
    projList = dict() # Hash of emp-hash hours
    e = empEmail # For convenience
    for d in range(1,mrange) :  #Extremely inefficent, brute force, but also safest course of action
        day = datetime.date(year,month,d)
        dayOfWeek = day.weekday()
        wd = (dayOfWeek <= 4) and not isHoliday(day) # WorkingDay if true
        if wd : 
            billableHours += 8 # Add 8 billable hours
            #Get Leave data ONLY if it is a working-date
            (leaveHours,leaveHoursApplied) = getLeaveInfo(e,day)
            totalLeaveHours += leaveHours
            totalLeaveAppliedHours += leaveHoursApplied
        #Emp. can work on weekends/holidays, so the processing need to be completed
        bookings = EmpBCSClaimData.query.filter_by(bookingDate = day).\
            filter_by(empEmail = e).all()

        daysBooking = 0 # this day, this employe, store separately

        for b in bookings: # All bookings for this day
            project_ID = b.project_ID.strip()
            projectName = b.projectName.strip()
            billability = b.billability.strip()
            duration = b.duration
            empEmail = b.empEmail # Should be same as "e", no need to check...its part of the filter_by
            projBillableHash[project_ID] = billability
            projNameHash[project_ID] = projectName
            fduration = float(duration) #Convert String to float
            if (round(fduration*60) == 8 or  round(fduration*60) == 4 ) : # Person has claimed min instead of hours
                msg = "WARNING:%s:Looks like MINUTES instead of HOURS on Project:%s" % (day.strftime('%Y-%m-%d'),projectName)
                logEmpBCSMessage(messageBuffer, msg ) 
#                logEmpError(e, msg)
            daysBooking += fduration # Hours booked only today, all projects: Used for checking
            if project_ID in projList.keys() : # Project is already encountered
                if empEmail in projList[project_ID] : #Emp in this project encountered
                    projList[project_ID][empEmail] += fduration #Add the hours
                else :
                    projList[project_ID][empEmail] = fduration
            else :
                projList[project_ID] = dict()
                projList[project_ID][empEmail] = fduration
        #Start checking for various errors
        #No claim found
        if wd and not daysBooking and leaveHours != 8 :
            logEmpBCSMessage(messageBuffer, "REMINDER:%s:No booking or approved leave found, please book your hours." % (day.strftime('%Y-%m-%d')) ) 
            errorcount += 1
        #Total 8 hours claimed if leave was applied for
        if wd and daysBooking and (leaveHours or leaveHoursApplied) and \
            ( (daysBooking + leaveHours) != 8 and (daysBooking + leaveHoursApplied) != 8) :
            logEmpBCSMessage(messageBuffer, "WARNING:%s:Hours Booked AND Leave(applied for) do not add-up to 8 hours" % (day.strftime('%Y-%m-%d') ) )
            errorcount += 1
        if wd and daysBooking > 8 :
            logEmpBCSMessage(messageBuffer, "INFORMATION:%s:More than 8 Hours(%d) Booked on a single day" % ( day.strftime('%Y-%m-%d'), daysBooking ) )
            errorcount += 1
    if errorcount :
        logEmpBCSMessage(messageBuffer, "Total %d discrepencies identified in BCS booking for month of %s" % \
            (errorcount, calendar.month_name[month]))
    else :
        logEmpBCSMessage(messageBuffer, "Thanks for claiming BCS correctly. No errors detected")
        
    #Aggregate errors and messages
    billedHours = 0 
#    logEmpBCSMessage(messageBuffer, "")
#    logEmpBCSMessage(messageBuffer, "Utilization Summary:")
    bcsUtilSummary = dict()
    bcsProjSummary = dict()
    for pid in projList.keys() :
        for e in projList[pid].keys() :
#            logEmpBCSMessage(messageBuffer, "Project[%s]:Hours[%s]" % (projNameHash[pid], str(projList[pid][e])))
            bcsProjSummary[pid] = "Project[%s]:Hours[%s]" % (projNameHash[pid], str(projList[pid][e]))
            if projBillableHash[pid] != 'N/B' :
                billedHours += projList[pid][e]
            bookedHours += projList[pid][e]
    bcsUtilSummary["AvailableHours"] = billableHours
    bcsUtilSummary["BookedHours"] = bookedHours
    bcsUtilSummary["BilledHours"] = billedHours
    bcsUtilSummary["LeaveHours"] = totalLeaveHours
    
#    logEmpBCSMessage(messageBuffer, "Available Hours[%d], Booked Hours[%d], Billed Hours[%d]" % \
#        (billableHours, bookedHours,bookedHours))
    return (messageBuffer, bcsProjSummary, bcsUtilSummary)

def getLeaveInfo(e,day) :
    #Get Leave Data
    leaves = EmpBCSLeaveData.query.filter_by(empEmail = e).filter(and_(EmpBCSLeaveData.dateStart <= day, EmpBCSLeaveData.dateEnd >= day)).all()
    leaveHours = 0
    leaveHoursApplied = 0
    for l in leaves: #Leave record
#        print("Leave:[%s]:%s:Start=%s:End=%s:Hours:%s" %(str(day), e, str(l.dateStart), str(l.dateEnd), str(l.duration)) )

        dur = float(l.duration[:-1])
        #status ='Applied For' and 'Approved'. Others (planned, rejected, etc.) are ignored
        if l.status == 'Approved':
            if dur >=1 :
                leaveHours += 8
            else :
                leaveHours += 4
        if l.status == 'Applied For':
            if dur >=1 :
                leaveHoursApplied += 8
            else :
                leaveHoursApplied += 4
#                print("Half Day Leave:[%s]:%s:%s:%s:Hours:%s" %(str(day), e, str(l.dateStart), str(l.dateEnd), str(l.duration)) )
    return(leaveHours,leaveHoursApplied)

def isHoliday(day) :
    fetch = Holidays.query.filter_by(date = day).first()
    return fetch    

def logEmpBCSMessage(messageBuffer,  message) :
    messageBuffer += [message]
    return

def formatMessageBuffer(messList) :
    str = htmlhead + "<table>"
    for m in messList :
        str += "<tr><td>" + m + "</td></tr>" 
    str += "</table>" + hrmsfooter + htmlfooter
    return str

def emailBCSInfoToEmp(empEmail,date, fullmsgbuf, bcsProjSummary, bcsUtilSummary) :
    #Get emp Details
    empDict = getEmpDictbyEmail(empEmail)
    #Form Message
    subject ="BCS Booking and Error Summary:" + date.strftime('%d-%m-%y')
    message = htmlhead + "<h4>Summary for : "  + empDict["FIRST_NAME"] + " " + empDict["LAST_NAME"] +"</h4>"
    message = "<h4>This is in BETA Test. Kindly help by pointing out any errors to K.Srinivas.</h4>"
    tstr = "<table>"
    for m in fullmsgbuf :
        tstr += "<tr><td>" + m + "</td></tr>" 
    tstr += "</table>"
    message += tstr 
    message += "<h3>Available Hours[%d], Booked Hours[%d], Billed Hours[%d] and Leave Hours[%d]</h3>" % \
        (bcsUtilSummary["AvailableHours"], bcsUtilSummary["BookedHours"], \
        bcsUtilSummary["BilledHours"],bcsUtilSummary["LeaveHours"] )

    message += hrmsfooter + htmlfooter
    #Send e-mail
    notify(empEmail, "BETA:" + subject , message ,  templateId="-1")

def emailBCSInfoToPMO (date, allErrors ) :
    #Form Message
    subject = "BCS Booking Errors-All:" + date.strftime('%d-%m-%y')
    message =  "<h4>Error Summary for all employees</h4>"
    message = "<h4>This is in BETA Test. Kindly help by pointing out any errors to K.Srinivas.</h4>"
    tstr = "<table>"
    for m in allErrors :
        tstr += "<tr><td>" + m + "</td></tr>" 
    tstr += "</table>"
    message += tstr 
    message += hrmsfooter 
    notifyGroup("PMO", "BETA:" + subject , htmlhead+ message+ htmlfooter, fromemail = "bcs-checkbookings@msg-global.com")
    return message

def checkBCSEmailsWithHRMS(nameHash) :
    retStr = ""
    emps = getAllEmployees()
    empDict = {e.OFFICE_EMAIL_ID.lower():e.OFFICE_EMAIL_ID for e in emps }
    for n in nameHash.values() :
        if n.lower() not in empDict.keys() :
            retStr += ":" + n
    if retStr:
        return ("Following BCS-Emails not in HRMS:" + retStr)
    return("")


##############################################################################################################
### Stuff below is the old one that will not work with DB #########################################################
##############################################################################################################
