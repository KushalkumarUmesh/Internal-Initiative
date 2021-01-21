"""
K.Srinivas, 10-Apr-2018

Project: BCS Projects
Description: This will contain the views loading BCS-XLS files into DB

TODO: 
a) DONE-This is being developed independently of the runapp.py at the top-level. To be integrated later.
b) DONE-Project -list , add, update. UI improvements are pending
b) DONE-Need methods and pages for Project-ROLE
c) DONE-Need pages for Account and Program - List/Add/Update/Delete
d) Link Account->Prog->Proj-Role

KNOWN BUGs: None
"""
import logging

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
from bcsorgstruct import *
from bcsdomain import *
from projdomain import *
from bcsmodel import *
from home import *
from bcsauthinterface import bcscheckauth
from documentmodel import HrmsDocument
from bcscheckclaims import checkBCSEmailsWithHRMS

class DataFilesUpload(FlaskForm) :
    claimdata = FileField("Select File")
    leavedata = FileField("Select File")
    orgdata = FileField("Select File")
    date = DateTimeField('End Date', format='%d-%m-%y')
    updateProjs = BooleanField(u'Update Projects and Roles',  default = False )
    submit = SubmitField('Upload') #   

#TODO: Disable after testing
@app.route('/bcsproj/loadbcsdata', methods=('GET', 'POST'))
@login_required
def loadbcsdata() : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    form  = DataFilesUpload(request.form)
    if request.method == 'POST':
        cf=request.files['file1']
        lf=request.files['file2']
        pf=request.files['file3']
        fname1 = secure_filename(cf.filename)
        claimfile = os.path.join(app.config['UPLOAD_FOLDER'], fname1)
        cf.save(claimfile)
        fname2 = secure_filename(lf.filename)
        leavefile = os.path.join(app.config['UPLOAD_FOLDER'], fname2)
        lf.save(leavefile)
        fname3 = secure_filename(pf.filename)
        orgfile = os.path.join(app.config['UPLOAD_FOLDER'], fname3)
        pf.save(orgfile)
        #Now these files are read and processed
        (error, nameHash) = readBCSOrgStructure(orgfile)

        #Check if the file was parsed correctly
        if error:
            flash(nameHash)
            return render_template('bcsdata/bcsdataupload.html',form = form)

        (error, mesg) = readBCSLeaveData(leavefile,nameHash)
        if error:
            flash(mesg)
            return render_template('bcsdata/bcsdataupload.html',form = form)

        (error, mesg) = readBCSClaimData(claimfile,nameHash)
        if error:
            flash(mesg)
            return render_template('bcsdata/bcsdataupload.html',form = form)

        if 'updateProjs' in request.form.keys() :
            flash(updateProjectsAndRoles())

        flash(checkBCSEmailsWithHRMS(nameHash))
        flash("Data Successfully loaded to DB.")  
    return render_template('bcsdata/bcsdataupload.html',form = form)


##############################################################################################
#### Stuff below this line is only for testing/one-time use purposes
##############################################################################################
##############################################################################################
#Methods for testing document mgmt methods (not used in the BCS-module, as yet)
#TODO: Disable after testing
@app.route('/bcsproj/savebcsFilesTest', methods=('GET', 'POST'))
@login_required
def savebcsFilesTest() : # id of the GoalSection is passed here
    import documentdomain as dd
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    form  = DataFilesUpload(request.form)
    if request.method == 'POST':
        cf=request.files['file1']
        lf=request.files['file2']
        pf=request.files['file3']
        fid = dd.saveFile(cf, empEmail, encrypt=False, retensionPeriod=0)
        fid = dd.saveFile(lf, empEmail, encrypt=False, retensionPeriod=0)
        fid = dd.saveFile(pf, empEmail, encrypt=False, retensionPeriod=0)
        return "Check the DB = " + str(fid)
    return render_template('bcsdata/bcsdataupload.html',form = form)

#Methods for testing documentat mgmt methods (not used in the BCS-module, as yet) -Download the file
#Get the metadata
#get the file
#get the file for reading - untested
@app.route('/bcsproj/downloadfiles', methods=('GET', 'POST'))
def getDownLoadedFilexxxx() :
    import documentdomain as dd
    #Get Meta Data
#    (a,b,c,d,e,f) = dd.getFileMetadata(4)
#    return c
    #get the file itself
#    return dd.getFile(2) 
    #To READ the file, on the server, 
#    fullFileName = os.path.join(app.config['UPLOAD_FOLDER'],c)
    #Open this file and read :-)



##############################################################################################
##############################################################################################

#TODO: Disable after testing
@app.route('/bcsproj/resetdb', methods=('GET', 'POST'))
@login_required
def bcstest() : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    return ("DB-Reset is disabled")

    db.drop_all(bind = 'bcsproj')
    db.create_all(bind = 'bcsproj')
    createDefaultsAccAndProg()
    baseDir = "C:\\Users\\kambhs\\Desktop\\Learning\\OpenPyxl\\BCS\\"
    nameHash = readBCSOrgStructure(baseDir + "Employee Email & Organisational_Structure_2018-05-11.xlsx")
    readBCSLeaveData(baseDir + "Leave_and_Flextime_Dates_21-05-2018.xlsx",nameHash)
    readBCSClaimData(baseDir + "Employee BCS Bookings_July18_02-08-2018.xlsx",nameHash)
    #Create Project and Role Data
    updateProjectsAndRoles()

#Drop down lists
    obj = ProjectType()
    obj.name = "POC"
    db.session.add(obj)
    obj = ProjectType()
    obj.name = "Maintenance"
    db.session.add(obj)
    obj = ProjectType()
    obj.name = "Development"
    db.session.add(obj)
    obj = ProjectType()
    obj.name = "Implementation"
    db.session.add(obj)
    obj = ProjectType()
    obj.name = "DevOps"
    db.session.add(obj)

    obj  = BillingModel()
    obj.name = "MonthlyFTE"
    db.session.add(obj)
    obj  = BillingModel()
    obj.name = "DailyEffort"
    db.session.add(obj)
    obj  = BillingModel()
    obj.name = "AlternateModel2"
    db.session.add(obj)
 
    obj  = StaffingStatus()
    obj.name = "Open"
    db.session.add(obj)
    obj  = StaffingStatus()
    obj.name = "Proposed"
    db.session.add(obj)
    obj  = StaffingStatus()
    obj.name = "Blocked"
    db.session.add(obj)
    obj  = StaffingStatus()
    obj.name = "Confirmed"
    db.session.add(obj)
    obj  = StaffingStatus()
    obj.name = "Shadowing"
    db.session.add(obj)
    obj  = StaffingStatus()
    obj.name = "AwaitingResourceJoin"
    db.session.add(obj)
 

    obj  = DeliveryStatus()
    obj.name = "AwaitingConfirmation"
    db.session.add(obj)
    obj  = DeliveryStatus()
    obj.name = "AwaitingStaffing"
    db.session.add(obj)
    obj  = DeliveryStatus()
    obj.name = "InProgress"
    db.session.add(obj)
    obj  = DeliveryStatus()
    obj.name = "Closed"
    db.session.add(obj)

    obj  = ContractStatus()
    obj.name = "Opportunity"
    db.session.add(obj)
    obj  = ContractStatus()
    obj.name = "Proposed"
    db.session.add(obj)
    obj  = ContractStatus()
    obj.name = "Signed"
    db.session.add(obj)
    obj  = ContractStatus()
    obj.name = "Terminated"
    db.session.add(obj)
    obj  = ContractStatus()
    obj.name = "Ended"
    db.session.add(obj)
    obj  = ContractStatus()
    obj.name = "OnHold"
    db.session.add(obj)

    db.session.commit()

    return ("Update completed")