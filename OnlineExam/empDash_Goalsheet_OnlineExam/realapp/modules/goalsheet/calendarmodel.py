"""
K.Srinivas, 3-Jul-2018

Project: Goal Sheet
Description: Model for implementation of the calendar module. The idea is that all flags
(what is allowed/not-allowed) are represented in the DB as flags. There is column for Auth-Level
that allows for filtering default flags by logged-in user. These default-flags
will be modified based on the sheet/goal/task status

TODO: None

KNOWN BUGs: None
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt


#Master-Data
class GoalCalendar(db.Model):
    __bind_key__ = 'goalsheet'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    phase = db.Column(db.String(80), nullable=False )  # Phase name
    phaseType = db.Column(db.Integer, default = 0) # Phase TYPE: Data-entry, Feedback, Feedback+Review, Review, Emp.Specific
    sheetStatus = db.Column(db.String(40), nullable=False, default="Assigned" )
    actionString = db.Column(db.String(80), nullable=False, default="No Action Required" )
    actionId = db.Column(db.Integer, default = 0) # 0 = Do nothing
    empEmail = db.Column(db.Integer,default = 0 ) # Non-Zero Number referres to an employee specific Phase, to handle exceptions
    description = db.Column(db.String(500), nullable=False ) 
    assessmentYear  = db.Column(db.String(10), nullable=False )
    dateStart = db.Column(db.DateTime) # Both days are INCLUSIVE
    dateEnd = db.Column(db.DateTime)

    authlevel = db.Column(db.Integer, default=0 )
    gs_enable_assignment = db.Column(db.Boolean(), default=False)

    # Sheet-Flags
    gs_enable_self = db.Column(db.Boolean(), default=False)
    gs_enable_approve = db.Column(db.Boolean(), default=False)
    gs_enable_end_year_self = db.Column(db.Boolean(), default=False)
    gs_enable_end_year_dc_approve = db.Column(db.Boolean(), default=False)
    gs_enable_end_year_closure = db.Column(db.Boolean(), default=False)

    # Goal-Flags
    goal_enable_task_approve = db.Column(db.Boolean(), default=False)
    goal_enable_edit = db.Column(db.Boolean(), default=False)
    goal_enable_approve = db.Column(db.Boolean(), default=False)

    # Task-Flags
    task_enable_update = db.Column(db.Boolean(), default=False)
    task_enable_delete = db.Column(db.Boolean(), default=False)
    task_enable_activity_edit = db.Column(db.Boolean(), default=False) # Also allows for marking it as complete

    #Task File -upload, ask-feedback flags, default set to true
    file_upload_enable = db.Column(db.Boolean(), default=True) # Enable File-Upload Button
    task_file_download_enable = db.Column(db.Boolean(), default=False) # Enable File-Upload Button
    ask_feedback_enable = db.Column(db.Boolean(), default=True) # Enable Ask-For-Feeback button

    task_enable_status_change = db.Column(db.Boolean(), default=False)

if __name__ == "__main__" :
#    db.drop('GoalCalendar')
    db.create('GoalCalendar')


#    goal_enable_submit_for_review = db.Column(db.Boolean(), default=False)
#    goal_enable_submit_mid_year = db.Column(db.Boolean(), default=False)
#    goal_enable_submit_end_year = db.Column(db.Boolean(), default=False)
#    goal_enable_task_create  = db.Column(db.Boolean(), default=True) # Leaving this as True by default
