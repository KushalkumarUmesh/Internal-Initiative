"""
28-Aug-2018
BCS-Check view methods. The methods are in bcscheckclaims.py
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from wtforms import *
from wtforms.validators import DataRequired, Length
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for, send_from_directory, render_template, redirect, request, flash
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import datetime
import os

from realapp import app, db
from bcscheckclaims import *
from home import *
from bcsauthinterface import bcscheckauth
from hrmsdomain import getEmailSetForSelect

class BcsDataView(FlaskForm) :
    candiateEmail = SelectField(u'Assign To Individual', choices=[], default ='' )
    date = DateTimeField('End Date', format='%d-%m-%y') # Take the month and Year from the date
    allEmps = BooleanField(u'Check ALL employees?',  default = False )
    emailToEmps = BooleanField(u'Send Email to All employees?',  default = False )
    emailToPmo = BooleanField(u'Send Email to PMO?',  default = False )
    submit = SubmitField('Calculate') #   

@app.route('/bcsproj/checkbcsdata', methods=['GET', 'POST'])
@login_required
def checkBcsData() :
    form = BcsDataView(request.form)
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    if request.method == 'POST':
        date = form.date.data # Get the date
        mrange = date.day
        year = date.year
        month = date.month
        if 'allEmps' in request.form.keys() :
            allErrors = []
            for e in getEmailSetForSelect() :
                print("Processing:"+ e[0])
                allErrors += [ "Processing:"+ e[0] ]
                (fullmsgbuf, bcsProjSummary, bcsUtilSummary) = validEmpBcsData(e[0] ,month, year, mrange )
                if 'emailToEmps' in request.form.keys() :
                    emailBCSInfoToEmp(e[0],date,fullmsgbuf, bcsProjSummary, bcsUtilSummary)
                allErrors += fullmsgbuf
            if 'emailToPmo' in request.form.keys() :
                if allErrors : # Something was added, notify the PMO group
                    return emailBCSInfoToPMO (date, allErrors )
                return ("Surprise!! No errors found for any of the employees.")
        else :
            if request.form['candiateEmail'] :
                em = request.form['candiateEmail'].strip()
                if em : # Check after stripping, just be sure
                    empEmail = em
                (fullmsgbuf, bcsProjSummary, bcsUtilSummary) = validEmpBcsData(empEmail ,month, year, mrange )
                if 'emailToEmps' in request.form.keys() :
                    emailBCSInfoToEmp(empEmail, date, fullmsgbuf, bcsProjSummary, bcsUtilSummary)
            else : #No candidate, no "all", do nothing
                form.candiateEmail.choices = getEmailSetForSelect()  + [("","")] # Fill in e-mails
                return render_template("bcsdata/empdatacheck.html" , form = form)

        return render_template("bcsdata/empdatashow.html" , mesgSet = fullmsgbuf, \
            bcsProjSummary = bcsProjSummary, bcsUtilSummary = bcsUtilSummary )

    form.candiateEmail.choices = getEmailSetForSelect()  + [("","")] # Fill in e-mails
    return render_template("bcsdata/empdatacheck.html" , form = form)


##### UNUSED AT THIS POINT ####
#@app.route('/bcs/validempbcsdata', methods=['GET'])
#@login_required
"""
def validempbcsdata(month=5, year=2018, maxday=0 ) :
    empEmail = current_user.username.lower()

    fullmsgbuf = [] 
    if maxday:
        mrange = maxday # use day-of-month if specified
    else :
        mrange = calendar.monthrange(year,month)[1] #Take last day of the month

#    for e in empEmailList : 
    fullmsgbuf = validEmpBcsData(empEmail,month, year, mrange )
    
    return formatMessageBuffer(fullmsgbuf)
"""