"""
K.Srinivas, 23-Jul-2018

Project: Goal Sheet
Description: This is for functionality related to management of the goalsheet application itself
To start with, it contains view-methods for editing goal-sheet
TODO: 
a) 

KNOWN BUGs: None
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired, Length
from flask_login import login_required ,  current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash, url_for, session
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from realapp import app, db
from hrmsdomain import getDCLeadListForSelect, getEmployeebyId, getAllManagersForSelect, getAllManagersInDCForSelect
from goaldomain import getGoalSheetStatusForSelect, getGoalSheetsForDc, getGoalSheetsAll
from goalmodel import GoalSheet


##########################################################################################################################
#### GoalSheet Management s##############################
class GoalSheetForm(FlaskForm) :
    id = IntegerField()
    current_role = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)]  )
    designation = SelectField(u'Designation ', choices=[], default ='' )
    department =  SelectField(u'Designation ', choices=[], default ='' )
    assessingManager = SelectField(u'current_manager ', choices=[], default ='' )
    assessment_year = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)]  )
    status = SelectField(u'goalsheet_status ', choices=[], default ='' )
    Update = SubmitField('Add/Update')

@app.route('/goals/sheetupdate/<int:id>', methods=('GET', 'POST'))
@app.route('/goals/sheetupdate', methods=('GET', 'POST'))
@login_required
def sheetUpdate(id = -1, year = '2018-2019') : # id is the id of the GoalSection, goes as is into the object creation
    year = session['year']
    table = 'GoalSheet'
    cname = eval(table)
    if(id > 0) :
        sheet = cname.query.filter_by(id = id).first()

    empEmail = current_user.username.lower()

    #Only Admins and DC Leads allowed
    if not current_user.is_admin and not current_user.is_dclead :
        return redirect("unauthorized.html")

    if request.method == "POST" and id > 0 :
#        print(request.form)
        form = GoalSheetForm(request.form)  # Create an itemList from request.form, in case of post
        if current_user.is_admin :
            form.populate_obj(sheet)
        else :
            sheet.assessingManager = form.assessingManager.data
        db.session.commit()
        return redirect(url_for('sheetUpdate'))

    #Get the Task AGAIN from DB, discard all changes

    if(id > 0) :
        sheet = cname.query.filter_by(id = id).first()
        form = GoalSheetForm(obj=sheet)
    else :
        sheet = None
        form = GoalSheetForm()
        
#    form.assessment_year.choices = getTaskStatusForSelect()
#    form.assessingManager.choices = getDCLeadListForSelect()
    if current_user.is_admin :
        form.assessingManager.choices = getAllManagersForSelect()
        form.status.choices = getGoalSheetStatusForSelect()
        sheets = getGoalSheetsAll(year)
    else :
        form.assessingManager.choices = getAllManagersInDCForSelect(empEmail)
        form.status.choices = getGoalSheetStatusForSelect()
        sheets = getGoalSheetsForDc(empEmail,year)
        
    if sheet :
        form.emailId = getEmployeebyId(sheet.empId).OFFICE_EMAIL_ID
    itemSet = []
    for gs in sheets :
        itemSet += [{'emailId': getEmployeebyId(gs.empId).OFFICE_EMAIL_ID,  'status':gs.status ,\
            'current_manager': getEmployeebyId(gs.assessingManager).OFFICE_EMAIL_ID , \
            'year': gs.assessmentYear, 'title': gs.templateRef.title, 'id': gs.id}]

    #Set Flags
    return render_template('goalsheet/goalsheetedit.html', goalSheets = itemSet, form = form)



##########################################################################################################################
##########################################################################################################################
#Method to publish the results to end-users, used at the end of the Appraisal Cycle.
@app.route('/goals/publishResults', methods=('GET',))
@login_required
def publishResults(year = '2018-2019') : 
    if not current_user.is_admin :
        return redirect("unauthorized.html")

    #Get each goal-sheet where status=Completed
    sheetsList = GoalSheet.query.filter_by(status = 'Completed').filter_by(assessmentYear = year).all()
    #Copy MGMT-Rating into PUB, MGMT-Comments to PUB-Comments
    for gs in sheetsList :
        gs.finalRating = getRatingString(gs.l3Rating)
        print("Publishing for: " + str(gs.empId))
        #Set Manager-Comments Employee Visible = True ??
        gs.status = 'Closed'
        db.session.commit()
    #Set goal-Sheet status to Closed
    remainingSheets = GoalSheet.query.filter(and_(GoalSheet.status != 'Completed',GoalSheet.status != 'Closed' )).filter_by(assessmentYear = year).all()
#    return render_template("message.html", message="Assessment Results Published" )
    return render_template("message.html", message="Assessment Results Published for %d, remaining %d" % (len(sheetsList), len(remainingSheets) ) )

#Get Rating String from number
def getRatingString(intRating) :
    switchRatingToString = {
        "0":"Not Rated",                #  0 - invalid rating
        "1":"Pls Contact HR",           #  1 - Fail
        "2":"Can do better",            #  2 - Poor
        "3":"Good",                     #  3
        "4":"Very Good",                #  4
        "5":"Excellent",                #  5
        "6":"Outstanding",              #  6
    }
    if intRating in switchRatingToString.keys() :
        strRating = switchRatingToString[intRating]
        return strRating
    print("Invalid Rating found:" + str(intRating))
    return "Unavailable"
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/dropall', methods=('GET', 'POST'))
#@login_required
def dbReCreate() : # id of the GoalSection is passed here
#    if not current_user.is_admin :
#        return redirect("unauthorized.html")
#    db.drop_all(bind ='goalsheet')
    db.create_all(bind ='goalsheet')
#    fillDefaultsInCalendar()
#    getAllCalendarFlags()
#    getCalendarFlags(2)
    return("Printed Valid Phases")
#    return("Tables dropped an re-created")

@app.route('/goals/testmethod', methods=('GET', 'POST'))
#@login_required
def testMethod() : 
#    notifyFeedbackToEmployees() 
    return("Method called")