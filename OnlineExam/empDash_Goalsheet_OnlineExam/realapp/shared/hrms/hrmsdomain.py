"""
K.Srinivas, 22-Mar-2018

Project: Multiple (starting with OnlineExam, Goalsheet)
Description: This is a set of Domain methods for getting,setting and listing data in the legacy HRMS. The original HRMS, designed as portlets
    in Liferay 6.2 has become a maintance challenge due to lack of source-code control and other reasons. However, it has
    lot of existing functionality that can be enhanced/used. In addition, maintance of master-data (list of managers, departments, etc.)
    and reports requires direct DB-access and SQL scripting. This is an attempt to augment the existing functionality and also use
    the existing data in newer application. Currently the following services are planned.

Common Methods
Emp:
    getEmployeebyId(emp_id) :
    getEmployeeEmail(emp_id) :
    getEmpIdByEmail(emailid) :
    getEmployee - Given the liferay userID, get the Employee Object
DC:
    getDCLead - given Employee Object, get DC-lead
    is_DCLead(dcleadEmail)
    getDcLeadEmpNum(emp_id)
Manager/Dept:
    getLineManager - given Employee Object, get manager
    get2ndLineManager - given Employee Object, get manager
    getDepartment - given Employee Object, get Dept.


NOTE: Currently being used to do an HRMS-employee data check/notification

TODO: 
a) Look for "ManagerINFO CHANGE" - Once the Manager_ID field is changed, these methods will need to change
b) filter_by(Status = None) # THis is a HACK till till we get Emp.Status corrected. 
    For now, non-null status means inactive. Need to fix it once the status-part is corrected in HRMS
    NOTE: This affects the nightly B'day and joining-day e-mails

KNOWN BUGs:
a) Added filter_by(Status = None) in DC-Emp Select (30-Jul-2018)
"""
import logging

from hrmsmodels import Employee, ManagerInfo, Departmant, Country, State, Designation, Addres, Gender
from readmaillist import MsgEmailList
from realapp import appC, cache
from notification import *
from emailstrings import *
from hrmsempdata import *

ACTIVE_EMP_STATUS = 'Active'
############################################################################################################
# Generic Interface methods
############################################################################################################
#Return all DCs as a drop-down, created for use in BCSPROJ (skill is DC-name)
@cache.cached(timeout=1800, key_prefix="getDCListForSelect")
def getDCListForSelect() :
    dcList = Departmant.query.all()
    dcSet = [(o.ID,o.DEPARTMENT_NAME)  for o in dcList]
    return sorted(dcSet,key=get2ndElm)

@cache.cached(timeout=1800, key_prefix="getDCLeadListForSelect")
def getDCLeadListForSelect() :
    dcList = getAllDCLeads()
    dcSet = [(o.EMPLOYEE_ID,o.OFFICE_EMAIL_ID)  for o in dcList]
    return sorted(dcSet,key=get2ndElm)

@cache.cached(timeout=1800, key_prefix="getAllManagersForSelect")
def getAllManagersForSelect() :
    allMgrList = getAllManagers()
    allMgrSet = [(o.EMPLOYEE_ID,o.OFFICE_EMAIL_ID)  for o in allMgrList]
    return sorted(allMgrSet,key=get2ndElm)

@cache.memoize(timeout=1800)
def getAllManagersInDCForSelect(email) :
    allMgrList = getAllManagersInDc(email)
    allMgrSet = [(o.EMPLOYEE_ID,o.OFFICE_EMAIL_ID)  for o in allMgrList]
    return sorted(allMgrSet,key=get2ndElm)

#Used above for sorted
def get2ndElm(elem) :
    return elem[1].lower()

############################################################################################################
# Managers, DCs, etc.
############################################################################################################
#ManagerINFO CHANGE
#Return all managers
@cache.cached(timeout=1800, key_prefix="getAllManagers")
def getAllManagers() :
    mgrList = ManagerInfo.query.all()
    mgrs = [] #Start with an empty set
    for m in mgrList :
        emp = Employee.query.filter_by(EMPLOYEE_ID = m.emp_id).first()
        if emp :
            mgrs += [emp]
        else :
            print("Manager Not found:" + m.name)
    return mgrs

#Get all Managers reporting a DC-Lead
@cache.memoize(timeout=1800)
def getAllManagersInDc(email) :
    #Get All Managers
    allManagers = getAllManagers()
    #Get Manager Reportees
    allReportees = getReportees(email)
    reporteeDict = { r.EMPLOYEE_ID:r.EMPLOYEE_ID for r in allReportees }
#    print(reporteeDict)
    #Filter Managers who are not reportees
    empList = []
    for m in allManagers :
        if m.EMPLOYEE_ID in reporteeDict.keys() :
#            print("Adding:" + m.OFFICE_EMAIL_ID + ":" + m.EMPLOYEE_ID)
            empList.append(m)
        else:
#            print("      Excluding:" + m.OFFICE_EMAIL_ID + ":" + m.EMPLOYEE_ID)
            pass            
    return empList

#SRINI: Method to improve on the *inDc to get a tree at ANY level, ignore DCs
#RECURSIVE METHOD IS BEST
@cache.memoize(timeout=1800)
def getAllManagersInTree(email, allManagers=None) : 
    #Get All Managers
    if not allManagers :
        allManagers = getAllManagers() 
    #Get Manager Reportees
    allReportees = getReportees(email)
    reporteeDict = { r.EMPLOYEE_ID:r.OFFICE_EMAIL_ID for r in allReportees }
#    print(reporteeDict)
    #Filter Managers who are not reportees
    empList = []
    for m in allManagers :
        if m.EMPLOYEE_ID in reporteeDict.keys() :
#            print("Adding:" + m.OFFICE_EMAIL_ID + ":" + m.EMPLOYEE_ID)
            empList.append(m)
            newEmpList = getAllManagersInTree(reporteeDict[m.EMPLOYEE_ID].lower(), allManagers ) 
            if newEmpList :
                empList += newEmpList
    return empList


#Return all DCs
@cache.cached(timeout=1800, key_prefix="getAllDCLeads")
def getAllDCLeads() :
    dcList = Departmant.query.all()
    dcs = [] #Start with an empty set
    dcempDict = dict() # For elimating dups
    for m in dcList :
        emp = Employee.query.filter_by(EMPLOYEE_ID = m.DC_LEAD).first()
        if emp :
            if (emp.EMPLOYEE_ID  not in dcempDict.keys()) :
                dcs += [emp]
    #            print(empToString(emp))
                dcempDict[emp.EMPLOYEE_ID] = 1
        else :
            print("DC-Lead Not found:" + m.DEPARTMENT_NAME)
    return dcs

@cache.memoize(timeout=1800)
def is_DCLead(dcleadEmail) :
    #get the Emp Object of the lead
    dcEmp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(dcleadEmail)).first()
    if not dcEmp :
        return False
    #Get all the departments he is the DC-Lead for
    dcList = Departmant.query.filter_by(DC_LEAD =  dcEmp.EMPLOYEE_ID).all()
#    print()
    if not dcList:
        return False # This employee is NOT a DC-Lead
    else :
        return dcList # This evaluates to true if not empty

#To be TESTED, added as its needed in Feedback-approval logic
@cache.memoize(timeout=1800)
def is_Manager(leadEmail) :
    #get the Emp Object of the lead
    emp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(leadEmail)).first()
    if not emp :
        return False
    #Get all the departments he is the DC-Lead for
    mList = ManagerInfo.query.filter_by(emp_id =  emp.EMPLOYEE_ID).all()

    if not mList:
        return False # This employee is NOT a Manager
    else :
        return mList # This evaluates to true if not empty

#Hard Code it for now, should be in RBAC
@cache.memoize(timeout=1800)
def is_countryManager(leadEmail) :
    if leadEmail == "sridhar.kalyanam@msg-global.com" or \
        leadEmail == "sriram.krishnan@msg-global.com" or \
        leadEmail == "srinivas.kambhampati@msg-global.com" :
#        leadEmail == "suresh.ranganathan@msg-global.com" :
        return True
    return False


#Given an employee, get DC-Lead's emp no.
@cache.memoize(timeout=1800)
def getDcLeadEmpNum(emp_id) :
    emp = Employee.query.filter_by(EMPLOYEE_ID = emp_id).first()
    if not emp :
        print("NOT FOUND: Employee with ID:" + str(emp_id))
        return "113"
    if not emp.departmant :
        print("NOT FOUND: Department for Employee with ID:" + str(emp_id))
        return "113"
    return emp.departmant.DC_LEAD

############################################################################################################
# Employee Groups/sets
############################################################################################################
@cache.cached(timeout=1800, key_prefix='all_employees') #Time for half a day, if an employee is added, it will showup next day morning
def getAllEmployees() :
    return Employee.query.filter_by(Status = ACTIVE_EMP_STATUS).all() 
    
#Return all employees in a DC. Input Paramenter is the DC-ID
@cache.memoize(timeout=1800)
def getEmployeesInDC(dcID) :
    emps = Employee.query.filter_by(Status = ACTIVE_EMP_STATUS).filter_by(DEPARTMENT_ID = dcID).all()
    return emps

#Return all employees in a DC. Input Paramenter is the DC-ID
@cache.memoize(timeout=1800)
def getDCEmpSetForSelect(dcleadEmail) :
    retval = getDCEmpSet(dcleadEmail)
    if retval :
            return getSelectSetFromEmpList(retval)
    return [('Not a DC Lead','Not a DC Lead' )]

#Return all employees in a DC. Input Paramenter is the DC-ID
@cache.memoize(timeout=1800)
def getReporteeSetForSelect(mgrEmail) :
    retval = getDCEmpSet(dcleadEmail)
    if retval :
            return getSelectSetFromEmpList(retval)
    return [('Not a DC Lead','Not a DC Lead' )]

#Why two of these?
#Return all employees in a DC. Input Paramenter is the DC-ID
@cache.memoize(timeout=1800)
def getReporteeSetForSelect(mgrEmail) :
    retval = getDCEmpSet(mgrEmail)
    if retval :
            return getSelectSetFromEmpList(retval)
    return [('','' )]


#Return all employees in any of the DCs by this DC-Lead. Input Paramenter is the DC-email ID
@cache.memoize(timeout=1800)
def getDCEmpSet(dcleadEmail) : # All members of all the DCs this person is a lead
    #get the Emp Object of the lead
    dcList = is_DCLead(dcleadEmail) # Returns the list (evaluates to True) or False
    if not dcList:
        return False # This employee is NOT a DC-Lead
    emps = []
    for dc in dcList : # each department
        emps += getEmployeesInDC(dc.ID)
    
    #Identify all DC-Leads who are the reportees of this DC-Lead (Sriram/Sridhar)
    dcEmpId = getEmpIdByEmail(dcleadEmail) # (Sridhar or Sriram)
    alldc = getAllDCLeads()
    for dcl in getAllDCLeads() :
        if dcl.Manager_ID == dcEmpId :
            emps += [dcl]
    return emps

#Set of emails for "Select" drop-downs in UI
#TODO: Use getSelectSetFromEmpList after testing
@cache.memoize(timeout=1800)
def getEmailSetForSelect() :
    elist = getAllEmployees()
    hrmsemailSet = [(o.OFFICE_EMAIL_ID.lower(),o.OFFICE_EMAIL_ID.lower())  for o in elist]
    return sorted(hrmsemailSet)

#Set of emails for "Select" drop-downs in UI
@cache.memoize(timeout=1800)
def getSelectSetFromEmpList(elist) :
    hrmsemailSet = [(o.OFFICE_EMAIL_ID.lower(),o.OFFICE_EMAIL_ID.lower())  for o in elist]
    return sorted(hrmsemailSet)


############################################################################################################
# Get Employee details, manager, by email, emp_id, liferay_id, etc.
############################################################################################################
#Get Employee Object, given the emp_id
@cache.memoize(timeout=1800)
def getEmployeebyId(emp_id) :
    return Employee.query.filter_by(EMPLOYEE_ID = emp_id).first()

@cache.memoize(timeout=1800)
def getEmployeeEmail(emp_id) :
    emp = Employee.query.filter_by(EMPLOYEE_ID = emp_id).first()
    if emp :
        return emp.OFFICE_EMAIL_ID.lower()
    return ""

@cache.memoize(timeout=1800)
def getEmpIdByEmail(emailid) :
    emp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(emailid)).first()
#    emp =  Employee.query.filter_by(OFFICE_EMAIL_ID = emailid).first()
    if not emp :
        return False
    return emp.EMPLOYEE_ID

@cache.memoize(timeout=1800)
def getEmpIdIntByEmail(emailid) :
    emp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(emailid)).first()
#    emp =  Employee.query.filter_by(OFFICE_EMAIL_ID = emailid).first()
    if not emp :
        return False
    return int(emp.EMPLOYEE_ID)

#### ManagerINFO CHANGE
#Get employee from emp_id
@cache.memoize(timeout=1800)
def getReportingManagerEmpNum(emp_id) :
    emp =  getEmployeebyId(emp_id)
    if emp :
        return emp.Manager_ID
    else :
        return False
#    (mgr, dept) = emp.Manager_ID.split('-') # Need to see what this is, has two numbers with a hyphen in between, looks for manager_info table
#    mgrInfoObj = ManagerInfo.query.filter_by(ID=mgr).first() # Get manger Object
#    return mgrInfoObj.emp_id


############################################################################################################
# For implementing 2nd level approval
############################################################################################################
#Lets rename to getReportingManagerByEmail
@cache.memoize(timeout=1800)
def getLineManager(empId) :
    #emp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(emailId)).first()
    emp = getEmployeebyId(empId)
    if emp : return emp
    print("Line Manager not found for:" + str(empId))
    return False    

@cache.memoize(timeout=1800)
def getLineManagerId(empId) :
    emp = getLineManager(empId)
    if emp : return emp.Manager_ID
    print("1st Line Manager not found for:" + str(empId))
    return False

@cache.memoize(timeout=1800)
def get2ndLineManagerId(empId) :
    emp = get2ndLineManager(empId)
    if emp : return emp.EMPLOYEE_ID
    print("Second Line Manager not found for:" + str(empId))
    return False

@cache.memoize(timeout=1800)
def get2ndLineManager(empId) :
    emp = getEmployeebyId(empId)
    if emp :
        managerId = emp.Manager_ID
        emp1 = getEmployeebyId(managerId)
        #Add Hard-Code for stopping 2nd level (for e.g. for Country Manager, e.g. empId!= 100)
        if emp1  :
            managerId = emp1.Manager_ID
            emp2 = getEmployeebyId(managerId)
            return emp2
    return False

@cache.memoize(timeout=1800)
def get2ndLineManagerName(empId) :
    emp = get2ndLineManager(empId) 
    if emp :
        return emp.FIRST_NAME + " " + emp.LAST_NAME
    else :
        return "No 2nd Level Manager"

#Return all employees directly reporting a manager. Input Paramenter is the manager email ID 
#TODO: Write this correctly so that goalSheetForManager in goaldisplay.py will work
@cache.memoize(timeout=1800)
def getReportees(email) :
    #Get manager Object
    mgrEmpID = getEmpIdByEmail(email)
    if not mgrEmpID :
        return False
    
    #the ID from ManagerInfo table for this manager
    #Loop through all employees, split the field and compare
    empList = Employee.query.filter_by(Status = ACTIVE_EMP_STATUS).filter_by(Manager_ID=mgrEmpID).all() # All employees
    return empList
