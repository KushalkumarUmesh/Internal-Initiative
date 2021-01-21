"""
K.Srinivas, 12-Jun-2018

Project: Temp model to save/display a tree when the data is stored as a list with parent
Description: Demo program to show skills-level as a tree while storing it in a list with parent of each item

TODO: None

KNOWN BUGs: None
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt


#Master-Data
class ItemsKitchenSink(db.Model):
    __bind_key__ = 'skillstree'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    title = db.Column(db.String(240), nullable=False ) 
    description = db.Column(db.String(1000), nullable=False ) 
    parentId = db.Column(db.Integer, nullable=False ) #Not using foriegn key into the same table..too many bugs in MySql