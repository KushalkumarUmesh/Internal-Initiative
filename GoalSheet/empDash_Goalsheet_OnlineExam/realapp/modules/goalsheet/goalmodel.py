"""
K.Srinivas, 10-Apr-2018

Project: Goal Sheet
Description: Model (DB-link) 
TODO: None

KNOWN BUGs: None
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt
from calendardomain import getAssessmentYearStart,getAssessmentYearEnd


#Master-Data
class MasterGoalSection(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) 
    description = db.Column(db.String(1000), nullable=False )    
#    weight = db.Column(db.FLOAT)

class MasterGoal(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) 
    description = db.Column(db.String(1000), nullable=False )    
    goalSectionId = db.Column(db.Integer, db.ForeignKey("master_goal_section.id") ) 
    goalSectionRef = db.relationship('MasterGoalSection', primaryjoin='MasterGoal.goalSectionId == MasterGoalSection.id', backref='mastergoals')
    weight1 = db.Column(db.FLOAT) #Line Employee
    weight2 = db.Column(db.FLOAT) #DC Lead
#    weight3 = db.Column(db.FLOAT) #Anyother
    

#This is created then a set of goals is assigned to an employee
#Each instance off this is created and assigned to an employee along with creation of goals/sections linked to this one
class GoalSheet(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )    
    empId = db.Column(db.Integer) # Employee this is assigned to
    assessmentYear  = db.Column(db.String(10), nullable=False ) # For Display, can be derived from start/end dates, but make it easy
    assessingManager = db.Column(db.Integer, nullable=False ) 
    assignedBy = db.Column(db.Integer, nullable=False ) # For Tracing who assigned
    defaultStartDate = db.Column(db.String(10), nullable=False ) # Used for setting Defaults for ALL Goals/Goal-Sections, tasks, etc.
    defaultEndDate = db.Column(db.String(10), nullable=False ) # Used for setting Defaults for ALL Goals/Goal-Sections, tasks, etc.
    templateId = db.Column(db.Integer, db.ForeignKey("assignment_template.id") ) # Which template was assigned
    status = db.Column(db.String(40), nullable=False ) # Create a Lookup-Table here? is it really needed?
    managerComments = db.Column(db.String(1000) ) 

    templateRef = db.relationship('AssignmentTemplate', primaryjoin='GoalSheet.templateId == AssignmentTemplate.id', backref='assignmenttemplate')
    l1Rating = db.Column(db.String(10), default="Not Rated" ) # 1st Level Manager
    l2Rating = db.Column(db.String(10), default="Not Rated" ) # DC-Lead
    l3Rating = db.Column(db.String(10), default="Not Rated" ) # mgmt/HR
    calculatedRating = db.Column(db.String(10), default="Not Rated" ) # From recommendation engine, at some point

    finalRating = db.Column(db.String(10), default="Not Rated" ) # What is SHOWN to the user, same as l3 after publish
    finalComments = db.Column(db.String(1000) ) 
#    weight = db.Column(db.DECIMAL)
    score = db.Column(db.FLOAT, default=0)
    maxscore = db.Column(db.FLOAT, default=0) #To be computed and updated at the time of goal-sheet assignment

#Template that defines a set of Goals/Sections. When this is created once for each "type" of goal-sheet,
#All the required Goals/Sections are copied from master-data and linked to this ID
class AssignmentTemplate(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) # Name of the template .e.g. Principal Consultant Goals
    description = db.Column(db.String(1000), nullable=False )     # Description of the template
    finalized = db.Column(db.Boolean(), default=False)


#Template created from Master-Data and lists the goals in a given template
#We are not creating list of GoalSections as they are already linked with the assignment_template
class TemplateGoalList(db.Model): # A list of goals from Master, that should be copied for a givem Template
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True ) # Template ID
    templateId = db.Column(db.Integer, db.ForeignKey("assignment_template.id") )
    mastergoalId = db.Column(db.Integer, db.ForeignKey("master_goal.id") )
# To be added if we are going to copy the goals/goal-sections into a template, for not it is not required (THINK)
#    templategoalID = db.Column(db.Integer, db.ForeignKey("template_goal_section.id") )
   
#Template assigned to a employee
class GoalSection(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) 
    description = db.Column(db.String(1000), nullable=False )    
    empId = db.Column(db.Integer)
    dateStart= db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)
    goalSheetId = db.Column(db.Integer, db.ForeignKey("goal_sheet.id") ) 
#    weight = db.Column(db.FLOAT)
#    score = db.Column(db.FLOAT)

class Goal(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) 
    description = db.Column(db.String(1000), nullable=False )    
    empId = db.Column(db.Integer) #  # Only for convenience, we can always traverse via the goal-sheet->section
    targetSet  = db.Column(db.String(500))
    midYearTargetAchieved  = db.Column(db.String(500))
    midyearSelfAssessment  = db.Column(db.String(500))
    midYearManagerFeedback = db.Column(db.String(500))
    midYeardcFeedback = db.Column(db.String(500))
    midYearFinalFeedback = db.Column(db.String(500))

    selfRating = db.Column(db.Integer)
    managerRating = db.Column(db.Integer)
    dcLeadRating = db.Column(db.Integer)
    finalRating = db.Column(db.Integer)
    endYearTargetAchieved  = db.Column(db.String(500))
    endyearSelfAssessment  = db.Column(db.String(500))
    endYearManagerFeedback = db.Column(db.String(500))
    endYeardcFeedback = db.Column(db.String(500))
    endYearFinalFeedback = db.Column(db.String(500))

    managerFeedback = db.Column(db.String(500))
    dcFeedback  = db.Column(db.String(500))
    
    dateStart = db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)

    manadator = db.Column(db.Boolean(), default=True)
    masterGoalId = db.Column(db.Integer)
    dtAssigned = db.Column(db.DateTime)
    dtCompleted = db.Column(db.DateTime)
    dcapprovalstatus  = db.Column(db.String(40))
    hrintimationstatus  = db.Column(db.String(40))
    completionstatus = db.Column(db.String(40))
    goalSectionId = db.Column(db.Integer, db.ForeignKey("goal_section.id") ) 
    goalSheetId = db.Column(db.Integer, db.ForeignKey("goal_sheet.id") )   # Only for convenience, we can always traverse via the goal-section
    weight = db.Column(db.FLOAT, default=0)
    score = db.Column(db.FLOAT, default=0)

class Task(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    description = db.Column(db.String(1000), nullable=False )    
    dtAssigned = db.Column(db.DateTime)
    dtCompleted = db.Column(db.DateTime)
    dateStart = db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)
    manadator = db.Column(db.Boolean(), default=True)
    midyearSelfAssessment  = db.Column(db.String(500))
    endyearSelfAssessment  = db.Column(db.String(500))
    completionstatus = db.Column(db.String(40))
    personalNotes = db.Column(db.String(1000))
    goalId = db.Column(db.Integer, db.ForeignKey("goal.id") ) 
    goalSheetId = db.Column(db.Integer, db.ForeignKey("goal_sheet.id") ) # # Only for convenience, we can always traverse via the goal-section
    selfRating = db.Column(db.Integer, default=0) #Self
    selfAssessment = db.Column(db.Integer, default=0) #Self 
    l1Rating = db.Column(db.Integer, default=0) #L1 Manager
    l1Assessment = db.Column(db.Integer, default=0) 
    l2Rating = db.Column(db.Integer, default=0) #L2 - DC-Lead
    l2Assessment = db.Column(db.Integer, default=0)
    l3Rating = db.Column(db.Integer, default=0) #L3 - mgmt - Sridhar/Sriram/Suresh
    l3Assessment = db.Column(db.Integer, default=0)
    pubRating = db.Column(db.Integer, default=0) #What is show to the end user and/or used for calculation
    pubAssessment = db.Column(db.Integer, default=0) #pub* may not be used, putting it just to be sure
    weight = db.Column(db.FLOAT, default=0)
    score = db.Column(db.FLOAT, default=0)

class Activity(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    description = db.Column(db.String(1000), nullable=False )    
    task = db.Column(db.Integer, db.ForeignKey("task.id") ) 
    goalSheetId = db.Column(db.Integer, db.ForeignKey("goal_sheet.id") ) 

#############################################################################################33
# Model Methods
#############################################################################################33
def createGoalSheet(emp_id, template_id, assessingManager_empId, assigningManager_empId, year= "2018-2019"):
    newSheet = GoalSheet()
    newSheet.empId = emp_id
    newSheet.assessmentYear  = year
    newSheet.assessingManager = assessingManager_empId
    newSheet.assignedBy  = assigningManager_empId # For Tracing who assigned
    newSheet.defaultStartDate = getAssessmentYearStart(year) # Used for setting Defaults for ALL Goals/Goal-Sections, tasks, etc.
    newSheet.defaultEndDate = getAssessmentYearEnd(year) # Used for setting Defaults for ALL Goals/Goal-Sections, tasks, etc.
    newSheet.status = "Assigned" # THis needs to be clearly defined what our statuses are
    newSheet.templateId = template_id
    db.session.add(newSheet) # Create the object
    db.session.commit()
    return newSheet


#Create a new GoalSection from Master Goal Section and return the Object
def createGoalSectionFromMaster(mgs, emp_id, date_start,date_end, goalSheetId  ) : 
    ngs = GoalSection()
    ngs.title = mgs.title 
    ngs.description = mgs.description 
    ngs.empId = emp_id
    ngs.dateStart= date_start
    ngs.dateEnd = date_end
    ngs.goalSheetId = goalSheetId
    db.session.add(ngs) # Create the object
    db.session.commit()
    return ngs # Retun the newly created GoalSection Object

#Create a new GoalSection from Master Goal Section and return the Object
def createGoalFromMaster(mg, ngs_id, emp_id, date_start,date_end, goalSheetId, template_id  ) : 
    ng = Goal()
    ng.title = mg.title 
    ng.description = mg.description 
    ng.empId = emp_id
    ng.dtAssigned = dt.datetime.now()
    ng.dateStart= date_start
    ng.dateEnd = date_end
    ng.goalSheetId = goalSheetId
    ng.goalSectionId =  ngs_id # New Goal Section, copied before creating this one 
    ng.dcapprovalstatus  = "Not Approved"
    ng.hrintimationstatus  = "None"
    ng.completionstatus = "Assigned"
    ng.masterGoalId = mg.id # reference to the master-goal, needed for reconciliation/mass update
    if template_id == 2 : # DC-Lead template special case
        ng.weight = mg.weight2
    else:
        ng.weight = mg.weight1 # Defaults for templates 1, 3 and all new ones
        
    db.session.add(ng) # Create the object
    db.session.commit()
    return ng # Retun the newly created GoalSection Object

def getMasterGoalById(id) : # id is an INT!! don't use where string is needed
    return MasterGoal.query.filter_by(id = id ).first() # Assuming ID to be an INT!! Watchout

def getMasterGoalSectionById(id) :
    return MasterGoalSection.query.filter_by(id = id ).first() # Assuming ID to be an INT!! Watchout

#Update the status of ALL tasks in a goal-sheet to the value provided
#This is needed as part of the work-flow.
def updateAllTasksStatus(sheet, status) :
    #get all tasks
    tasks = Task.query.filter_by(goalSheetId = sheet.id).all()
    for t in tasks :
        t.completionstatus = status
    return
"""
    dcapprovalstatus  = "Not Approved"
    hrintimationstatus  = "None"
    completionstatus = "Assigned"
    goalSection = db.Column(db.Integer, db.ForeignKey("goal_section.id") ) 
"""

if __name__ == "__main__" :
    db.drop_all()
    db.create_all()




"""
# This is a copy of the MasterGoalSection
class TemplateGoalSection(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) #  # Title of the goal, copied from Master
    description = db.Column(db.String(1000), nullable=False )     # Description of the goal, copied from Master
    goalSection = db.Column(db.Integer, db.ForeignKey("master_goal_section.id") ) # Link to the Top-level
    templateID = db.Column(db.Integer, db.ForeignKey("assignment_template.id") )


# This is a copy of the MasterGoal
class TemplateGoal(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )    
    title = db.Column(db.String(240), nullable=False ) #  # Title of the goal, copied from Master
    description = db.Column(db.String(1000), nullable=False )     # Description of the goal, copied from Master
    goalSection = db.Column(db.Integer, db.ForeignKey("master_goal_section.id") ) # Link to future reference
    templateSectionID = db.Column(db.Integer, db.ForeignKey("template_goal_section.id") )
    templateID = db.Column(db.Integer, db.ForeignKey("assignment_template.id") ) # For convenience/reference, not needed as goal-section is there

#    qualification_type = db.relationship('QualificationType', primaryjoin='QualificationNameType.QUALIFICATION_TYPE_ID == QualificationType.ID', backref='qualification_name_types')

"""
