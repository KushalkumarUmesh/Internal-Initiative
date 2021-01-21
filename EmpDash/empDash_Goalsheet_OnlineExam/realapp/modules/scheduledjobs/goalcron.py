from feedbackmodel import GoalFeedback
import datetime as dt
import goaldomain # getGoalSheet
from notification import notify, notifyGroup
from hrmsdomain import getEmployeeEmail
from hrmsempdata import getEmployeeNameById
from emailstrings import *
from realapp import db, ELEMENT_TYPE_SHEET , ELEMENT_TYPE_GOAL, ELEMENT_TYPE_TASK, cache
from askfeedbackmodel import FeedbackFromAnyone
from goaldomain import getGoalSheetStatusForSelect
from calendarmodel import GoalCalendar
from calendardomain import getCalFlags

#CRON-Job for sending out e-mails on feedback
#Method to go through the Feedback-entries from Feedback table and send out e-mails
#to folks, based on the flags set.
def notifyFeedbackToEmployees() :
    fStr = dict() # Key=Emp.no, Value = message string
    #Send e-mails to Emps first
    feedbackList = GoalFeedback.query.filter_by(empNotified = False).filter_by(visibleToEmp = True).all() # Get all pending notifications
    for f in feedbackList :
        getStringRep(f, fStr) # Get the string representation and append to list by emp_no
    for k in fStr.keys() : # All emp-emails pending
        empEmail = getEmployeeEmail(k)
        if not empEmail :
            print("Email not found= Emp.No:" + str(k))
        mesg = htmlhead+ feedbackHeader + fStr[k] + goalsheetFooter + htmlfooter
#        notify(empEmail, feedbackSubject, messg,  templateId="-1")
#For Testing Only, send all e-mails to me prefixed by the addresss
        subj = feedbackSubject
        #print("Sending e-mail to:" + empEmail)
        notify(empEmail, subj, mesg,  templateId="-1")

    #Set the flag so that it does not send it again
#TESTING...uncomment for real use
    for f in feedbackList :
        f.empNotified = True
    #Send e-mails to Non-emps
    #Year end assessment notification
    #     
    #REsend e-mails to emps
    #REsend e-mails to non-emps
    db.session.commit()
    return

#Send notifications on feedback requests...
def sendAskFeedbackNotificationsCron() :
    empRecvList = dict() #Key: receiver email, Value=List of givers
    empGivrList = dict() #Key: Giver email, Value= List of receivers
    empAllList = dict()

    #Get a list of all feedbacks - empNotified = False
    askList = FeedbackFromAnyone.query.filter_by(empNotified = False).all()
    for ask in askList :
        #=>Who you asked
        givr = ask.giverEmail
        recv = ask.receiverEmail
        if givr not in empGivrList.keys() :
            empGivrList[givr] = "" # Initialize to an empty List
            empAllList[givr] = 1 
        empGivrList[givr] += recv + " " 

        if recv not in empRecvList.keys() :
            empRecvList[recv] = "" # Initialize to an empty List
            empAllList[recv] = 1 
        empRecvList[recv] += givr + " "
    
#    revrString = "You have requested feedback from:"
#    givrString = "Feedback has been requested from you by:"
    for emp in empAllList : # All givers, receivers found
        recvsList = 0
        givrsList = 0
        revrString = "You have requested feedback from:"
        givrString = "Feedback has been requested from you by:"
    #Send Notifications, one-person-by-one-person + Update Table notified time
    #Commented out the GIVERS--no need to send e-mail to self
        if emp in empGivrList.keys() :
            givrString += empGivrList[emp]
            givrsList = 1
        if emp in empRecvList.keys() :
            revrString += empRecvList[emp]
            recvsList = 1
        finalStr = ""
        if givrsList :
            finalStr  =  givrString + "<p>"   
        if recvsList :
            finalStr  +=  revrString + "<p>" 
        #send notification emp
        mesg = htmlhead + askfeedbackHeader + finalStr + goalsheetFooter + htmlfooter

        subject = askfeedbackSubject
        notify(emp, subject, mesg)
#        notify('srinivas.kambhampati@msg-global.com', subject, mesg)
    #Update DB
    for ask in askList :
        ask.empNotified = True
#        ask.empNotifiedTime = dt.datetime.now()
    db.session.commit()

#def notifyTaskDeadLine()
#def notifyPendingApproval()
#def notifyPendingSubmission()
#def notifyAssessingManagerChange()

#TODO: Put Goal/Task Title
#Need to format this correctly for multiple comments
def getStringRep(f, fStr) :
    #Ignore comments given to self
    if f.receiverEmpId == f.giverEmpId :
        return
    msgForStr = getElementString(f.elementId, f.elementType)
    msgStr = msgForStr + " ====> <b>" + f.feedback + "</b>"
#    if visiblityLevel : # Anything other than emp
    if f.receiverEmpId in fStr.keys() :
        fStr[f.receiverEmpId] += msgStr
    else :
        fStr[f.receiverEmpId] = "Comments:<p>" + msgStr
    return

def getElementString(elementId, elementType) :
    if elementType == ELEMENT_TYPE_TASK :
        #getTaskByID
        task = goaldomain.getTaskById(elementId)
        if not task :
            print("Task Not found in getElementString=" + str(elementId) + ":" + str(elementType))
            return "<b>Task:</b>" + str(elementId)
            
        return "<b>Task:</b>" + task.description

    if elementType == ELEMENT_TYPE_GOAL :
        #getTaskByID
        goal = goaldomain.getGoalById(elementId)
        if not goal :
            print("Goal Not found in getElementString=" + str(elementId) + ":" + str(elementType))
            return "<b>Goal:</b>" + str(elementId)
        return "<b>Goal:</b>" + goal.title

    if elementType == ELEMENT_TYPE_SHEET :
        #getTaskByID
        sheet = goaldomain.getGoalSheetById(elementId)
        if not sheet :
            return "<b>Sheet:" + str(elementId) + "</b>"
        return "<b>Sheet for " + sheet.assessmentYear + "</b>"

### IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT
### This deletes the Cal-Flags CACHE, so IT MUST BE DONE AT MIDNIGHT and NOT DISABLED
#This is a cron job expected to run right after mid-night. 
# It will verify that EACH GOAL-SHEET
#STATUS, auth-level has ONE and only ONE valid entry. If not it will send notification
#to the GoalSheet Maintenance Team
def calFlagsVerifyCron(year='2018-2019', detailedInfo=True) :
    print("Clearing Calandar Flags from Cache")
    cache.delete_memoized(getCalFlags)
#    cache.delete_memoized(getCalendarFlags) #This method itself appears to be UNUSED
#    todayDate = dt.datetime.today()
#    calFlagsVerifyDate(todayDate, year='2018-2019', detailedInfo=True) 
    return
#TODO: Complete this one to SCAN the entire time-window for valid Calendar data
#Check Calendar Flags from today to rest of the year
#The objective is that for ANY status+AuthLevel, there should be ONE and ONLY one entry
#excluding the PERFORM phase incase there are TWO entries
# def calFlagsVerifyCron(year='2019', detailedInfo=True) :
#     todayDate = dt.datetime.today()
#     for timedelta
#     for authLevel in (0,1,2,3) :
    

#Method to check if Calendar Data is consistent for a given date
def calFlagsVerifyDate(ckdate, year='2018-2019', detailedInfo=False) :
    mesgStr = ""
    for authLevel in (0,1,2,3) :
        mesgStr += "<p>Emp. Level = " + getAuthLevel(authLevel) + "</p>"
        for sheetStatusEntry in getGoalSheetStatusForSelect() :
            sheetStatus =sheetStatusEntry[0]
#            print("sheetStatus=" + str(sheetStatus))
            calList = GoalCalendar.query.filter_by(assessmentYear=year). \
                filter_by(authlevel=authLevel).filter_by(sheetStatus=sheetStatus). \
                filter( ckdate >= GoalCalendar.dateStart, ckdate <= GoalCalendar.dateEnd). \
                all()

            calFinal = None
            calCount = len(calList)

            if calCount > 2:
                mesgStr = "Too many Phases found for:" + str(todayDate) + ":" + str(sheetStatus) + ":" + str(authLevel)
                print(mesgStr)
        #        notify('srinivas.kambhampati@msg-global.com', "FATAL ERROR:GoalSHEET CALENDER",mesgStr )
                return flagDict

            if calCount == 1 : # Only Perform phase can be there
                calFinal = calList[0]
            else : # calCount == 2, take the one where phaseType is NOT zero
                if calList[0].phaseType :
                    calFinal = calList[0]
                else : 
                    calFinal = calList[1]
        #        print("Phase:" + calFinal.phase)    

            if not calFinal:
                mesgStr += "Sheet Status:" +  str(sheetStatus) + ":" + " No Valid Phase found"  + "<br>"
            elif count > 1:
                mesgStr += "Sheet Status:" + str(sheetStatus) + ":" + " More than ONE Valid Phases found"    + "<br>"
            else :
                mesgStr += "Sheet Status:" + str(sheetStatus) + ":" + " OK"  
                if detailedInfo :
                    mesgStr += getFlagsStr(calFinal)   + "<br>"
                else : 
                    mesgStr += "<br>"
                
#    print("mesgStr=" + mesgStr)
    finalmesgStr = htmlhead  + mesgStr + goalsheetFooter + htmlfooter
    if mesgStr :
        notifyGroup("GoalSheetAdmin", "FATAL ERROR in GoalSheet CALENDAR DATA",mesgStr ,\
            fromemail = "goalsheet-monitor@msg-global.com" , templateId="-1") 
    else :
        notifyGroup("GoalSheetAdmin", "No ERRORs in GoalSheet CALENDAR DATA", "Great Work" ,\
            fromemail = "goalsheet-monitor@msg-global.com" , templateId="-1")
        
    return

def getAuthLevel(authLevel) :
    if authLevel == 10 :
        return "Super User"
    if authLevel == 3 :
        return "HR/Management"
    if authLevel == 2 :
        return "DC-Lead"
    if authLevel == 1 :
        return "1st Level Manager"
    if authLevel == 0 :
        return "Line Employee"
    return "Unknown AuthLevel:" + str(authLevel)

def getFlagsStr(calFinal) :
    flagDict =dict()
    flagDict['phase'] = calFinal.phase
    flagDict['actionString'] = calFinal.actionString
    flagDict['actionId'] = calFinal.actionId
        
    #Create flagDict 
    flagDict['gs_enable_assignment'] = calFinal.gs_enable_assignment

    flagDict['gs_enable_self'] = calFinal.gs_enable_self
    flagDict['gs_enable_approve'] = calFinal.gs_enable_approve
    flagDict['gs_enable_end_year_self'] = calFinal.gs_enable_end_year_self
    flagDict['gs_enable_end_year_dc_approve'] = calFinal.gs_enable_end_year_dc_approve
    flagDict['gs_enable_end_year_closure'] = calFinal.gs_enable_end_year_closure

    flagDict['goal_enable_task_approve'] = calFinal.goal_enable_task_approve
    flagDict['goal_enable_edit'] = calFinal.goal_enable_edit
    flagDict['goal_enable_approve'] = calFinal.goal_enable_approve

    flagDict['task_enable_update'] = calFinal.task_enable_update
    flagDict['task_enable_delete'] = calFinal.task_enable_delete
    flagDict['task_enable_activity_edit'] = calFinal.task_enable_activity_edit
    flagDict['task_enable_status_change'] = calFinal.task_enable_status_change

    msgStr = "<br>PHASE: " + flagDict['phase'] + "<br>TASKS:"
    if flagDict['task_enable_update'] :
        msgStr += "task_enable_update,"
    if flagDict['task_enable_delete'] :
        msgStr += "task_enable_delete,"
    if flagDict['task_enable_activity_edit'] :
        msgStr += "task_enable_activity_edit,"
    if flagDict['task_enable_status_change'] :
        msgStr += "task_enable_status_change,"

    msgStr += "<br>GOALS:"
    if flagDict['goal_enable_task_approve'] :
        msgStr += "goal_enable_task_approve,"
    if flagDict['goal_enable_edit'] :
        msgStr += "goal_enable_edit,"
    if flagDict['goal_enable_approve'] :
        msgStr += "goal_enable_approve,"

    msgStr += "<br>SHEET:"
    if flagDict['gs_enable_self'] :
        msgStr += "gs_enable_self,"
    if flagDict['gs_enable_approve'] :
        msgStr += "gs_enable_approve,"
    if flagDict['gs_enable_end_year_self'] :
        msgStr += "gs_enable_end_year_self,"
    if flagDict['gs_enable_end_year_dc_approve'] :
        msgStr += "gs_enable_end_year_dc_approve,"
    if flagDict['gs_enable_end_year_closure'] :
        msgStr += "gs_enable_end_year_closure,"

    msgStr += "<br>ACTIONS AND ASSIGNMENT:"

    if flagDict['actionString'] :
        msgStr += "actionString= " + flagDict['actionString'] + ","
    if flagDict['actionId'] :
        msgStr += "actionId= " + str(flagDict['actionId']) + ","
        
    if flagDict['gs_enable_assignment'] :
        msgStr += "gs_enable_assignment"
    msgStr += "<br>"
    return msgStr

