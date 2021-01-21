"""
K.Srinivas, 4-Apr-2018

Project: Fix DCs and Managers for all employees

Description: This contains ONE-TIME use methods, meant for cleaning/maintaining HRMS data. 
=>All DCs and Managers have been fixed as of 6th April

SRINI: 10-Jul-2018: Review the file. It is NOT required anymore.
10-Sep:
=>All mobile numbers to be format checked, integration with textlocal.in SMS gateway  
"""
import logging

from hrmsmodels import Employee, ManagerInfo, Departmant, Country, State, Designation, Addres, Gender
from readmaillist import MsgEmailList
from realapp import appC, db, RepresentsInt
from notification import *
import hrmsdomain
import phonenumbers
import smsnotification

import pandas as pd

def getAllEmpCell():
    emps = hrmsdomain.getAllEmployees()
    messageList = []
    numList = []
    tcount = 0
    count  = 0
    for e in emps:
        tcount +=1
#        if not (e.EMPLOYEE_ID == '63' or e.EMPLOYEE_ID == '274'): continue
        if e.MOBILE_NO :
            (isValid, isIndian, national_number) =  isValidIndianPhoneNumber(e.MOBILE_NO)
            if isValid and isIndian :
                numList +=  ["91" + str(national_number)] # Store the number in international format without a +
                count += 1
            else :
                messageList += [e.OFFICE_EMAIL_ID + ":Invalid Mobile Number or not Indian Number"]
        else :
            messageList += [e.OFFICE_EMAIL_ID + ":Mobile Number unavailable"]
    print("Total=%d, Clean=%d" %(tcount, count))
    return (numList, messageList)

def isValidIndianPhoneNumber(num) :
    x = phonenumbers.parse(num, 'IN')
    return ( phonenumbers.is_valid_number(x) , x.country_code == 91, x.national_number )


#Not Used at this time, only for testing
def fixPhoneNumber(num) :
    x = phonenumbers.parse(num, 'IN')
    print(phonenumbers.is_valid_number(x))
    cstr = ""
    if x.country_code != 91 :
        cstr = "Not INDIA"
    else :
        cstr = "---------"
    print(cstr + ":" + str(x.national_number ) )
    
    return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

#emp.DEPARTMENT_ID
#Departmant

def fixManagers() :
    #Create a Manager Hash by email ID!!! No emp. number?
    #Get Manager -> email -> Object -> emp-number -> ManagerInfo-table->Select the 1st one -> get ID
    mgrIDHash = dict()
    mgrNameHash = dict()
    empNameHash = dict()
    df = pd.read_excel("EmpManagerMapping.xlsx") # Skip the first 4 lines, start from the 5th, ZERO indexed
    for i in range(len(df)) :
        s = df.iloc[i] # Get the row
        e = s.EmpID
        m = s.ManagerID
        if e == 113 : 
            e = 75 # Map Sridhar's emp number
#            print("Sridhar's ID Mapped")
        if m == 113 : 
            m = 75 # Map Sridhar's emp number
#            print("Sridhar's ID Mapped as manager")
        name= s.Name
        mName = s.ReportingManager
        mgrIDHash[e] = m # Name= key, email ID is the value
        mgrNameHash[e] = mName
        empNameHash[e] = name

    FIXREPORTING_MANAGER = True

    emps = Employee.query.filter_by(Status = None).all() 
    for emp in emps :
        if RepresentsInt(emp.EMPLOYEE_ID) :
            e = int(emp.EMPLOYEE_ID)
        else :
            continue
        if RepresentsInt(emp.Manager_ID) :
            m = int(emp.Manager_ID)
        else :
            continue
            
        if e in mgrIDHash.keys() : # Employee not in XLS file
            mx = mgrIDHash[e] # XLS-Manager
            if mx != m :
                mName = str(m)
                mxName = str(mx)
                if m in empNameHash.keys() : mName = empNameHash[m]
                if mx in empNameHash.keys() : mxName = empNameHash[mx]
                if not FIXREPORTING_MANAGER : #Print it
                    print("Manager Mismatch:" + str(e) +":" + empNameHash[e] + " HRMS=" + mName + " XLS:" + mxName)
                else : #Change it
                    print("CHANGING Manager:" + str(e) +":" + empNameHash[e] + " HRMS=" + mName + " XLS:" + mxName)                    
                    emp.Manager_ID = str(mx)
                    db.session.commit()  
        else :
            print("Employee Not Found in XLS File:" + str(e) +":" + str(emp.FIRST_NAME) + " " + str(emp.LAST_NAME))

    return

    # mgrList = ManagerInfo.query.all()
    # for m  in  mgrList :
    #     mgrIDHash[m.emp_id] = m.ID

    # #Create a Department HASH - by name
    # dcList = Departmant.query.all()
    # dcHash = dict()
    # for d in dcList:
    #     dcHash[d.DEPARTMENT_NAME] = d.ID


#     #Create an emp_hash with Key as the email ID in all lower-case
#     empHash = dict()
#     emps = Employee.query.all()
#     for e in emps :
#         empHash[e.OFFICE_EMAIL_ID.lower()] = e # Store the object

#     #Read exl-file and create a hash of employee-EMAILs, Depart and Manager
# #Name	Email	Responsibilities	DC Team	DC Manager	DC_Num
#     #Get Manager-emails from Responsibilities
#     #Get Keys
#     for i in range(len(df)) :
#         s = df.iloc[i] # Get the row
#         n = s.Responsibilities
#         e = s.Email.lower()
#         mgrNameHash[n] = 1 # Name= key, email ID is the value

#     for i in range(len(df)) :
#         s = df.iloc[i] # Get the row
#         n = s.Name
#         e = s.Email.lower()
#         if n in mgrNameHash.keys() :
#             mgrNameHash[n] = e # fix email ID is the value
#     if 1 in mgrNameHash.values() :
#         print("Some manager Was NOT FOUND!!")
#         return("Disaster...")

# #    for k in mgrNameHash.keys() :
# #        print(k + ":" + mgrNameHash[k])

#     found = 0
#     notfound = 0

#     for i in range(len(df)) :
#         s = df.iloc[i] # Get the row
#         e = s.Email.lower() 
#         m = s.Responsibilities
# #        print("emp:%s, Manager:%s" % (e,m))
#         if m in mgrNameHash.keys() :
#             me = mgrNameHash[m]
# #            print("emp:%s, Manager Email:%s" % (e,str(me)))
#             if me in empHash.keys() :
#                 mgrObj = empHash[me]
# #                print("emp:%s, Manager EmpID:%s" % (e,mgrObj.EMPLOYEE_ID))

#         if not mgrObj :
#             print("Manager for %s not found. Skipping Data Update" % (e) ) 
#             continue

#         mgrEmpID = mgrObj.EMPLOYEE_ID

#         if mgrEmpID not in mgrIDHash.keys() :
#             print("Manager Emp ID not found in mgrIDHash:email" + str(mgrEmpID) + ":" + str(mgrObj.OFFICE_EMAIL_ID))
#             return("See Console-2")
#         mgrID = mgrIDHash[mgrEmpID]
#         if e in empHash.keys() :
#             found += 1
#             emp = empHash[e]
#             mgr_dept =  emp.Manager_ID 
#             if mgr_dept : # If this present, better check
#                 (mgr, dept) = mgr_dept.split('-') # Need to see what this is, has two numbers with a hyphen in between, looks for manager_info table
#             else :
#                 print("Warning: No Manager-Department for " + e)
# #                continue
#             newDept = df[ df.Email == e ].DC_Num.data[0]
# #            print("NewDept:" + str(newDept) ) 
#             oldDept = emp.DEPARTMENT_ID
#             #REAL CHANGE - Execution COmpleted on 5-Apr-2018, no further DB-changes required
# #            emp.DEPARTMENT_ID = newDept
# #            emp.Manager_ID = str(mgrID) + '-' + str(newDept)
#             new_mgr_dept = str(mgrID) + '-' + str(newDept)
#             print("Employee %s:Old/New Dept:%s:%s, mgr-dept:old/new:%s:%s" % (e,str(oldDept), newDept,mgr_dept,new_mgr_dept   ))
#         else :
#             notfound += 1
#             print("Email:%s not found" % (e))
#     #db.session.commit()
#     return "See Console %d:%d" % (found, notfound)
#     #Check available Departs with department table

#emp.DEPARTMENT_ID
#Departmant
def fixDCs() :

    return("Remove ME TO UPDATE ONLY DC-DATA. USE fixManagers Instead..it fixes both ")

    #Create a Manager Hash by email ID!!! No emp. number?
    #Get Manager -> email -> Object -> emp-number -> ManagerInfo-table->Select the 1st one -> get ID
    mgrList = ManagerInfo.query.all()

    #Create a Department HASH - by name
    dcList = Departmant.query.all()
    dcHash = dict()
    for d in dcList:
        dcHash[d.DEPARTMENT_NAME] = d.ID

    #Create an emp_hash with Key as the email ID in all lower-case
    empHash = dict()
    emps = hrmsdomain.getAllEmployees()
    for e in emps :
        empHash[e.OFFICE_EMAIL_ID.lower()] = e # Store the object

    #Read exl-file and create a hash of employee-EMAILs, Depart and Manager
    df = pd.read_excel("Employee Email  Organisational_Structure_2018-04-04.xlsx") # Skip the first 4 lines, start from the 5th, ZERO indexed
#Name	Email	Responsibilities	DC Team	DC Manager	DC_Num
    found = 0
    notfound = 0
    for e in df.Email :
        e = e.lower()
        if e in empHash.keys() :
            found += 1
            empObj = empHash[e]
            newDept = df[ df.Email == e ].DC_Num.data[0]
#            print("NewDept:" + str(newDept) ) 
            oldDept = empObj.DEPARTMENT_ID
            #empObj.DEPARTMENT_ID = newDept
            print("Employee %s:Old/New Dept:%s:%s" % (e,str(oldDept), newDept ))
        else :
            notfound += 1
#            print("Email:%s not found" % (e))
    #db.session.commit()
    return "See Console %d:%d" % (found, notfound)
    #Check available Departs with department table


#Return all managers
def getAllEmpsWOManager() :
    #mgrList = ManagerInfo.query.all() # All Managers
    #dcList = Departmant.query.all() # All DCs
    empList = hrmsdomain.getAllEmployees() # All employees

    for emp in empList :
        dept = emp.departmant
        dc_emp =""
        dcLead =""
        mgrName =""
        mgrEmail =""
        if dept :
            dcName = emp.departmant.DEPARTMENT_NAME
            if emp.departmant.DC_LEAD :
                dc_emp = Employee.query.filter_by(EMPLOYEE_ID =  emp.departmant.DC_LEAD).first()
                if dc_emp :
                    dcLead = dc_emp.OFFICE_EMAIL_ID 

        mgr_dept =  emp.Manager_ID 
        if mgr_dept : # If this present, better check
            (mgr, dept) = mgr_dept.split('-') # Need to see what this is, has two numbers with a hyphen in between, looks for manager_info table
            mgrInfoObj = ManagerInfo.query.filter_by(ID=mgr).first() # Get manger Object
            if mgrInfoObj :
                mgrName = mgrInfoObj.name
                manager_emp = Employee.query.filter_by(EMPLOYEE_ID =  mgrInfoObj.emp_id).first()
                if manager_emp :
                    mgrEmail = manager_emp.OFFICE_EMAIL_ID
        if not dc_emp or not dcLead or not mgrName or not mgrEmail :
            print("Emp:%s, %s,%s,%s,%s" %(emp.OFFICE_EMAIL_ID,str(dc_emp),str(dcLead), str(mgrName),str(mgrEmail)  ))
    return "Completed"

#Method to read email list provided by Mukundan for BCS-Check and list out employees
# not found in HRMS Employee list by e-mail ID.    
def getEmpsNotInHRMS() :
    hrmsemailList =  getAllEmpEmails()
    msgObj = MsgEmailList(appC, []) 
    msgemailDict = msgObj.getEmailDict()
    allinfo = str(hrmsemailList)
    for e in msgemailDict :
        if e not in hrmsemailList :
            allinfo += "<p>%s not in HRMS</p>" % (e)
    return allinfo

def getAllEmpEmails() :
    empList = hrmsdomain.getAllEmployees()
    emailList = [e.OFFICE_EMAIL_ID.lower() for e in empList ]
    return emailList

def fixReportingManagerAll() :
    emps = Employee.query.all()
    for e in emps :
#        print("Processing:" + str(e.EMPLOYEE_ID))
        fixReportingManagerEmpNum(e.EMPLOYEE_ID)

def fixReportingManagerEmpNum(emp_id) :
    from hrmsdomain import getEmployeebyId
    emp =  getEmployeebyId(emp_id)
    mgr_dpt = emp.Manager_ID
    if not mgr_dpt :
        print("Mgr_dpt Null for:" + str(emp_id))
        return
    if '-'  not in mgr_dpt :
        return
    (mgr, dept) = emp.Manager_ID.split('-') # Need to see what this is, has two numbers with a hyphen in between, looks for manager_info table
    mgrInfoObj = ManagerInfo.query.filter_by(ID=mgr).first() # Get manger Object
    if not mgrInfoObj :
        print("MgrInfoObj Null for:" + str(emp_id))        
        return
    emp.Manager_ID = mgrInfoObj.emp_id
    db.session.commit()
    return
