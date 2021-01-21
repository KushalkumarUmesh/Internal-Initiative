"""
K.Srinivas, 19-Nov-2018

Project: Goal Sheet
Description: Business methods for ask-feedback-from-anyone functionality

TODO: Just started

KNOWN BUGs: None
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import or_
from realapp import db, cache, ELEMENT_TYPE_TASK
import datetime as dt
from askfeedbackmodel import FeedbackFromAnyone
from hrmsempdata import getEmpDictbyEmail
#Dup , TODO:Move to realapp/config

@cache.memoize(timeout=1800)
def getRelationshipsForSelect(emailid=None) :
    firstname="He(him)/She(her)"
    if  emailid :   
        empDict = getEmpDictbyEmail(emailid)
        if empDict and empDict['FIRST_NAME']:
            firstname = empDict['FIRST_NAME']
    return sorted([ ("",""),
        ('%s managed you directly' % (firstname) ,'%s managed you directly' % (firstname) ),\
        ('%s was your DC Lead' % (firstname),'%s was your DC Lead' % (firstname) ), \
        ('%s reported directly to you'% (firstname),'%s reported directly to you'% (firstname)), \
        ('%s reported in your DC'% (firstname),'%s reported in your DC'% (firstname)), \
        ("%s was senior to you but didn’t manage directly"% (firstname),"%s was senior to you but didn’t manage directly"% (firstname)), \
        ("You were senior to %s but didn’t manage directly"% (firstname),"You were senior to %s but didn’t manage directly" % (firstname)), \
        ('%s mentored you'% (firstname),'%s mentored you'% (firstname)), \
        ('%s was your mentee'% (firstname),'%s was your mentee'% (firstname)), \


        ('%s and you worked together in same DC '% (firstname) ,'%s and you worked together in same DC '% (firstname)), \
        ('%s and you worked together but reported in different DC '% (firstname) ,'%s and you worked together but reported in different DC '% (firstname)), \
        ])

@cache.cached(key_prefix="getRolesForSelect")
def getRolesForSelect() :
    return sorted([('Manager1','Manager1'),('Team Member1','Team Member1'), \
        ('Direct Reportee1','Direct Reportee1'),('Project Participant1','Project Participant1'), ('Its Complicated2','Its Complicated2') ])




def allAsksForUser(receiverEmail, year,visibleToEmp=True,authLevel=0 ) :
    allAsks = FeedbackFromAnyone.query.filter_by(receiverEmail = receiverEmail).\
        filter(or_(FeedbackFromAnyone.visibleToEmp == visibleToEmp , FeedbackFromAnyone.visiblityLevel <=  authLevel)). \
        filter_by(assessmentYear = year).all()
    return allAsks

def allAsksForUserByTaskId(receiverEmail, year, taskId,visibleToEmp=True,authLevel=0 ) :
    allAsks = FeedbackFromAnyone.query.filter_by(receiverEmail = receiverEmail).\
        filter_by(elementId = taskId).filter_by(elementType = ELEMENT_TYPE_TASK). \
        filter(or_(FeedbackFromAnyone.visibleToEmp == visibleToEmp , FeedbackFromAnyone.visiblityLevel <=  authLevel)). \
        filter_by(assessmentYear = year).all()
    return allAsks

def allAsksByTaskId(taskId,visibleToEmp=True,authLevel=0 ) :
    allAsks = FeedbackFromAnyone.query. \
        filter_by(elementId = taskId).filter_by(elementType = ELEMENT_TYPE_TASK). \
        filter(or_(FeedbackFromAnyone.visibleToEmp == visibleToEmp , FeedbackFromAnyone.visiblityLevel <=  authLevel)). \
        all()
    return allAsks

