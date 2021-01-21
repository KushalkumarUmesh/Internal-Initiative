"""
K.Srinivas, 2-Nov-2018

Project: Document Management Module
Description: This file defines the entity-class for the document. Its implemented in a generic way
so as to allow adding "file attachments" to existing functionality without changing the DB.

linkedToType : This is a unique number for each element type we might use it for, e.g. Task, Comment, etc.
linkedToId :Id of the element its linked to. Assumption is that one file is linked only to one element.

14-Nov-2018:Question: What if we want one file linked to multiple elements? - Leave it for now

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt
import logging

#Data from BCS. Most field-names are misleading...they are names from the BCS-Header
class HrmsDocument(db.Model):
    __bind_key__ = 'hrmsdocuments'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    empEmail = db.Column(db.String(200) ) #Employee email, after look-up by name
    fileName = db.Column(db.String(256)) # FileName as given by the user (for downloading)
    storedFileName = db.Column(db.String(1024)) # FileName as stored on disk
    dateStored = db.Column(db.DateTime)
    retentionDays = db.Column(db.Integer, default=0) #  number of days to keep
    encrypted = db.Column(db.Boolean(), default=False)
    archived = db.Column(db.Boolean(), default=False)

    #Lets store the linking information along with the file-data instead of the element data
    #This allows for adding file-attachments to existing elements without modifying them
    #Defined types: Task = 1, Comments = 2
    linkedToType = db.Column(db.Integer, default=0) # Task, Comment, etc.
    linkedToId = db.Column(db.Integer, default=0) # Id of Task, comment, etc.

#    dateAccessed = db.Column(db.DateTime) #Last accessed time ??





