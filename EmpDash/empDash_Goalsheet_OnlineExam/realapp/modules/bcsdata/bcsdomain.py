"""
Change Log:
18-May-2018: File copied from BCSScripts, removed capitalization in file-name. The purpose is to move it into
the Flask+Alchemy framework. The general approach is to read the BCS-data and store it in DB.

27-Feb:Project as key to dicts has been changed to PRoject:Task as multiple bookings on same project with different tasks is possible.
This was done as part of a bug-fix
TODO: The entire things needs to be look at to improve efficiency
a) Attempted to work on an "update" of Claim data - But its not possible with errors. Dropped.
   Instead will provide a method deleted the data in a date-range, that can be manually be done
b) Need to populate the email column in Claim and Leave data : Need BCS-Name to email ID mapping
    -> Search for an existing entry?
    -> Use "intelligent e-mail ID" guess from HRMS db?
    -> Read from XLS-file?/Add field in HRMS? Add another table for mapping?
        -> Org_Structure XLS, downloaded from BCS gives this info
    
"""
import pandas as pd
import re
from bcsmodel import *
from realapp import db, app
import datetime
import calendar
from sqlalchemy import and_
from getxlsformat import GetXLSFormat
from notification import notifyGroup

##############################################################################################################
### Read BCS Data into staging Tables ########################################################################
##############################################################################################################
def readBCSClaimData(bcsInfile, nameHash) :
    app.logger.info("Reading file:" + bcsInfile)

    #Sanity Check the input file
    xlsfile = GetXLSFormat(bcsInfile)

    (error, message) = xlsfile.chkXLSFileFormat(('Employee cost centre','Employee',\
        'Global career level','Project cost centre', 'Project-ID',\
        'Project','Status','Type of project','Type of contract','Task ID','Task',\
        'Utilization relevant','Date','Duration', 'Incentive hrs', 'Billability',\
        'Task billablity'
        ))
    if error :
        return (error, message)

    xls = pd.ExcelFile(bcsInfile)
    mylist = xls.sheet_names
    sheet = mylist[0]
    app.logger.info("Pasrsing Sheet:" + sheet)
    bcs_df = xls.parse(sheet, na_filter=False)
#    bcs_df = pd.read_excel(bcsInfile)
    bcs_df = bcs_df.fillna('')
    app.logger.info("Num of rows:" + str(len(bcs_df)))
    
    #Locate Month-start and end-dates, then delete the data from DB first
    if not deletemonthlyclaimdata(bcs_df) :
        return (1, "Data crosses month or year boundry")

    numAdded = 0
    for i in range(0, len(bcs_df)) :
        obj = EmpBCSClaimData()
        s = bcs_df.iloc[i]
        if populateBCSClaim(obj, s) :
            if obj.empBCSName in nameHash.keys() :
                obj.empEmail = nameHash[obj.empBCSName]
            db.session.add(obj)
            numAdded += 1 # Lets record it
        if i % 500 == 0:
            db.session.flush()
    app.logger.info("Commiting %d Objects that were added.." % (numAdded))
    db.session.commit() #Commit all objects
    return(0, "Successfully updated Claim Data")

def populateBCSClaim(obj, s) :
    obj.employeeCostCentre  = s['Employee cost centre']
    obj.empBCSName = s['Employee']
    obj.globalCareerLevel  = s['Global career level']
    obj.projectCostCentre  = s['Project cost centre']
    obj.project_ID  = s['Project-ID']
    obj.projectName = s['Project']
    obj.projectStatus = s['Status']
    obj.typeOfProject = s['Type of project']
    obj.typeOfContract = s['Type of contract'] #Deal with NAN
    obj.taskID = s['Task ID']
    obj.taskName = s['Task']
    obj.utilizationRelevant = s['Utilization relevant']
    obj.description = ""
    if 'Description' in s.keys() :
        obj.description = str(s['Description'])[:199] #Deal with NAN, limit to 200 chars
    obj.bookingDate= s['Date']
    obj.duration = s['Duration']
    obj.incentiveHrs =s['Incentive hrs']
    obj.billability = s['Billability']
    obj.taskBillability = s['Task billablity']
    obj.interCompanyChargeability = s['Intercompany chargeability'] #Deal with NAN
    return True

#Delete ALL claim data for a given Month (and year)
def deletemonthlyclaimdata(bcs_df) :
    month = 0
    year = 0
    dateSeries = bcs_df['Date']
    for d in dateSeries :  #Extremely inefficent, brute force, but also safest course of action
        m = d.month
        y = d.year
        if not month : month = m
        if not year : year = y
    #Comment out this section for mass-month upload
        if month != m or year != y :
            app.logger.error("Multiple Months or years found in the data")
            return False   
    mrange = calendar.monthrange(year,month)[1]
    #Delete the data
    startDate = datetime.date(year,month,1)
    endDate = datetime.date(year,month,mrange)
    EmpBCSClaimData.query. \
        filter(and_(EmpBCSClaimData.bookingDate >= startDate, EmpBCSClaimData.bookingDate <= endDate) ).\
        delete(synchronize_session='evaluate')
    db.session.commit()
    return True

#Delete ALL leave data for the entire year
def deleteleavedata(bcs_df) :
    year = 0
    dateSeries = bcs_df['End']
    for d in dateSeries :  #Extremely inefficent, brute force, but also safest course of action
        y = d.year
        if not year : year = y
        if year != y :
            app.logger.error("Multiple years found in the data:%d:%d" % (year,y))
            return False   
    #Delete the data
    app.logger.info("Deleting all Leave Data for year:%d" % (year))
    startDate = datetime.date(year,1,1)
    print("StartDate:" + str(startDate))
    endDate = datetime.date(year,12,31)
    l = EmpBCSLeaveData.query. \
        filter(and_(EmpBCSLeaveData.dateStart >= startDate, EmpBCSLeaveData.dateStart <= endDate) ).\
            delete(synchronize_session=False)
    print("Deleted %d records." % l )
    db.session.commit()
    return True

#def readBCSClaimData(bcsInfile, proj_task_separator) :
def readBCSLeaveData(bcsInfile, nameHash) :
    app.logger.info("Reading file:" + bcsInfile)

    #Sanity Check the input file
    xlsfile = GetXLSFormat(bcsInfile)

    (error, message) = xlsfile.chkXLSFileFormat(('Department','External ID', 'Employee','Subject','Start','End','Budget', 'Duration','Duration (Time Period)', 'Status'))
    if error :
        return (error, message)

    xls = pd.ExcelFile(bcsInfile)
    mylist = xls.sheet_names
    sheet = mylist[0]
    app.logger.info("Pasrsing Sheet:" + sheet)
    bcs_df = xls.parse(sheet, na_filter=False)
    bcs_df = bcs_df.fillna('')
    app.logger.info("Num of rows:" + str(len(bcs_df)))

    #Delete all data for this year
    deleteleavedata(bcs_df) 

    for i in range(0, len(bcs_df)) :
        obj = EmpBCSLeaveData()
        s = bcs_df.iloc[i]
        # Popupate obj with s
        populateBCSLeave(obj, s) 
        if obj.empBCSName  in nameHash.keys() :
            obj.empEmail = nameHash[obj.empBCSName]
        db.session.add(obj)
#        app.logger.info("Adding:%d=%s, %s" % (i, s['Employee'], s['Date']))
#        db.session.commit() #Commit all objects
        if i % 500 == 0:
            db.session.flush()
    app.logger.info("Commiting Objects")
    db.session.commit() #Commit all objects
    return(0, "Successfully updated Leave Data")

def populateBCSLeave(obj, s) :
    obj.department  = s['Department']
    obj.external_ID = s['External ID']
    obj.empBCSName = s['Employee']
    obj.subject  = s['Subject']
    obj.dateStart= s['Start']
    obj.dateEnd = s['End']
    obj.budget  = s['Budget']
    obj.duration = s['Duration']
    obj.durationTimePeriod = s['Duration (Time Period)']
    obj.status  = s['Status']
#    obj.description = str(s['Description'])[:199]  
    obj.description = ""  # Description field has an issue in BCS dump

##############################################################################################################
### Process BCS Data into Projects and Roles #################################################################
##############################################################################################################

#Method to read BCS Claim data and update the list of Project and Roles
#This data will further need to be augmented from other sources, UI-Manual input, etc.
#What is the Unique KEY for a Project? Project-ID?
def updateProjectsAndRoles() : 
#    allproj = MsgProject.query.all() # Get all Projects
#    allRoles = ProjectRole.query.all() # May be we need to filter this at some point
    app.logger.info("Begin Updating Projects and Roles" )
    mesgList = ""
    allRows = EmpBCSClaimData.query.all() # Need to filter the latest month
    for r in allRows :
        proj = r.project_ID # Get the project ID
        if re.search('G103DC', r.projectName) :
            continue
        if r.billability == 'N/B' :
            continue
        projInDb = MsgProject.query.filter_by(bcsProjectID = proj).first() # Check if Project exists
        if not projInDb:
            #Create
            projInDb = MsgProject()
            populateMsgProject(projInDb, r)
            mesgList += "<p>" + "Creating New Project:ID=%s\tName=%s" % (projInDb.bcsProjectID, projInDb.projBCSName) + "</p>"
            db.session.add(projInDb)
            db.session.commit()
        #get all roles by ID, and name of the emp. decide to updated/add.
        #If an emp moves to another role with-in the same project, bad-luck will need manual update
        projRolls = ProjectRole.query.filter_by(projectId = projInDb.id, assignedEmpBcsName = r.empBCSName).first()
        if not projRolls:
            roleInDb = ProjectRole()
            populateProjectRole(roleInDb, r,projInDb)
            mesgList += "<p>" + "Creating New Role in:ID=%s\tName=%s" % (projInDb.bcsProjectID, projInDb.projBCSName) + "</p>"
            db.session.add(roleInDb)
            db.session.commit()
        #Else do nothing, the candidate is already has a role in the project
    app.logger.info("Done Updating Projects and Roles" )
    if mesgList : # Something was added, notify the PMO group
        notifyGroup ("PMO","New Projects/Roles added into Project-DB", mesgList , fromemail ="bcs-dataupload@msg-global.com")
    return mesgList

def populateProjectRole(obj, r,proj) :
    obj.roleName = "NotAvailable" #Text name of the role
    obj.projectId = proj.id 
    obj.dateStart= "2000-01-01"
    obj.dateEnd = "2000-01-01"
    obj.careerLevel = r.globalCareerLevel  # from BCS, the "reqiured level"
    obj.billingModel = "NotAvailable" # [MonthlyFTE, DailyEffort, AlternateModel2]
    obj.staffingStatus  = "Confirmed" # [Blocked, Confirmed, Filled, Shadowing, AwaitingResourceRelease, AwaitingReourceJoin]
    obj.candidatesInPlay = "NotAvailable" #[comma separted list of names, till recruitment Module comes-in]
    obj.assignedEmpId = 0 # In case an employee is assigned
    obj.assignedEmpBcsName = r.empBCSName # In case an employee is assigned
    obj.assgined_billLevel = 0 # Level Of the employee assigned
    obj.roleSkillCat = "Technical" # Skill category of the role e.g. Technical, Functional, Managerial
    obj.roleSkill = "NotAvailable" # Specific Skill Desription e.g. Sr. Java Developer, Openshift
    obj.billingPercent = 100 # 100% is the default


def populateMsgProject(obj, claimRow) :
    obj.pmEmail = "NotAvailable"
    obj.onsiteCounterpart = "NotAvailable" # email of the oniste PM-counterpart
    obj.programId  = 1 #Default
    obj.accountId = 1  #Default
    obj.projName  = str(claimRow.projectName)[:10] # Project Name that is used, e.g. NN, defaults to first 10 chars
    obj.projType  = "NotAvailable" # Project POC, Maintenance, Development, implementation, DevOps
    obj.projBCSName  = claimRow.projectName # Project Name as obtained from BCS, needed for linking
    obj.bcsProjectID = claimRow.project_ID # This is the PROJECT_ID from the BCS-FILE
    obj.dateStart = "2000-01-01"
    obj.dateEnd =  "2000-01-01"
    obj.customerName  = "NotAvailable"
    obj.programName  = "NotAvailable"
    obj.marketCountry = "NotAvailable"
    obj.contractStatus = "NotAvailable" # [Opportunity, Proposed, Signed, Terminated, Ended]
    obj.delivertStatus = "InProgress" # [AwaitingConfirmation,AwaitingStaffing, InProgress, Closed ]
    obj.bcsProjectStatus = claimRow.projectStatus # [Opportunity, Proposed, Signed, Terminated, Ended]
    obj.billability = claimRow.billability
    obj.projectCostCentre = claimRow.projectCostCentre
    obj.travelCountry = "NotAvailable" # default travel country, For travel information purpose, 
    obj.billingModel = "NotAvailable" # [MonthlyFTE, DailyEffort, AlternateModel2]


##############################################################################################################
### Create Default Account and Program for first use #########################################################
##############################################################################################################
def createDefaultsAccAndProg() :
    app.logger.info("Creating Default Account and Program")
    #Default Account
    accObj = MsgAccount()
    accObj.managerEmail = "sridhar.kalyaman@msg-global.com" # email of the account manager
    accObj.accountName  = "Default Account" # Short Name  e.g. MSIG
    accObj.dateStart= "2000-01-01" #Defaults to 2000-01-01
    accObj.dateEnd = "2099-01-01" #Defaults to 2000-01-01
    accObj.description = "Default Account for initial assignment" # General Notes
    accObj.contractCompany = "Not Set" # msg-global, systems, GIC
    accObj.contractRegion = "Not Set"
    accObj.contractEntity = "Not Set" # msg Global, 
    db.session.add(accObj)
    db.session.commit() #Commit all objects
    #Default Program
    progObj = MsgProgram()
    progObj.accountId = accObj.id
    progObj.managerEmail = "sridhar.kalyaman@msg-global.com" # email of the project manager
    progObj.programName = "Default Account"# Project Name that is used, e.g. NN
    progObj.dateStart = "2000-01-01" #Defaults to 2000-01-01
    progObj.dateEnd = "2099-01-01" #Defaults to 2000-01-01
    progObj.description = "Default Program for initial assignment" # General Notes
    db.session.add(progObj)
    db.session.commit() #Commit all objects
