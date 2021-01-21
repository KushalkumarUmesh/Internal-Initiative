"""
K.Srinivas, 10-Apr-2018

Project: Goal Sheet
Description: This will contain the basic views for goal-sheet assignment. Objective is for folks to be able to input ASAP.


TODO: 
a) Prevent re-assignment of Goal-Sheet to the same person
b) Test-Mechanism to impersonate ANY DC-Lead
c) Test-Mechanism: Delete GoalSheet - Admin View
d) Create a DC View of Goal-Sheets of reportees
e) Each Goal-Sheet can be Approved or Returned.
    => Need "Comments" for  Return in "Manager comments" element of the goal-sheet
f) 

KNOWN BUGs: None
"""
import logging
from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required, current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash, session
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from realapp import app, db
from goaldomain import *
from hrmsempdata import getEmpDictbyEmail, getEmpDictbyEmpid
import os

##########################################################################################################################
#### Assign Goal and a team-member ##############################
class GoalSheetAssignmentForm(FlaskForm) :
    templateList = SelectField(u'Template to Assign', choices=[]  )
    candiateEmail = SelectField(u'Assign To Individual', choices=[], default ='' )
    addemail = SubmitField('Add') #   

class GoalSheetAssignmentFormFromFile(FlaskForm) :
    templateList = SelectField(u'Template to Assign', choices=[]  )
    item = FileField("Enter Value")
    submit = SubmitField('Upload') #   

#TODO: Make this ADMIN or DC only
#TODO: Allow for impersonating ANY DC for testing purposes
@app.route('/goals/assigngoals', methods=('GET', 'POST'))
@login_required
def assignGoals(year = '2018-2019') :
    year = session['year']
    user = current_user.username.lower()
    table = 'GoalSheet'
    cname = eval(table)
    form  = GoalSheetAssignmentForm(request.form)
    form.templateList.choices = getTemplateListForSelect()  # Fill-in templates
    if current_user.is_admin :
        form.candiateEmail.choices = getEmailSetForSelect()  + [("","")] # Fill in e-mails
    elif current_user.is_dclead : # must be a DC-Lead
        form.candiateEmail.choices = getEmpSetForSelect(user)  + [("","")] # Fill in e-mails
    else :
        return render_template('goalsheet/message.html', message = "You are not authorized to assign goals.")

    form1 = GoalSheetAssignmentFormFromFile(request.form)
    form1.templateList.choices = getTemplateListForSelect()  # Fill-in templates

    if request.method == 'POST':
        tempId = request.form['templateList']
        if request.form['addemail'] == 'Add' : 
            if request.form['candiateEmail'] :
                em = request.form['candiateEmail'].strip()
                if em : # Check after stripping, just be sure
                    flash(assignTemplate(em, tempId,user, year))
                else : 
                    flash("E-mail Selected is empty")
            else :
                flash("No e-mail Selected")
        #File-Upload needs to be handled separately as combining it with another submit is causing some issue in the libraries down below.
    if current_user.is_admin :
        sheets = GoalSheet.query.filter_by(assessmentYear=year).all()
    else: 
        empInfo = getEmpDictbyEmail(user)
        dcEmpId = int(empInfo["EMPLOYEE_ID"])
        sheets = GoalSheet.query.filter_by(assessingManager = dcEmpId).filter_by(assessmentYear=year).all()
    itemSet = []
    for gs in sheets :
        emp = getEmployeebyId(gs.empId)
        if emp :
            itemSet += [{'emailId': emp.OFFICE_EMAIL_ID,  'status':gs.status , 'year': gs.assessmentYear, 'title': gs.templateRef.title}]
        else :
            print("Goal Sheet found for non-existant emp:" + str(gs.empId))
    #print("ItemSet=" + str(itemSet))
    return render_template('goalsheet/goalsheetslist.html', goalSheets = itemSet, form = form, form1=form1)

#TODO: Validate the emails read from the file to be authorized 
@app.route('/goals/assigngoalsfromfile', methods=['POST'])
@login_required
def assignFromFile(year = '2018-2019') :
    year = session['year']

    print("In File-Upload..")
    user = current_user.username
    tempId = request.form['templateList']
    f = request.files['file']
    fname = secure_filename(f.filename)
    fullpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
    f.save(fullpath)
    flash(assignTemplateFromFile(fullpath, tempId, user,  year))
    return redirect(url_for('assignGoals'))

@app.route('/goals/deletegoalsheet/<em>', methods=('GET', 'POST'))
@login_required
def deleteGoalSheetForEmp(em, year = '2018-2019') :
    year = session['year']

    flash(deleteGoalSheet(em, year))
    return redirect(url_for('assignGoals'))

@app.route('/goals/managegoalsheets/<int:id>', methods=['GET'])
@app.route('/goals/managegoalsheets', methods=['GET'])
@login_required
def manageGoalSheets(id = -1) :
    if True :
        user = 'Kalyan.Chakravarthy@msg-global.com'
    else :
        user = current_user.username
    empInfo = getEmpDictbyEmail(user)
    table = 'GoalSheet'
    cname = eval(table)

    sheets = GoalSheet.query.filter_by(assessingManager = int(empInfo['EMPLOYEE_ID'])).filter_by(status = 'Assigned').all()
    itemSet = []
    for gs in sheets :
        itemSet += [{'emailId': getEmployeebyId(gs.empId).OFFICE_EMAIL_ID,  'status':gs.status , 'year': gs.assessmentYear, 'title': gs.templateRef.title, 'id': gs.id}]
    #print("ItemSet=" + str(itemSet))
    return render_template('goalsheet/managegoalsheets.html', goalSheets = itemSet )
    