"""
K.Srinivas, 21-May-2018

Project: BCS in DB
Description: BCS-Data is read-in and loaded into the DB. This represents the DB-model for storing the BCS-data
The model is as follows:
a) Staging tables will be created for BCS-Claim and BCS-Leave data
    - This data will be augmented with emp. no and emp.e-mail
    - ??? Need a mapping XLS-file for handling incorrect e-mails in BCS-Org-data?? or Should I maintain
        BCS-Names  to emp. no and e-mail mapping statically in a table?
b) Project-table will created/updated from BCS-Claim data. Entries are never deleted
    - Additional information will be added via UI: Name, start-date, end-date, PM-name, etc.
    - Roles will be created from BCS-Data, additional role info will be added manually
        - Roles will have start-date and end-date
    - Project-status will include "Opportunity". This allows for tentatively booking resources for future
c) Emp. reservation information will maintained separately. Same role can have multiple people
    at different points of time.


TODO:


KNOWN BUGs: None
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt
import logging

#Data from BCS. Most field-names are misleading...they are names from the BCS-Header
class EmpBCSClaimData(db.Model):
    __bind_key__ = 'bcsproj'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    employeeCostCentre  = db.Column(db.String(20)) ########### Not used
    empBCSName = db.Column(db.String(80), nullable=False ) 
    globalCareerLevel  = db.Column(db.String(10)) ########### Not used
    projectCostCentre  = db.Column(db.String(20))########### Not used
    project_ID  = db.Column(db.String(20)) # Note: this is a field from BCS, not a real "ID"
    projectName = db.Column(db.String(200))  
    typeOfProject = db.Column(db.String(20)) ########### Not used
    projectStatus = db.Column(db.String(20)) ########### Not used
    typeOfContract = db.Column(db.String(100)) ########### Not used
    taskID = db.Column(db.String(20)) ########### Not used
    taskName = db.Column(db.String(200)) #Just "Task" in BCS-Data
    utilizationRelevant = db.Column(db.String(20)) 
    description = db.Column(db.String(200)) # Description column in day-booking
    bookingDate= db.Column(db.DateTime)
    duration = db.Column(db.String(10)) # Claim hours
    incentiveHrs = db.Column(db.String(10)) ########### Not used
    taskICRelevance = db.Column(db.String(10)) ########### Not used, put a as %
    billability = db.Column(db.String(20)) 
    taskBillability = db.Column(db.String(20)) ########### Not used
    interCompanyChargeability = db.Column(db.String(20)) ########### Not used
    #utilizationRelevant2 = db.Column(db.String(200)) ########### Not used, not sure why we have the same column 2nd time
    empEmail = db.Column(db.String(200) ) #Employee email, after look-up by name

#Data from BCS. Most field-names are misleading...they are names from the BCS-Header
class EmpBCSLeaveData(db.Model):
    __bind_key__ = 'bcsproj'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    department  = db.Column(db.String(20)) ########### Not used
    external_ID = db.Column(db.String(80), nullable=False ) 
    empBCSName = db.Column(db.String(80), nullable=False ) 
    subject  = db.Column(db.String(40))########### Not used
    dateStart= db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)
    duration = db.Column(db.String(10)) # Claim hours
    durationTimePeriod = db.Column(db.String(10)) # Claim hours
    budget  = db.Column(db.String(100)) ########### Not used
    status  = db.Column(db.String(30)) # [Blocked, Confirmed, Filled, Shadowing, AwaitingResourceRelease, AwaitingReourceJoin]
    description = db.Column(db.String(250))
    empEmail = db.Column(db.String(200) ) #Employee email, after look-up by name

#An account is for a customer or customer group
class MsgAccount(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    managerEmail = db.Column(db.String(200), nullable=False ) # email of the account manager
    accountName  = db.Column(db.String(50)) # Short Name  e.g. MSIG
    dateStart= db.Column(db.DateTime) #Defaults to 2000-01-01
    dateEnd = db.Column(db.DateTime) #Defaults to 2000-01-01
    description = db.Column(db.String(1000)) # General Notes
    contractCompany = db.Column(db.String(50)) # msg-global, systems, GIC
    contractRegion = db.Column(db.String(50)) # e.g. Benelux, Germany, SGP, India
    contractEntity = db.Column(db.String(50)) # msg Global, 
#  
#A Program is part of a account
class MsgProgram(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    accountId = db.Column(db.Integer, db.ForeignKey("msg_account.id") ) 
    managerEmail = db.Column(db.String(200), nullable=False ) # email of the project manager
    programName = db.Column(db.String(200)) # Project Name that is used, e.g. NN
    dateStart = db.Column(db.DateTime) #Defaults to 2000-01-01
    dateEnd = db.Column(db.DateTime) #Defaults to 2000-01-01
    description = db.Column(db.String(1000)) # General Notes
    accountObj = db.relationship('MsgAccount', primaryjoin='MsgProgram.accountId == MsgAccount.id', backref='progaccounts')

#Every project should have once instance
class MsgProject(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    programId  = db.Column(db.Integer, db.ForeignKey("msg_program.id") ) 
    accountId = db.Column(db.Integer, db.ForeignKey("msg_account.id") ) #Duplicated here for convenience
    pmEmail = db.Column(db.String(200), nullable=False ) # email of the project manager
    onsiteCounterpart = db.Column(db.String(200) ) # email of the oniste PM-counterpart
    projName  = db.Column(db.String(200)) # Project Name that is used, e.g. NN
    projBCSName  = db.Column(db.String(200)) # Project Name as obtained from BCS, needed for linking
    projType  = db.Column(db.String(100)) # Project POC, Maintenance, Development, implementation, DevOps
    bcsProjectID = db.Column(db.String(20)) # This is the PROJECT_ID from the BCS-FILE
    dateStart= db.Column(db.DateTime) #Defaults to 2000-01-01
    dateEnd = db.Column(db.DateTime) #Defaults to 2000-01-01
    travelCountry = db.Column(db.String(200)) # default travel country, For travel information purpose, 
    contractStatus = db.Column(db.String(30)) # [Opportunity, Proposed, Signed, Terminated, Ended, OnHold]
    deliveryStatus = db.Column(db.String(30)) # [AwaitingConfirmation,AwaitingStaffing, InProgress, Closed ]
    bcsProjectStatus = db.Column(db.String(20)) # From BCS-Data
    billability = db.Column(db.String(20)) # From BCS-Data
    projectCostCentre = db.Column(db.String(20)) # From BCS-Data
    billingModel =db.Column(db.String(20)) # Project Level[MonthlyFTE, DailyEffort, AlternateModel2]
    accountObj = db.relationship('MsgAccount', primaryjoin='MsgProject.accountId == MsgAccount.id', backref='accounts')
    programObj = db.relationship('MsgProgram', primaryjoin='MsgProject.programId == MsgProgram.id', backref='programs')

class ProjectRole(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    projectId = db.Column(db.Integer, db.ForeignKey("msg_project.id") ) 
    roleName = db.Column(db.String(100)) #Text name of the role
    roleSkillCat = db.Column(db.String(30)) # Skill category of the role e.g. Technical, Functional, Managerial
    roleSkill = db.Column(db.String(100)) # Specific Skill Desription e.g. Sr. Java Developer, Openshift
    dateStart= db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)
    careerLevel = db.Column(db.String(10)) # from BCS, the "reqiured level" or the "demand level"
    billingModel =db.Column(db.String(20)) # [MonthlyFTE, DailyEffort, AlternateModel2]
    billingPercent =db.Column(db.Integer) # 100% is the default
    staffingStatus  = db.Column(db.String(30)) # [Open, Proposed, Blocked, Confirmed, Shadowing, AwaitingReourceJoin]
    candidatesInPlay = db.Column(db.String(200)) #[comma separted list of names, till recruitment Module comes-in]
    assignedEmpId = db.Column(db.Integer) # In case an employee is assigned
    assignedEmpBcsName = db.Column(db.String(80) )  # In case an employee is assigned
    assigned_billLevel = db.Column(db.Integer) # Level Of the employee assigned
    projectObj = db.relationship('MsgProject', primaryjoin='ProjectRole.projectId == MsgProject.id', backref='programs')
#Employee Skill Category - from HRMS
#Employee-Status = Need to use from HRMS
#Employee-Career-level = in HRMS?? Same as the field we have in HRMS?

class Holidays(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    date = db.Column(db.DateTime)
    description = db.Column(db.String(200)) # Description of the Holiday
    year  = db.Column(db.String(4), nullable=False ) # Should work

#Create an empty Project, pre-filled with defaults
def createMsgProject() :
    proj = MsgProject()
    proj.accountId = 1 
    proj.programId = 1
    proj.projBCSName = "NA"
    proj.bcsProjectID = "NotApplicable"
    proj.bcsProjectStatus = "NA"
    proj.projectCostCentre = "NA"
    proj.dateStart = "2000-01-01" #Defaults to 2000-01-01
    proj.dateEnd = "2000-01-01" #Defaults to 2000-01-01
    return proj

#Drop down lists
class DeliveryStatus(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    name = db.Column(db.String(30))

class ContractStatus(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    name = db.Column(db.String(30))

class StaffingStatus(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    name = db.Column(db.String(30))

class BillingModel(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    name = db.Column(db.String(30))

class ProjectType(db.Model):
    __bind_key__ = 'bcsproj'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    name = db.Column(db.String(100))

"""
Who are not billable?
Who are the shadowing?
Who are working in multiple projects? 
    are they billing more than 100%
How to get credit for shadows?

Need employee-Log with each role-change
"""