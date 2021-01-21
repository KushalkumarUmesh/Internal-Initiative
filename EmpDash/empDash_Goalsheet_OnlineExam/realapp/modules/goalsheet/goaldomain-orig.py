"""
K.Srinivas, 10-Apr-2018

Project: Goal Sheet
Description: These are the domain methods for the Goal Sheet module. 
    a) getTests: Returns a set of lists containing Test-attributes for ALL tests.
    b) updateTest: Updates the Exam Object and all the Questions with the answers given

TODO: 
KNOWN BUGs: None
"""
import logging
import datetime as dt
from hrmsdomain import *
from goalmodel import *
from readmaillist import MsgEmailList
from emailstrings import *
from hrmsempdata import getEmpDictbyEmail, getEmpDictbyEmpid
#from feedbackdomain import recordSheetFeedback -- This results in circular depenency
import feedbackdomain # need only recordSheetFeedback
from realapp import cache, RepresentsInt

#Get Templates
#Get Employees by Manager Role
#Get Employees by DC-Lead-role
def getEmpSetForSelect(dcLeadEmail) :
    return getDCEmpSetForSelect(dcLeadEmail)
        
def get1stLevelReporteesForSelect(mgrEmail) :
    return  getReporteeSetForSelect(mgrEmail)

#@cache.cached(timeout=1800,key_prefix='getTemplateListForSelect')
def getTemplateListForSelect() : # We need to ensure that ONE template exists, no point in checking it here
    itemSet = AssignmentTemplate.query.all()
    return [(item.id, item.title) for item in itemSet]

def deleteGoalSheet(em, year) :
    emp_id = getEmpIdByEmail(em) 
    #Get Goal-Sheet
    sheet = GoalSheet.query.filter_by(empId = int(emp_id)).filter_by( assessmentYear = year).first() # Fix this...
    if not sheet :
        return ("Employee (%s) does not have a Goalsheet." %(em))
    goalSheetId = sheet.id
    #Delete Goals
    Task.query.filter_by(goalSheetId = goalSheetId ).delete(synchronize_session='evaluate')
    Goal.query.filter_by(goalSheetId = goalSheetId ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    GoalSection.query.filter_by(goalSheetId = goalSheetId ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    GoalSheet.query.filter_by(id = goalSheetId ).delete(synchronize_session='evaluate')
    db.session.commit()
    return("Goal Sheet with ID= %d Deleted" %(goalSheetId))
    #Delete Goal Sections
    #Delete GoalSheet


def assignTemplate(em, tempId, managerEmail, year, notify=True) : 
    #Create GoalSheet Object
#    print(em + ":" + managerEmail + ":" + str(tempId))
    emp_id = getEmpIdByEmail(em) 
    if doesEmpHaveAGoalSheet(emp_id, year) :
        return ("Employee (%s) already has a Goalsheet assgined." %(em))
    assigningManager_empId = getEmpIdByEmail(managerEmail) # Person assigning the goal sheet
    if not is_DCLead(em) :
        assessingManager_empId = getDcLeadEmpNum(emp_id) # For now DC Lead/or assigner is also the evaluator
    else :
        assessingManager_empId = getReportingManagerEmpNum(emp_id) # For now DC Lead/or assigner is also the evaluator
    if not emp_id or not assessingManager_empId :
        print ("Emp or AssingManager not in HRMS : emp_id=%s, assessingManager:%s"
             % ( str(emp_id), str(assessingManager_empId)) )
        return ("Employee or Manager could not be located in HRMS ")
        
    gs = createGoalSheet(emp_id, tempId, assessingManager_empId, assigningManager_empId, year)    #Get Template Object
    
    #template = AssignmentTemplate.query.filter_by(id = tempId ).first()
    tempContents = TemplateGoalList.query.filter_by(templateId = tempId).all()
    #collect Master Goal-Objects
    mgoalsList = []
    for tlist in tempContents: 
        mg = getMasterGoalById(tlist.mastergoalId)
        mgoalsList += [mg] # We are getting list of Master goals
#        print('MS-ID=%d, %s' % (mg.id, mg.title)) 
    #Get Sections
    mgoalSectionList = [] # Master Goal Section List
    for mgl in mgoalsList:
        mg = getMasterGoalById(mgl.id) # Get the Mastergoal from ID
        mgs = getMasterGoalSectionById (mg.goalSectionId) #Get the MasterGoalSection from ID
        mgoalSectionList += [mgs] # Add to the list of MasterGoalSections
#        print('MSD-ID=%d, %s' % (mgs.id, mgs.title)) 

    #Copy GoalSections
    goalSectionMap = dict() # Map of MasterGoalSection-GoalSection: Key is MasterGoalSection-ID, Value is Individual GoalSection-ID
    for mgs in mgoalSectionList :
        gsID = mgs.id
        if gsID  in goalSectionMap.keys() : # This was already and handled
            continue
        newgs = createGoalSectionFromMaster(mgs, emp_id, "2018-04-01","2019-03-31",  gs.id)
        goalSectionMap[mgs.id] = newgs.id  # Update our Map

    #Copy Goals
    for mg in mgoalsList :
        ngs_id = goalSectionMap[mg.goalSectionId] # Get the NEW Goal Section for the Given Master Goal Section
        createGoalFromMaster(mg, ngs_id, emp_id, "2018-04-01","2019-03-31", gs.id, tempId  )

    if notify:
        notifySheetStatusChange(gs,goalEmailSubject, goalAssign %(year) ,\
            goalEmailSubject, goalAssignDC % (em))
    return ("Goal assigned to employee:" + em)

    #Update GoalSheet Status



#This is probably not used. Put an X to see if it fails somewhere
#To be deleted laer
def XgetGoalTitleById(goalId) :
    gl = Goal.query.filter_by(id = goalId).first()
    return gl.title

#For updating the goal-Target
def getGoalById(goalId) :
    gl = Goal.query.filter_by(id = goalId).first()
    return gl


def createTask(goal,  desc = None, cstatus = "Identified") :
    obj = Task()
    obj.goalId = goal.id #Set Goal-ID
    obj.goalSheetId = goal.goalSheetId #Set Goal Sheet ID
    obj.dtAssigned = dt.datetime.now()
    obj.dateStart = goal.dateStart
    obj.dateEnd = goal.dateEnd
    obj.manadator = True
    obj.completionstatus = cstatus
    if desc:
        obj.description = desc
    return obj

@cache.cached(key_prefix='getGoalSheetStatusForSelect')
def getGoalSheetStatusForSelect() :
    return sorted([('Assigned','Assigned'),\
        ('Pending1stApproval','Pending1stApproval'), \
        ('Pending2ndApproval','Pending2ndApproval'), \
        ('Returned','Returned'),\
        ('Approved','Approved'),
        ('Reviewed','Reviewed'), # Need CRON to move to this state to Approved state at the end of the review cycle
        ('Pending1stReview','Pending1stReview'), \
        ('Pending2ndReview','Pending2ndReview'), \
        ('Pending-1stLevel','Pending-1stLevel'), \
        ('Pending-2ndLevel','Pending-2ndLevel'), \
        ('Pending-MGMT','Pending-MGMT'), \
        ('Completed','Completed'), 
        ('Closed','Closed'), # Need CRON to move to this state
          ])


@cache.cached(key_prefix='getTaskStatusForSelect')
def getTaskStatusForSelect() :
    return sorted([('Identified','Identified'),('Pending Approval','Pending Approval'), \
        ('Returned','Returned'),('Approved','Approved'), ('1stLevelReviewed','1stLevelReviewed'), \
        ('Completed','Completed') ])
    
#Filter out inactive employees
def getGoalSheets(assessingManagerEmail, filterActiveEmps=True, year = '2018-2019') :
    dcEmpId = getEmpIdByEmail(assessingManagerEmail) 
    gsList = GoalSheet.query.filter_by(assessingManager = dcEmpId).filter_by(assessmentYear = year).all()
    if filterActiveEmps :
        return goalSheetFilterForActiveEmps(gsList)
    return gsList

#MISNOMER - IT gets all the goal-sheets with-in the reporting tree
#Get all goal-sheets for DC-Lead
def getGoalSheetsForDc(dcEmail, year = '2018-2019') :
    #a) get gsList for direct reportees
    finalGsList = []
    finalGsList = getGoalSheets(dcEmail, filterActiveEmps=False)
    #b) Get a list of reportees
#    directReports = getAllManagersInDc(dcEmail)
    directReports = getAllManagersInTree(dcEmail)
    #c) get gsLIst for the direct reportees and add-up
    for dr in directReports :
        drEmail = dr.OFFICE_EMAIL_ID
#        print("getting goal sheets for:"+ drEmail)
        finalGsList += getGoalSheets(drEmail.lower(), filterActiveEmps=False)
#        print("No. of sheets so far=" +str(len(finalGsList)) +"\n")
    #d) add all these, filter for Active emps and return
    return goalSheetFilterForActiveEmps(finalGsList) # No need to filter for Active emps, it has already happened

#TODO: Test-Filter out inactive employees
#@cache.cached(timeout=60, key_prefix="getGoalSheetsAll")
def getGoalSheetsAll(year = '2018-2019') :
    gsList = GoalSheet.query.filter_by(assessmentYear = year).all()
    return goalSheetFilterForActiveEmps(gsList)

def getGoalSheetById(sheetId) :
    gs = GoalSheet.query.filter_by(id = sheetId).first()
    return gs

#TODO: Test-Filter out inactive employees 
#DUPLICATE of getGoalSheetsAll
# @cache.cached(timeout=30)
# def getAllGoalSheets(year = '2018-2019') :
#     gsList = GoalSheet.query.filter_by(assessmentYear = year).all()
#     return goalSheetFilterForActiveEmps(gsList)

def goalSheetFilterForActiveEmps(gsList) :
    #Get list of active employees,
    empList = getAllEmployees() 
    empHash = dict()
    for emp in empList :
        empHash[int(emp.EMPLOYEE_ID)] = 1
    #Check each and del inactive ones
    for g in gsList :
        if g.empId not in empHash.keys() :
            gsList.remove(g) # Remove inactive employee's goal-sheet
    return gsList

def getGoalSheet(sheetId) :
    gs = GoalSheet.query.filter_by(id = sheetId).first()    
    return gs

def getGoalSheetForEmp(empEmail, year = '2018-2019') :
    empId = getEmpIdByEmail(empEmail)
    if not empId :
        return False
    gs = GoalSheet.query.filter_by(empId = empId).filter_by(assessmentYear = year).first()    
    return gs

#####################################################Works

def assignTemplateFromFile(fname, tempId, managerEmail, year) :
    eObj = MsgEmailList("", [], fname) 
    emailDict = eObj.getEmailDict()
    retStr = ""
    for e in emailDict.keys() :
        retStr += assignTemplate(e, tempId, managerEmail, year) 
    return ("Goal assigned to employees: " + retStr)


########################################################################################################################
# Methods used for displaying Goal-Sheet Page [Sheet->Goalsections->Goals->Tasks]
########################################################################################################################
@cache.memoize(timeout=300) #5 min enough
def getGoalSheetHeader(empEmail, year) :
    msgDict = getEmpDictbyEmail(empEmail) # Get all available fields for the employee
    if not msgDict :
        print("Employee not found with email:" + empEmail)
        return {'FIRST_NAME':"Not available",'EmployeeID':"NA", 'Current Role':'To Be Updated', 'Designation':"Not available", \
        'Project/Department' : "Not available", 'Manager': "Not available" , 'Assessment Year': "Not available"  }
        
    empName = msgDict["FIRST_NAME"] + " " + msgDict["LAST_NAME"]
    empId = str(msgDict["EMPLOYEE_ID"])
    empDesignation =  msgDict["DESIGNATION"]
    empDepartment = msgDict["DEPARTMENT"]
#    empManager = msgDict["MANAGER_NAME"]
    empManager = msgDict["DC_LEAD"]
    empInfo = {'FIRST_NAME':empName,'EmployeeID':empId, 'Manager2': get2ndLineManagerName(empId), 'Designation':empDesignation, \
        'Project/Department' : empDepartment, 'Manager': empManager , 'Assessment Year': year  }
    return empInfo

def getAllGoalsAndSections(empId, year) :
    if not RepresentsInt(empId):
        return(None,None,None)

    sheet = GoalSheet.query.filter_by(empId = int(empId)).filter_by( assessmentYear = year).first() # Fix this...
    if sheet:
        return getAllGoalsAndSectionsInSheet(sheet)
    else :
        return(None,None,None)

def getAllGoalsAndSectionsInSheet(sheet) :
    allgoalsections = GoalSection.query.filter_by(goalSheetId = sheet.id).all()
    allgoals = []
    for gs in allgoalsections :
        allgoals += [Goal.query.filter_by(goalSheetId = sheet.id).filter_by(goalSectionId = gs.id).all()]
    return (sheet, allgoalsections , allgoals)

def getAllTasks( allgoals) :
    alltasks = dict()
    if allgoals :
        for goalsInSection in allgoals : # Get each set of goals in a section
            for goal in goalsInSection : # get each goal in a set of goals for this section
                alltasks[goal.id] = Task.query.filter_by(goalId = goal.id).all()  # Get tasks for THIS goal
    return alltasks

def getAllTasksInGoal( goalId) :
    alltasks = Task.query.filter_by(goalId = goalId).all()  # Get tasks for THIS goal
    return alltasks

def getAllTasksInSheet(gs) :
    alltasks = Task.query.filter_by(goalSheetId = gs.id).all()  # Get tasks for THIS goal
    return alltasks


def getAllTasksForSelect(empEmail, year) :
    #Get Goal-Sheet ID
    gs = getGoalSheetForEmp(empEmail, year)
    if not gs :
        return (["",""])

    #Get all tasks
    alltasks = Task.query.filter_by(goalSheetId = gs.id).all()  # Get tasks for THIS goal    
    #Create a Select block
    return sorted([(t.id, t.description) for t in alltasks])

def getTaskById(taskId) :
    return Task.query.filter_by(id = taskId).first()  # Get tasks for THIS goal    

########################################################################################################################
#GoalSheet States-Implemented: Assigned (initial), PendingApproval (DC lead to approve), Approved, Returned
#Other states will come later such as "Submitted for Evaluation", etc.
########################################################################################################################

def requestGoalSheetApproval(sheet) :
    sheet.status = "PendingApproval" 
    emp = getEmployeebyId(sheet.empId)
    assessingMgr = getEmployeebyId(sheet.assessingManager)
    notifySheetStatusChange(sheet, goalEmailSubject, goalPendingApproval % (assessingMgr.OFFICE_EMAIL_ID) ,\
        goalEmailSubject , goalPendingApprovalDC % (emp.OFFICE_EMAIL_ID))
    return ("Goal Sheet is PendingApproval.")
 
#IS THIS USED AT ALL?
def submitGoalSheet(sheet) :
    sheet.status = "PendingApproval" 
    #Notify
    return ("Goal Sheet is PendingApproval.")

def submitSelfAssessment(sheet) :
    sheet.status = "Pending-1stLevel" 
    #Notify
    return ("Goal Sheet is Pending-1stLevel.")

def pendingReviewGoalSheet(sheet) :
    sheet.status = "PendingReview"
    #Notify
    return ("Goal Sheet set to PendingReview.")

def managerSubmitFeedbackGoalSheet(sheet) :
    sheet.status = "Approved" # Moved back to Approved state
    #Notify - Notification content changes as feedback was given
    return ("Goal Sheet set to Approved.")

def setStatusInAllTasksInGoal( goalId, status = "Approved") :
    alltasks = getAllTasksInGoal(goalId)  # Get tasks for THIS goal
    for t in alltasks :
        t.completionstatus = status
    return 


#Need to Store Comments in the Feedback Table
def approveGoalSheet(comments, sheet, mgmtLevel) :
    mgrComments = "No comments"
    emp = getEmployeebyId(sheet.empId)
    if comments:
        sheet.managerComments = comments
        mgrComments = comments
        feedbackdomain.recordSheetFeedback(sheet, comments, visibleToEmp = True, visiblityLevel=1 , \
            dateRecorded = dt.datetime.now(),  giverEmpId = 0  )
    if mgmtLevel == 2:
        sheet.status = "Approved"
    elif  mgmtLevel == 1:
        sheet.status = "1stLevelReviewed"
    else :
        sheet.status = "DontKnowWhatToDo"
        
    #Update Status of ALL Tasks in the Sheet 
    (x, allgoalsections , allgoals) = getAllGoalsAndSectionsInSheet(sheet)

    for gs in allgoals :
        for g in gs :
            g.completionstatus = sheet.status

    updateAllTasksStatus(sheet, sheet.status)
    notifySheetStatusChange(sheet, goalEmailSubject, goalApproved %(mgrComments),\
        goalEmailSubject, goalApprovedDC %(emp.OFFICE_EMAIL_ID, mgrComments) )
    return ("Goal Sheet is approved.")

def returnGoalSheet(comments, sheet, mgmtLevel) :
    mgrComments = "No comments"
    emp = getEmployeebyId(sheet.empId)
    if comments:
        sheet.managerComments = comments
        mgrComments = comments
        feedbackdomain.recordSheetFeedback(sheet, comments, visibleToEmp = True, visiblityLevel=1 , \
            dateRecorded = dt.datetime.now(),  giverEmpId = 0  )
    sheet.status = "Returned" 
    #Notify
    notifySheetStatusChange(sheet,goalEmailSubject, goalReturned  %(mgrComments) ,\
        goalEmailSubject, goalReturnedDC %(emp.OFFICE_EMAIL_ID, mgrComments))
    return ("Goal Sheet returned to employee with comments.")

def doesEmpHaveAGoalSheet(empId, year) :
    sheet = GoalSheet.query.filter_by(empId = int(empId)).filter_by( assessmentYear = year).first() # Fix this...
    if sheet :
        return True
    else :
        return False

def notifySheetStatusChange(sheet,subjectEmp, empMessage,subjectManager, managerMessage) :
    #get employee email
    emp = getEmployeebyId(sheet.empId)
    if emp :
        empEmail = emp.OFFICE_EMAIL_ID
        notify(empEmail,subjectEmp, empMessage ,  templateId="-1")
    emp = getEmployeebyId(sheet.assessingManager)
    if emp :
        empEmail = emp.OFFICE_EMAIL_ID
        notify(empEmail, subjectManager, managerMessage ,  templateId="-1")


@cache.memoize(timeout=1800)
def getAuthLevel(user, ownItem, is_admin = False) :
    if ownItem : return 0 # 
    if is_admin :
        return 3 # Instead of 10, force HR to be sr. Admin
    if is_countryManager(user) : return 3 # Sridhar/Sriram/HR?
    if is_DCLead(user) : return 2 # DC
    if is_Manager(user) : return 1 # DC
    
    #Make RBAC calls here
    return 0 # authorization level

#Generic method to return the relationship between the item-Owner and the logged-in user
#Outputs are: 0 - Owner, 1-1st Level Manager, 2-DC-Lead, 3-Management/HR, 10-Admin
#Current UNTESTED and UNUSED
@cache.memoize(timeout=1800)
def getMgmtRelationship(sheetOwnerEmail, loggedInEmail, sheetOwnerEmpId=0, loggedInEmpId=0 ) :
    #Best approach is to go with EmpIds and look-up in HRMS
    if not sheetOwnerEmpId :
        sheetOwnerEmpId = getEmpIdIntByEmail(sheetOwnerEmail)
    if not loggedInEmpId :
        loggedInEmpId = getEmpIdIntByEmail(loggedInEmail)

    if loggedInEmpId == sheetOwnerEmpId :  return 0 # Owner
#    print("Getting LineManager for:" + str(sheetOwnerEmpId))
    mgrId = getLineManagerId(sheetOwnerEmpId)
    if not mgrId :
#        print("loggedInEmpId=" + str(loggedInEmpId) )
        return -1 
    if loggedInEmpId == int(mgrId) :
#        print("Hit 1nd Level=" + str(mgrId) )
        return 1 # 1st level manager, 1st-level, DC-Lead (for managers), Country-Manager (for DC-leads)

#    print("Getting 2ndLineManager for:" + str(sheetOwnerEmpId))
    mgr2Id = get2ndLineManagerId(sheetOwnerEmpId)
    if not mgr2Id :
#        print("loggedInEmpId=" + str(loggedInEmpId) )
#        print("LineManager=" + str(mgrId) )
        return -1 
    if loggedInEmpId == int(mgr2Id):
#        print("Hit 2nd Level=" + str(mgr2Id) )
        return 2 # 2nd Level manager, could be DC lead or country manager
    #Don't know
    print("loggedInEmpId=" + str(loggedInEmpId) )
    print("LineManager=" + str(mgrId) )
    print("2ndLineManager=" + str(mgr2Id) )
    return -1

