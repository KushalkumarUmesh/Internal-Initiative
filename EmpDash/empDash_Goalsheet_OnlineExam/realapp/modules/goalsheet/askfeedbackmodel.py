"""
K.Srinivas, 18-Nov-2018

Project: Goal Sheet
Description: Model (DB-link) for requesting feedback from anyone for any task. This is different from the
feedback module that was meant for taking feedback from manager at the goal-level for evaluation purposes.

TODO: Just started

KNOWN BUGs: None
"""
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt

#Structure for all review/return feedbacks from everyone for sheet/goal/tasks
class FeedbackFromAnyone(db.Model):
    __bind_key__ = 'goalsheet'
    #Generic ID
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    #About which Item?
    elementId = db.Column(db.Integer, nullable=False ) # ID of the Sheet, goal, task
    elementType = db.Column(db.Integer, nullable=False ) # Is it a Sheet, goal, task Id?
    # Who, to Whom?
    giverEmail = db.Column(db.String(200), nullable=False ) # Emp giving the feedback
    receiverEmail = db.Column(db.String(200), nullable=False ) # Emp getting the feedback

    # Role of the giver e.g.: Project Manager, team member, etc.
    role = db.Column(db.String(200), nullable=True )
    # Relationship of the giver with the receiver e.g. colleague, direct reportee, reported directly, etc.
    relationship = db.Column(db.String(200), nullable=False )
    comment = db.Column(db.String(1000), nullable=False )  # Entered by person requesting feedback
    feedback = db.Column(db.String(1000), nullable=False ) # Entered by person giving feedback
    status = db.Column(db.String(30), nullable=False )     # Requested, Given, withdrawn?
    # Who can see this?
    visibleToEmp = db.Column(db.Boolean(), default=True) # Is it visible to employee?
    visiblityLevel = db.Column(db.Integer, default=0 ) # At what level can an employee see this?
    #When
    dateRecorded = db.Column(db.DateTime, nullable=False) # Date/Time when the feedback was given
    #Which Assessment Year?
    assessmentYear  = db.Column(db.String(10), nullable=False )

    #Notification flags, needed as notifications will go in batchs
    empNotified = db.Column(db.Boolean(), default=False) # Employee has been notified
    empNotifiedTime = db.Column(db.DateTime) # Employee last notified
    l1Notified = db.Column(db.Boolean(), default=False) # Manager/DC has been notified
    l2Notified = db.Column(db.Boolean(), default=False) # 2nd-line has been notified
    l3pNotified = db.Column(db.Boolean(), default=False) # HR has been notified
    renotifyEmp = db.Column(db.Boolean(), default=False) # Resend emails to employee 
    renotifyNonEmp = db.Column(db.Boolean(), default=False) # Resend emails to managers/others 
    

