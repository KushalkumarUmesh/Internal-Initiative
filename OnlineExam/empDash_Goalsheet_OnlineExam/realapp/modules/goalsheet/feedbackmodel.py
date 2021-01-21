"""
K.Srinivas, 09-Jul-2018

Project: Goal Sheet
Description: Model (DB-link) for feedback/Review phase. This is a generic model for storing
feedback at ANY point, including sheet/goal/task level feedback, return-comments, approve
comments, etc.

TODO: None

KNOWN BUGs: None
"""
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt


#Structure for all review/return feedbacks from everyone for sheet/goal/tasks
class GoalFeedback(db.Model):
    __bind_key__ = 'goalsheet'
    #Generic ID
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    #About which Item?
    elementId = db.Column(db.Integer, nullable=False ) # ID of the Sheet, goal, task
    elementType = db.Column(db.Integer, nullable=False ) # Is it a Sheet, goal, task Id?
    # Who, to Whom?
    giverEmpId = db.Column(db.Integer, nullable=False ) # Emp giving the feedback
    receiverEmpId = db.Column(db.Integer, nullable=False ) # Emp getting the feedback
    #What
    feedback = db.Column(db.String(1000), nullable=False )    
    # Who can see this?
    visibleToEmp = db.Column(db.Boolean(), default=False) # Is it visible to employee?
    visiblityLevel = db.Column(db.Integer, nullable=False ) # At what level can an employee see this?
    #When
    dateRecorded = db.Column(db.DateTime, nullable=False) # Date/Time when the feedback was given
#    phaseId = db.Column(db.Integer) # Phase ID - How can we find this?, Is it relavent?
    #Which Assessment Year?
    assessmentYear  = db.Column(db.String(10), nullable=False )

    #Notification flags, needed as notifications will go in batchs
    empNotified = db.Column(db.Boolean(), default=False) # Employee has been notified
    l1Notified = db.Column(db.Boolean(), default=False) # Manager/DC has been notified
    l2Notified = db.Column(db.Boolean(), default=False) # 2nd-line has been notified
    l3pNotified = db.Column(db.Boolean(), default=False) # HR has been notified
    renotifyEmp = db.Column(db.Boolean(), default=False) # Resend emails to employee 
    renotifyNonEmp = db.Column(db.Boolean(), default=False) # Resend emails to managers/others 
    

