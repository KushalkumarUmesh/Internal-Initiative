"""
K.Srinivas, 11-May-2018

Project: Multiple (starting with OnlineExam, Goalsheet)
Description: Large methods from hrmsdomain.py are moved here. These were originally written to test 
the Alchmey connection HRMS-DB. By moving these here, the hrmsdomain file becomes smaller and it will be
easier to organize various "getemp..." methods

Common Methods
    getEmpDictbyEmail(email)
    getEmpDictbyEmpid(emp_id)


NOTE: 10-Jul-2018:Currently being used to do an HRMS-employee data check/notification

TODO: 
a) Define a full list of methods needed to support the requirements. This is an ongoing process but the initial few are identified.
b) DONE: Added comparision for encrypted fields in getEmpDict
c) DONE: Added an "Is_Active" filter for home-address

KNOWN BUGs: None
"""
import logging

from hrmsmodels import Employee, ManagerInfo, Departmant, Country, State, Designation, Addres, Gender
from realapp import appC, cache
from notification import notify
from emailstrings import *
import hrmsdomain

#For use in the Scheduler for NAG-emails
#10-Jul-2018: Currently in use in schduledjobs/hrmscron.py
def sendDataMissingMsgToAll(sendEmailToEmp=True) :
    empList = hrmsdomain.getAllEmployees() 
#    empList = ['srinivas.kambhampati@msg-global.com']
    count = 0
    respStr = ""
    empCount = 0
    for emp in empList : #For each employee
        (resp,retval) = dataMissingMsg(empObj = emp, email="", sendEmailToEmp=sendEmailToEmp)
        respStr += "<p>" + resp + "</p>"
        if retval : count += 1
        empCount += 1

    #Send a summary to myself- to be moved to config file
    retStr = "<p>Total %d employees (out of %d) notified.</p>" % (count, empCount) + respStr
    notify("srinivas.kambhampati@msg-global.com", "HRMS: Data Update Status", retStr ,  templateId="-1")
    return (htmlhead + retStr + respStr + htmlfooter)

#Called for notify employee if some critical data is missing
#NOTE: Sends e-mail notification to the employee
def dataMissingMsg(**kwargs) :
    if kwargs["email"] :
        email  = kwargs["email"]
        msgDict = getEmpDictbyEmail(email) #If we got an e-mail ID
    elif kwargs["empObj"] :
        emp = kwargs["empObj"] 
        msgDict = getEmpDictbyObj(emp) # If we got an emp-object
        email = emp.OFFICE_EMAIL_ID
    else :
        #Do Nothing
        print("No valid Arguments")
        return ("No valid Arguments",False)

    sendEmailToEmp = False
    if "sendEmailToEmp" in kwargs.keys():
        sendEmailToEmp = kwargs["sendEmailToEmp"]

    #For absolute SAFETY, check if the domain is correct, else return False
    if '@' in email :
        (name, domain) = email.split('@')
        if domain:
            domain = domain.lower()
            if domain != 'msg-global.com' :
                return ("Invalid Email:" + email,False)         
        else :
            return ("Invalid Email:" + email, False)
    else :        
        return ("Invalid Email:" + email, False)  
    
    num = 0 # No of items per line
    errNum = 0 # No. of errors found
    #Start creating the formated output
    retStr = "<table border='1'>"
    errStr = "" # Put errors separately, att to the top
    msgStr = "<tr><td style=\"padding-left:5px;\">"
    lasttr = 0
    for k in msgDict.keys() :
        if msgDict[k] == "Not Available" :
            msgStr +=  "%s:<a><b style=\"color:red;\">%s</b></a>" %(k,msgDict[k] )
            errNum += 1 # Some error occured
        else :
            msgStr +=  "%s:%s" %(k,msgDict[k] )
        num += 1
        if not num % 3 :
            msgStr += "</td><tr><td style=\"padding-left:5px;\">"
            lasttr = 1
        else :
            msgStr += "</td><td style=\"padding-left:5px;\">"
            lasttr = 0
    retStr += msgStr
    if not lasttr :
        retStr += "</tr>"
    retStr += "</table>"

    if (errNum and sendEmailToEmp) :
        message = htmlhead + hrmsdatacheck + retStr + hrmsfooter + htmlfooter
        notify(email, "HRMS: Data Update Required", message ,  templateId="-1")
#        print(email + " HRMS: Data Update Required "+ message )
        return ("Notification sent to:" +   email, True) 
    if errNum :
        return htmlhead + hrmsdatacheck + retStr + hrmsfooter + htmlfooter 
    return ("Up to Date:" +   email, False )  


#Convenience Method
@cache.memoize(timeout=3600)
def getEmpDictbyEmail(email) :
    emp = Employee.query.filter(Employee.OFFICE_EMAIL_ID.ilike(email)).first()
    if emp :
        return getEmpDictbyObj(emp)
    return {}

#Convenience Method
@cache.memoize(timeout=3600)
def getEmpDictbyEmpid(emp_id) :
    emp = Employee.query.filter_by(EMPLOYEE_ID = emp_id).first()
    if emp :
        return getEmpDictbyObj(emp)
    return 'None'

@cache.memoize(timeout=3600)
def getEmployeeNameById(emp_id) :
    emp = Employee.query.filter_by(EMPLOYEE_ID = emp_id).first()
    if emp :
        return (emp.FIRST_NAME + " " + emp.MIDDLE_NAME + " " + emp.LAST_NAME)
    

#Return a dict with all the information about an employee, used in emp-profile
#and error checking
#TODO:ManagerINFO CHANGE
def getEmpDictbyObj(emp) :
    msgDict = {} # Fields Key-Value
    #Run each check and add to msgStr
    msgDict["FIRST_NAME"] = emp.FIRST_NAME
    msgDict["MIDDLE_NAME"] = emp.MIDDLE_NAME
    msgDict["LAST_NAME"] = emp.LAST_NAME

    msgDict["EMPLOYEE_ID"] = emp.EMPLOYEE_ID
    msgDict["OFFICE_EMAIL_ID"] = emp.OFFICE_EMAIL_ID
    msgDict["PERSONAL_EMAIL_ID"] = emp.PERSONAL_EMAIL_ID

    msgDict["DATA_OF_BIRTH"] = emp.DATA_OF_BIRTH
    msgDict["DATE_OF_JOINING"] = emp.DATE_OF_JOINING
    if emp.GENDER :
        msgDict["GENDER"] = Gender.query.filter_by(ID = int(emp.GENDER)).first().name
    else :
        msgDict["GENDER"] = "Not Available"

    msgDict["MOBILE_NO"] = emp.MOBILE_NO
    msgDict["EMERGENCY_NO"] = emp.EMERGENCY_NO
    msgDict["BLOOD_GROUP"] = emp.BLOOD_GROUP

    msgDict["ENGINEERING_OR_NON_ENGINEERING"] = emp.ENGINEERING_OR_NON_ENGINEERING
#    msgDict["TOTAL_RELEVANT_EXPERIENCE"] = emp.TOTAL_RELEVANT_EXPERIENCE
#    msgDict["TOTAL_RELEVANT_EXPERIENCE_DATE"] = emp.TOTAL_RELEVANT_EXPERIENCE_DATE

    tempname = emp.designation
    msgDict["DESIGNATION"] = 'Not Available'
    if tempname :
        msgDict["DESIGNATION"] = emp.designation.DESIGNATION_NAME

    tempname = emp.departmant
    msgDict["DEPARTMENT"] = 'Not Available'
    msgDict["DC_LEAD"] = 'Not Available'
    if tempname :
        msgDict["DEPARTMENT"] = emp.departmant.DEPARTMENT_NAME
        if emp.departmant.DC_LEAD :
            dc_emp = Employee.query.filter_by(EMPLOYEE_ID =  emp.departmant.DC_LEAD).first()
            if dc_emp :
                msgDict["DC_LEAD"] = dc_emp.OFFICE_EMAIL_ID 
            else :
                #This cannot happen?
                print("DC-Lead Not found: emp.departmant.DEPARTMENT_NAME=" + str(emp.departmant.DEPARTMENT_NAME))
                print("DC-Lead Not found: emp.departmant.DC_LEAD=" + str(emp.departmant.DC_LEAD))

#TODO:ManagerINFO CHANGE
    mgr_dept =  emp.Manager_ID 
    msgDict["MANAGER_NAME"] = 'Not Available'
    msgDict["MANAGER_EMAIL"] = 'Not Available'
    msgDict["MANAGER_EMPID"] = 'Not Available'
    """
    if mgr_dept : # If this present, better check
        (mgr, dept) = mgr_dept.split('-') # Need to see what this is, has two numbers with a hyphen in between, looks for manager_info table
        mgrInfoObj = ManagerInfo.query.filter_by(ID=mgr).first() # Get manger Object
        if mgrInfoObj :
            msgDict["MANAGER_NAME"] =mgrInfoObj.name
            msgDict["MANAGER_EMPID"] = mgrInfoObj.emp_id
            manager_emp = Employee.query.filter_by(EMPLOYEE_ID =  mgrInfoObj.emp_id).first()
            if manager_emp :
                msgDict["MANAGER_EMAIL"] = manager_emp.OFFICE_EMAIL_ID
    """
    msgDict["MANAGER_EMPID"] = emp.Manager_ID
    manager_emp = Employee.query.filter_by(EMPLOYEE_ID =  emp.Manager_ID).first()
    if manager_emp :
        msgDict["MANAGER_EMAIL"] = manager_emp.OFFICE_EMAIL_ID
        msgDict["MANAGER_NAME"] = manager_emp.FIRST_NAME + " " + manager_emp.LAST_NAME


    if emp.BANK_ACCOUNT_NO and emp.BANK_ACCOUNT_NO != 'IuSVD2DqOyM=':
        msgDict["BANK_ACCOUNT_NO"] = "Available"
    else :
        msgDict["BANK_ACCOUNT_NO"] = "Not Available"

    #Check UAN, PAN, PF, AADHAR -- Employee
    if emp.document_details:
        msgDict["AADHAR_NO"] = emp.document_details.AADHAR_NO
        msgDict["PAN_NO"] = emp.document_details.PAN_NO
        msgDict["PASSPORT"] = emp.document_details.PASSPORT_NO

        if emp.BANK_ACCOUNT_NO and emp.BANK_ACCOUNT_NO != 'IuSVD2DqOyM=':
            msgDict["BANK_ACCOUNT_NO"] = "Available"
        else :
            msgDict["BANK_ACCOUNT_NO"] = "Not Available"
        msgDict["UAN"] = emp.document_details.UAN_NO
        msgDict["PF_NO"] = emp.document_details.PF_NO

        msgDict["NAME_AS_PER_THE_PASSPORT"] = emp.document_details.NAME_AS_PER_THE_PASSPORT
        msgDict["PASSPORT_ISSUE_DATE"] = emp.document_details.PASSPORT_ISSUE_DATE
        msgDict["PASSPORT_EXPIRY_DATE"] = emp.document_details.PASSPORT_EXPIRY_DATE
        msgDict["PASSPORT_ISSUE_PLACE"] = emp.document_details.PASSPORT_ISSUE_PLACE

        #As values are encrypted, need to compare to find out if available
        if emp.document_details.AADHAR_NO and emp.document_details.AADHAR_NO != 'IuSVD2DqOyM=':
            msgDict["AADHAR_NO"] = "Available"
        else :
            msgDict["AADHAR_NO"] = "Not Available"

        if emp.document_details.PAN_NO and emp.document_details.PAN_NO != 'IuSVD2DqOyM=':
            msgDict["PAN_NO"] = "Available"
        else :
            msgDict["PAN_NO"] = "Not Available"

        if emp.document_details.UAN_NO and emp.document_details.UAN_NO != 'IuSVD2DqOyM=':
            msgDict["UAN"] = "Available"
        else :
            msgDict["UAN"] = "Not Available"

        if emp.document_details.PF_NO and emp.document_details.PF_NO != 'IuSVD2DqOyM=':
            msgDict["PF_NO"] = "Available"
        else :
            msgDict["PF_NO"] = "Not Available"

        if emp.document_details.PASSPORT_NO and emp.document_details.PASSPORT_NO != 'IuSVD2DqOyM=':
            msgDict["PASSPORT"] = "Available"
        else :
            msgDict["PASSPORT"] = "Not Available"

        #Check if the Documents were uploaded
        if emp.document_details.PASSPORT_DOC :
            msgDict["PASSPORT_DOC"] = "Available"
        else :
            msgDict["PASSPORT_DOC"] = "Not Available"

        if emp.document_details.AADHAAR_NO_DOC:
            msgDict["AADHAAR_NO_DOC"] = "Available"
        else :
            msgDict["AADHAAR_NO_DOC"] = "Not Available"
        if emp.document_details.PAN_NO_DOC :
            msgDict["PAN_NO_DOC"] = "Available"
        else :
            msgDict["PAN_NO_DOC"] = "Not Available"
    else :
        msgDict["AADHAR_NO"] = "Not Available"
        msgDict["PAN_NO"]  = "Not Available"
        msgDict["PASSPORT"] = "Not Available"
        msgDict["BANK_ACCOUNT_NO"] = "Not Available"
        msgDict["UAN"] = "Not Available"
        msgDict["PF_NO"] = "Not Available"
        msgDict["NAME_AS_PER_THE_PASSPORT"] = "Not Available"
        msgDict["PASSPORT_ISSUE_DATE"] = "Not Available"
        msgDict["PASSPORT_EXPIRY_DATE"] = "Not Available"
        msgDict["PASSPORT_ISSUE_PLACE"] = "Not Available"
        msgDict["AADHAAR_NO_DOC"]  = "Not Available"
        msgDict["PAN_NO_DOC"]  = "Not Available"
        msgDict["PASSPORT_DOC"] = "Not Available"

    #Lets add Home Address
    home = Addres.query.filter_by(EMPLOYEE_ID = emp.SID ).filter_by(ADDRESS_TYPE = '1').\
        filter_by(IS_ENABLE = '1').first()
    if home :
        msgDict["Home Address-LINE1"]  = home.LINE1
        msgDict["CITY"] = home.CITY
    else :
        msgDict["Home Address-LINE1"]  = "Not Available"
        msgDict["CITY"] = "Not Available"
        
    #msgDict["ROLE_OF_EMPLOYEE"] = emp.ROLE_OF_EMPLOYEE
    #msgDict["EMERGENCY_NO"] = emp.EMERGENCY_NO
    #msgDict["EMERGENCY_NO"] = emp.EMERGENCY_NO
    #msgDict["TOTAL_EXPERIENCE"] = emp.TOTAL_EXPERIENCE
    #Clean-up the values
    for k in msgDict.keys() :
        if not msgDict[k] or msgDict[k] == 'None' :
            msgDict[k] = "Not Available"
    if msgDict["MIDDLE_NAME"] == "Not Available" :
        msgDict["MIDDLE_NAME"] = "No Middle Name" #Middle name need not be there
    return msgDict


#########################################################################################
#Methods below could potentially be delted in future
#########################################################################################
#Method to print important information as a string.
#Used only in hrmsview.py for display of information
def empToString(emp) :
    msgDict = getEmpDictbyObj(emp)
    eName  = msgDict["FIRST_NAME"] + " " + msgDict["LAST_NAME"]
    eDept = "DC_LEAD:" + msgDict["DC_LEAD"] + ", Mgr:" + msgDict["MANAGER_NAME"]
    eStr = "ID:" + msgDict["EMPLOYEE_ID"] + " " + eName + " " + eDept
    return eStr

#For TEST only, for displaying profile page of ONE employee
def getEmpProfile(email) :
    return dataMissingMsg(email=email)


#Method is UNUSED. Could be used in future, left here
def notifyAllEmps(sendEmail=0) :
    #return getEmpDictbyEmail("sriniVas.kaMbhampati@msg-global.com")
    empList = hrmsdomain.getAllEmployees()
    allinfo = ""
    errCount = 0 # Check the count
    totalCount = len(empList)
    errEmailList = []
    for emp in empList : #For each employee
        #Run each check and add to msgStr
        msgDict =  getEmpDictbyObj(emp)
        num = 0 # No of items per line
        errNum = 0
        errStr = "" # Put errors separately, att to the top
        msgStr = ""
        for k in msgDict.keys() :
            if msgDict[k] == "Not Available" :
                errStr += "%s:%s" %(k,"Not Available" )
                errNum += 1
                if not errNum % 4 :
                    errStr += "\n"
                else :
                    errStr += "\t"
            else :
                msgStr +=  "%s:%s" %(k,msgDict[k] )
                num += 1
                if not num % 4 :
                    msgStr += "\n"
                else :
                    msgStr += "\t"
        if errStr :
            name = "Hi " + emp.FIRST_NAME + " " + emp.LAST_NAME + "\nPlease Update the Following:\n"
            emailMsg = name +  errStr
        if msgStr :
            emailMsg +=  "\n\nPlease verify and correct(if required) the following:\n" + msgStr
        print ('notify(%s, "Action Required:Correct HRMS Data", %s)' % (emp.OFFICE_EMAIL_ID, emailMsg) )
#        print(emaiMsg +"\n")
        allinfo += emailMsg +'<p>'
        #Notify employee
    return allinfo
