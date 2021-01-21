from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import required, DataRequired, Length
from flask_login import login_required, current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for, session
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from realapp import app, db, ELEMENT_TYPE_TASK

from askfeedbackmodel import FeedbackFromAnyone
from hrmsdomain import getEmpIdByEmail, getEmailSetForSelect
from hrmsempdata import getEmpDictbyEmail
from askfeedbackdomain import *
from goaldomain import getAllTasksForSelect, getTaskById
import json

###############################################################################################################
#############################################Feedback Request ###############################################
class GiveFeedbackForm(FlaskForm) :
   
#    item = TextField("Enter a Group Name", [validators.data_required()])
#    itemdesc = TextAreaField("Description", [validators.data_required()])
    id = IntegerField()
    giverEmail = TextField(u'From ')
    relationship = TextField(u'Relation ')
    status = TextField(u'Status')
    role = TextField(u'Role ')
    task =TextField(u'Task')
    comment = TextField(u'Group Name')
    feedback = StringField(u'Your Feedback', widget=TextArea())
    submit = SubmitField('Submit') 


@app.route('/goals/givefeedback', methods=('GET', 'POST'))
@app.route('/goals/givefeedback/<int:id>', methods=('GET', 'POST'))
@login_required  #Without login, we don't know who it is
def giveFeedback(id = 0, year = '2018-2019') :
    year =  session['year']
    empEmail = current_user.username.lower()
    loginedInEmpId = getEmpIdByEmail(empEmail)

    #Get Info for the top-part : Emp-Name, number, Role, Designation, Department, Manager, IS_DC_LEAD?
    if request.method == "POST" : #and form.validate_on_submit():
        obj = GiveFeedbackForm(request.form)
        #Populate the fields
        ask = FeedbackFromAnyone.query.filter_by(id = id).first()
        ask.feedback = obj.feedback.data[0:998]
        ask.status = "FG"
        ask.empNotified = False #  Reset notified flag if already set
        db.session.commit()

    form = GiveFeedbackForm()  #Lets not take assessment year for now, but we default it nicely
    if id : 
        ask = FeedbackFromAnyone.query.filter_by(id = int(id)).first()        
        if ask :
            form = GiveFeedbackForm(obj=ask)  #Lets not take assessment year for now, but we default it nicely
            task = getTaskById(ask.elementId)
            if task :
                form.task.data = task.description

    allAsks = FeedbackFromAnyone.query.filter_by(giverEmail = empEmail).\
        filter_by(assessmentYear = year).all()
    #Get Task description for display
    for ask in allAsks :
        task = getTaskById(ask.elementId)
        if task :
            ask.taskdescription = task.description
        else :
            ask.taskdescription = "This Task has been deleted."

    return render_template('goalsheet/givefeedback.html', form = form, itemSet = allAsks)


###############################################################################################################
#############################################Feedback Request ###############################################

class AskFeedbackForm(FlaskForm) :
    id = IntegerField()
    fromEmail = SelectField(u'From ', choices=[], default ='' )
    relationship = SelectField(u'Relation ', choices=[], default ='' )
    task =SelectField(u'Task', choices=[], default ='')
    comment = StringField(u'Group Name', widget=TextArea())
    status = StringField(u'Status')
    submit = SubmitField('Submit') 

@app.route('/goals/askfeedback/<int:id>', methods=('GET', 'POST'))
@app.route('/goals/askfeedback', methods=('GET', 'POST'))
@login_required  #Without login, we don't know who it is
def askfeedbackAddUpdate(id = 0, year = '2018-2019') :  
    year =  session['year']
    empEmail = current_user.username.lower()
    loginedInEmpId = getEmpIdByEmail(empEmail)

    #Get additional details for the objects to be displayed (e.g. Task Name)
    if request.method == "POST" : #and form.validate_on_submit():
        obj = AskFeedbackForm(request.form)
        if id  : 
            newAsk = FeedbackFromAnyone.query.filter_by(id = int(id)).first() 
            print("Found ask=" + str(newAsk.id) )      
        else :
            newAsk = FeedbackFromAnyone()
#        obj.populate_obj(newAsk)
        #Populate the fields
        if  obj.task.data :
            newAsk.elementId = obj.task.data
            newAsk.relationship = obj.relationship.data
            newAsk.elementType = ELEMENT_TYPE_TASK
            newAsk.giverEmail = obj.fromEmail.data
            newAsk.comment = obj.comment.data
            newAsk.receiverEmail = empEmail
            newAsk.feedback = "No Feedback Yet"
            newAsk.dateRecorded = dt.datetime.now()
            newAsk.assessmentYear = year
            newAsk.status = "RQ"
            if not id:
                db.session.add(newAsk) # Add it to the data base if it was new
            db.session.commit()
        else :
            flash("Please select a valid Task for which you are requesting feedback.")
    form = AskFeedbackForm()   
    form.fromEmail.choices = getEmailSetForSelect() + [("","")] ##
    form.relationship.choices = getRelationshipsForSelect()##
#    form.role.choices = getRolesForSelect() ##
    form.task.choices = getAllTasksForSelect(empEmail,year ) + [("","")] ##

    if id  : 
        ask = FeedbackFromAnyone.query.filter_by(id = id).first()        
        if ask :
            print("Ask found" + ask.giverEmail)
            form = AskFeedbackForm(obj=ask)  #Lets not take assessment year for now, but we default it nicely
            form.fromEmail.choices = getEmailSetForSelect() ##
            form.fromEmail.data = ask.giverEmail ##
            form.relationship.choices = getRelationshipsForSelect(ask.giverEmail) ##
            form.relationship.data = ask.relationship 
#            form.role.choices = getRolesForSelect() ##
            form.task.choices = getAllTasksForSelect(empEmail,year )  ##
            form.task.data = str(ask.elementId)
            

    #Get a list of feedbacks already requested
    allAsks = allAsksForUser(empEmail, year)
    #Get Task description for display
    for ask in allAsks :
        print("Ask Element=" + str(ask.elementId))
        task = getTaskById(ask.elementId)
        if task :
            ask.taskdescription = task.description
        else :
            ask.taskdescription = "Task appears to be deleted"
    return render_template('goalsheet/askforfeedback.html',form = form,  itemSet = allAsks )

#For AJAX call to get Relationship from "giver" dropdown
@app.route('/goals/getRelationshipsJSON/<emailid>', methods=['GET'])
@login_required  #Without login, we don't know who it is
def getRelationshipsJSON(emailid, year = '2018-2019') :
    year =  session['year']

    #get firstname from e-mail
    relSelectList =  getRelationshipsForSelect(emailid)
    mydict = [r[0] for r in relSelectList ]
    return (json.dumps(mydict))


