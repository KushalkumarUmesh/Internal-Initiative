"""
K.Srinivas, 10-Apr-2018

Project: BCS Projects
Description: This will contain the views for Account/Program/Project/Project-Role.
Approach is as follows:
a) Copy GoalSection/Goals/Tasks and map to Accounts/Programs/Projects
b) Project-Role will need to be copied from projects itself.
c) Edit and change the variable names

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
from wtforms import *
from wtforms.validators import DataRequired, Length
#from flask_login import login_required ,  current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for, send_from_directory, render_template, redirect, request, flash
from flask_login import login_required, current_user
#ForFileUpload
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from realapp import app, db
from hrmsdomain import getEmailSetForSelect, getEmpIdByEmail
import re
from bcsdomain import *
from bcsorgstruct import *
from projdomain import *
from bcsauthinterface import bcscheckauth
from home import *
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
#### Project Form s##############################
class MsgProjectForm(FlaskForm) :
    id = IntegerField()
    projName  = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)]  )# Project Name that is used, e.g. NN
    pmEmail = SelectField(u'Select Account', choices=[], default ='' )  # email of the project manager
    projType  = SelectField(u'Select Account', choices=[], default ='' ) # Project POC, Maintenance, Development, implementation, DevOps
    billability = BooleanField(u'Billable',[validators.required()],  default = False ) # From BCS-Data # Check-box
    dateStart= DateTimeField('Start Date', [validators.required()],  format='%d-%m-%y')
    dateEnd = DateTimeField('End Date', [validators.required()], format='%d-%m-%y')
    deliveryStatus = SelectField(u'Select Account', choices=[], default ='' ) # [AwaitingConfirmation,AwaitingStaffing, InProgress, Closed ]
    contractStatus = SelectField(u'Select Account', choices=[], default ='' )# [Opportunity, Proposed, Signed, Terminated, Ended, OnHold]
    onsiteCounterpart = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)], ) # email of the oniste PM-counterpart

    accountId =  SelectField(u'Select Account', choices=[], default ='' )
    programId =  SelectField(u'Select program', choices=[], default ='' )
    travelCountry =  StringField(u'Description', validators=[DataRequired(), Length(max=200)], ) # default travel country, For travel information purpose, 
    billingModel = SelectField(u'Select Account', choices=[], default ='' ) # Project Level[MonthlyFTE, DailyEffort, AlternateModel2]

    #Display-only, non-editable at any point
    projBCSName  = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)],  ) # Project Name as obtained from BCS, needed for linking
    bcsProjectID = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)],   ) # This is the PROJECT_ID from the BCS-FILE
#    bcsProjectStatus = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)], ) # From BCS-Data
#    projectCostCentre = StringField(u'Onsite Manager Email ID', validators=[DataRequired(), Length(max=200)], ) # From BCS-Data

    submit = SubmitField('Add/Update') #   

#Display a List of Tasks for a given program, and allow add, update and delete
@app.route('/bcsproj/projaddupdateinprog/<int:id>', methods=('GET', 'POST'))
@app.route('/bcsproj/projaddupdateinprog', methods=('GET', 'POST'))
@login_required
def projListAddInProg(id = -1) : # id is the id of the GoalSection, goes as is into the object creation
    return projListAdd(id, inProg=True) 

#Display a List of Tasks for a given Account (or program), and allow add, update and delete
@app.route('/bcsproj/projaddupdate/<int:id>', methods=('GET', 'POST'))
@app.route('/bcsproj/projaddupdate', methods=('GET', 'POST'))
@login_required
def projListAdd(id = -1, inProg=False) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProject'
    cname = eval(table)
    if id > 0 :
        if inProg :
            acct = MsgProgram.query.filter_by(id = id).first()
            acctTitle = acct.programName
        else :
            acct = MsgAccount.query.filter_by(id = id).first()
            acctTitle = acct.accountName
    else :
        acctTitle = "All" 
    #form.pmE-mail = This needs to be a drop-down
    if request.method == "POST" : #and form.validate_on_submit():
        form = MsgProjectForm(request.form)  # Create an itemList from request.form, in case of post
        proj = createMsgProject()
        form.populate_obj(proj) 
        db.session.add(proj) # Add it to the data base
        db.session.commit()
    form = MsgProjectForm()  # Create an itemList from request.form, in case of post
    projectFormSetSelect(form)
    if id > 0:
        if inProg:
            allProjs = cname.query.filter_by(programId = id).all()
#            allProjs = cname.query.filter_by(programId = id).filter(db.not_(cname.projBCSName.contains("G103DC"))).all()
        else :
            allProjs = cname.query.filter_by(accountId = id).all()
#            allProjs = cname.query.filter_by(accountId = id).filter(db.not_(cname.projBCSName.contains("G103DC"))).all()
    else:
        allProjs = cname.query.filter(db.not_(cname.projBCSName.contains("G103DC"))).all() # Simply show all projects                    
    return render_template('bcsdata/projshowlist.html', itemSet = allProjs, form = form, projTitle = acctTitle)

def projectFormSetSelect(form) :
    form.pmEmail.choices =  getEmailSetForSelect()  + [("","")]
    form.deliveryStatus.choices =   getDeliveryStatusForSelect() # Fill in e-mails
    form.projType.choices = getProjectTypeForSelect() # Fill in e-mails
    form.accountId.choices =  getAccountsForSelect()  # Fill in e-mails
    form.programId.choices =  getProgramsForSelect() # Fill in e-mails
    form.contractStatus.choices = getContractStatusForSelect()  # Fill in e-mails
    form.billingModel.choices = getBillingModelForSelect() # Fill in e-mails    
    return

#Update a Given Task, ID is provided. Goal-ID and SHeet ID are already available, so no need for anything else
@app.route('/bcsproj/projupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def projUpdate(id) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProject'
    cname = eval(table)
    form = MsgProjectForm(request.form)  # Create an itemList from request.form, in case of post
    proj = cname.query.filter_by(id = id).first()
    acct = MsgAccount.query.filter_by(id = proj.accountId).first()
    acctTitle = acct.accountName
    if request.method == "POST" :
        form.populate_obj(proj)
#        app.logger.info(str(request.form)) 
        db.session.commit()
        return redirect(url_for('projListAdd', id=proj.accountId))
    allProjs = cname.query.all()
#    allProjs = cname.query.filter(db.not_(cname.projBCSName.contains("G103DC"))).all() # Fixed in the data load
    form = MsgProjectForm(obj=proj)  # Create an itemList from request.form, in case of post
    projectFormSetSelect(form)
    form.billability.value = re.search('BIL', proj.billability) or re.search('SHO', proj.billability)
    return render_template('bcsdata/projshowlist.html', itemSet = allProjs, form = form, projTitle = acctTitle, parentid=proj.accountId )

#TODO: Make this ADMIN only Once the goalsheet is approved
@app.route('/bcsproj/projdelete/<int:id>', methods=('GET', 'POST'))
@login_required
def projDelete(id) : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProject'
    cname = eval(table)
    proj = cname.query.filter_by(id = id).first()
    acctid = proj.accountId
    item = cname.query.filter_by(id = id ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    db.session.commit()
    return redirect(url_for('projListAdd'))

#########################################################################################################3
### This is Siddu's first Python code, that he has written on his own to render the files
# these static files...but leaving them here
class ProgramAjax(FlaskForm) :
    programId =  SelectField(u'Select program', choices=[], default ='' )

@app.route('/bcsproj/progdetails', methods=['GET'])
@login_required
def progdetails() : 
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

#    if request.method == "GET" :
#        app.logger.info("GET request: "+request.args.get('name1')) 
    accIdStr = request.args.get('name1')
    try :
        accId = int(accIdStr)
    except :
        return ("AccID Str is not an Int: " + accIdStr)
    acc = MsgAccount.query.filter_by(id = accId).first()
    if not acc :
        return ("No account with the number given:" + accIdStr)

    form = ProgramAjax()
    form.programId.choices = getProgramsForSelect(accId)
    retStr = render_template('bcsdata/progdetails.html', form = form)
#    print("Returning:" + retStr)
    return retStr


@app.route('/bcsproj/projhome', methods=('GET', 'POST'))
@login_required
def projhome() :
    return render_template('bcsdata/projhome.html' )

#Not Used
@app.route('/bcsproj/projnavhome', methods=('GET', 'POST'))
@login_required
def projnavhome() :
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))
    allAccts = MsgAccount.query.all()
    allProgs = MsgProgram.query.all()
    allProjs = MsgProject.query.all()
    #  allRoles = ProjectRole.query.all()
    return render_template( 'bcsdata/projnavhome.html', allAccts = allAccts, allProgs = allProgs, allProjs = allProjs )


##########################################################################################################################
#### Project-ROLE Form s##############################
##########################################################################################################################
class MsgProjectRoleForm(FlaskForm) :
    id = IntegerField()
    roleName = StringField(u'Role Title', validators=[DataRequired(), Length(max=200)],  ) #Text name of the role
    dateStart= DateTimeField('Start Date', [validators.required()],  format='%d-%m-%y')
    dateEnd = DateTimeField('End Date', [validators.required()], format='%d-%m-%y')
    roleSkillCat = SelectField(u'Select Skill Category', choices=[], default ='' ) # Skill category of the role e.g. Technical, Functional, Managerial
    roleSkill = SelectField(u'Select Skill', choices=[], default ='' ) # Specific Skill Desription e.g. Sr. Java Developer, Openshift
    careerLevel = SelectField(u'Select Skill', choices=[], default ='' )  # from BCS, the "reqiured level" or the "demand level"
    billingModel = SelectField(u'Select Skill', choices=[], default ='' ) # [MonthlyFTE, DailyEffort, AlternateModel2]
    billingPercent = IntegerField(default = 100) # 100% is the default
    staffingStatus  = SelectField(u'Select Staffing Status', choices=[], default ='' ) # [Open, Proposed, Blocked, Confirmed, Shadowing, AwaitingReourceJoin]
    candidatesInPlay = StringField(u'Candidates in play', validators=[DataRequired(), Length(max=200)],  ) #[comma separted list of names, till recruitment Module comes-in]
    assignedEmpBcsName = SelectField(u'Assign or Change Employee', choices=[], default ='' )
#    candidate = SelectField(u'Assign or Change Employee', choices=[], default ='' )
    submit = SubmitField('Add/Update') #   


#Display a List of Tasks for a given program, and allow add, update and delete
@app.route('/bcsproj/projroleaddupdate/<int:id>', methods=('GET', 'POST'))
@app.route('/bcsproj/projroleaddupdate', methods=('GET', 'POST'))
@login_required
def projRoleListAdd(id = -1) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'ProjectRole'
    cname = eval(table)
    if id > 0 :
        proj = MsgProject.query.filter_by(id = id).first()
        projTitle = proj.projName
    else :
        projTitle = "All"
#        return ("Invalid Role ID")

    form = MsgProjectRoleForm(request.form)  # Create an itemList from request.form, in case of post

    if request.method == "POST" and id > 0 : #and form.validate_on_submit():
        obj = cname()
        form.populate_obj(obj)
        projRoleFormSetCandidate(form, obj)
        obj.projectId = id 
        obj.assgined_billLevel=1 # TO BE FIXED, make it NULL ALLOWED
        db.session.add(obj) # Add it to the data base
        db.session.commit()
    form = MsgProjectRoleForm()  # Create an itemList from request.form, in case of post
    projRoleFormSetSelect(form)
    if id > 0 :
        allRoles = cname.query.filter_by(projectId = proj.id).all()
    else :
        allRoles = cname.query.all()
    return render_template('bcsdata/projroleshowlist.html', itemSet = allRoles, form = form, projTitle = projTitle)

def projRoleFormSetSelect(form) :
    form.roleSkillCat.choices =  getSkillCatSetForSelect()  + [("","")]
    form.roleSkill.choices =   getSkillForSelect("category") # Fill in e-mails
    form.careerLevel.choices = getCareerLevelForSelect() # Fill in e-mails
    form.staffingStatus.choices = getStaffingStatusForSelect() # Fill in e-mails
    form.assignedEmpBcsName.choices =  getEmailSetForSelect()  + [("","")]  # Fill in e-mails
    form.billingModel.choices = getBillingModelForSelect() # Fill in e-mails
    return

#Method to set the assignedBCSemployee field from form
def projRoleFormSetCandidate(form, role) :
    app.logger.info("In Candidate-set") 
    if form.assignedEmpBcsName : # Is non-null
#        app.logger.info("In Candidate-set to:" + form.assignedEmpBcsName.data) 
        role.assignedEmpId = getEmpIdByEmail(form.assignedEmpBcsName.data)
    return

@app.route('/bcsproj/projroleupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def projRoleUpdate(id) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'ProjectRole'
    cname = eval(table)
    form = MsgProjectRoleForm(request.form)  # Create an itemList from request.form, in case of post
    role = cname.query.filter_by(id = id).first()
    proj = MsgProject.query.filter_by(id = role.projectId).first()
    projTitle = proj.projName
    if request.method == "POST" :
        app.logger.info(str(role.assignedEmpBcsName)) 
        form.populate_obj(role)
        projRoleFormSetCandidate(form, role)
        app.logger.info(str(role.assignedEmpBcsName)) 
        db.session.commit()
        return redirect(url_for('projRoleListAdd', id= role.projectId))
    form = MsgProjectRoleForm(obj=role)  # Create an itemList from request.form, in case of post
    projRoleFormSetSelect(form)
    allRoles = cname.query.filter_by(projectId = proj.id).all()
    return render_template('bcsdata/projroleshowlist.html', itemSet = allRoles, form = form, projTitle = projTitle, parentid=role.projectId )

#TODO: Make this ADMIN only Once the goalsheet is approved
@app.route('/bcsproj/projroledelete/<int:id>', methods=('GET', 'POST'))
@login_required
def projRoleDelete(id) : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'ProjectRole'
    cname = eval(table)
    role = cname.query.filter_by(id = id).first()
    projid = role.projectId
    item = cname.query.filter_by(id = id ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    db.session.commit()
    return redirect(url_for('projRoleListAdd', id=projid))

##########################################################################################################################
###END OF ROLE #######################################################################################
####Account List/Add/Update/Delete###########################################################################################
##########################################################################################################################
class MsgAccountForm(FlaskForm) :
    id = IntegerField()
    managerEmail = SelectField(u'Assign or Change Manager', choices=[], default ='' ) # email of the account manager
    accountName  = StringField(u'Account Name', validators=[DataRequired(), Length(max=50)],   ) # Short Name  e.g. MSIG
    dateStart= DateTimeField('Start Date', [validators.required()],  format='%d-%m-%y')
    dateEnd = DateTimeField('End Date', [validators.required()], format='%d-%m-%y')
    description = StringField(u'Description', validators=[DataRequired(), Length(max=1000)],   ) # General Notes
    contractCompany = StringField(u'Contract Company', validators=[DataRequired(), Length(max=50)] ) # msg-global, systems, GIC
    contractRegion = StringField(u'Contract Region', validators=[DataRequired(), Length(max=50)] ) # e.g. Benelux, Germany, SGP, India
    contractEntity = StringField(u'Contract Entity', validators=[DataRequired(), Length(max=50)] ) # msg Global, 
    submit = SubmitField('Add/Update') #   

#Display a List of Tasks for a given program, and allow add, update and delete
@app.route('/bcsproj/acctaddupdate', methods=('GET', 'POST'))
@login_required
def acctListAdd() : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgAccount'
    cname = eval(table)


    if request.method == "POST" : #and form.validate_on_submit():
        form = MsgAccountForm(request.form)  # Create an itemList from request.form, in case of post
        obj = cname()
        form.populate_obj(obj) 
        db.session.add(obj) # Add it to the data base
        db.session.commit()
    form = MsgAccountForm()  # Create an itemList from request.form, in case of post
    form.managerEmail.choices =  getEmailSetForSelect()  + [("","")]
    allAcct = cname.query.all()
    return render_template('bcsdata/projaccount.html', itemSet = allAcct, form = form)


#Update a Given Task, ID is provided. Goal-ID and SHeet ID are already available, so no need for anything else
@app.route('/bcsproj/acctupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def acctUpdate(id) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgAccount'
    cname = eval(table)
    form = MsgAccountForm(request.form)  # Create an itemList from request.form, in case of post
    acct = cname.query.filter_by(id = id).first()
    if request.method == "POST" :
        form.populate_obj(acct)
        db.session.commit()
        return redirect(url_for('acctListAdd'))
    form = MsgAccountForm(obj=acct)  # Create an itemList from request.form, in case of post
    form.managerEmail.choices =  getEmailSetForSelect()  + [("","")]
    allAcct = cname.query.all()
    return render_template('bcsdata/projaccount.html', itemSet = allAcct, form = form)

#TODO: Make this ADMIN only Once the goalsheet is approved
@app.route('/bcsproj/acctdelete/<int:id>', methods=('GET', 'POST'))
@login_required
def acctDelete(id) : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgAccount'
    cname = eval(table)
    item = cname.query.filter_by(id = id ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    db.session.commit()
    return redirect(url_for('acctListAdd'))


##########################################################################################################################
###END OF Account #######################################################################################
####Program List/Add/Update/Delete###########################################################################################
##########################################################################################################################
class MsgProgramForm(FlaskForm) :
    id = IntegerField()
#    accountId = SelectField(u'Select or change Account', choices=[], default ='' ) 
    managerEmail = SelectField(u'Assign or Change Manager', choices=[], default ='' ) # email of the account manager
    programName  = StringField(u'Account Name', validators=[DataRequired(), Length(max=50)],  widget=TextArea() ) # Short Name  e.g. MSIG
    dateStart= DateTimeField('Start Date', [validators.required()],  format='%d-%m-%y')
    dateEnd = DateTimeField('End Date', [validators.required()], format='%d-%m-%y')
    description = StringField(u'Description', validators=[DataRequired(), Length(max=1000)],  widget=TextArea() ) # General Notes
    submit = SubmitField('Add/Update') #   

 
#Display a List of Tasks for a given program, and allow add, update and delete
@app.route('/bcsproj/progaddupdate/<int:id>', methods=('GET', 'POST'))
@app.route('/bcsproj/progaddupdate', methods=('GET', 'POST'))
@login_required
def progListAdd(id = -1) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProgram'
    cname = eval(table)
    if id > 0 :
        acct = MsgAccount.query.filter_by(id = id).first()
        acctTitle = acct.accountName
    else :
        acctTitle = "All"


    if request.method == "POST" : #and form.validate_on_submit():
        form = MsgProgramForm(request.form)  # Create an itemList from request.form, in case of post
        obj = cname()
        form.populate_obj(obj) 
        if id > 0 :
            obj.accountId = id
        else :
            obj.accountId = 1
        db.session.add(obj) # Add it to the data base
        db.session.commit()
    form = MsgProgramForm()  # Create an itemList from request.form, in case of post
    form.managerEmail.choices =  getEmailSetForSelect()  + [("","")]
    if id > 0 :
        allProgs = cname.query.filter_by(accountId = id).all()
    else :
        allProgs = cname.query.all()
        
    return render_template('bcsdata/projprogram.html', itemSet = allProgs, form = form, projTitle = acctTitle)


#Update a Given Task, ID is provided. Goal-ID and SHeet ID are already available, so no need for anything else
@app.route('/bcsproj/progupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def progUpdate(id) : # id is the id of the GoalSection, goes as is into the object creation
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProgram'
    cname = eval(table)
    form = MsgProgramForm(request.form)  # Create an itemList from request.form, in case of post
    prog = cname.query.filter_by(id = id).first()
    acct = MsgAccount.query.filter_by(id = prog.accountId).first()
    acctTitle = acct.accountName
    if request.method == "POST" :
        form.populate_obj(prog)
        db.session.commit()
        return redirect(url_for('progListAdd', id= prog.accountId))
    form = MsgProgramForm(obj=prog)  # Create an itemList from request.form, in case of post
    form.managerEmail.choices =  getEmailSetForSelect()  + [("","")]
    allProgs = cname.query.filter_by(accountId = id).all()
    return render_template('bcsdata/projprogram.html', itemSet = allProgs, form = form, projTitle = acctTitle)

#TODO: Make this ADMIN only Once the goalsheet is approved
@app.route('/bcsproj/progdelete/<int:id>', methods=('GET', 'POST'))
@login_required
def progDelete(id) : # id of the GoalSection is passed here
    empEmail = current_user.username.lower()
    if not bcscheckauth(empEmail) :
        return redirect(url_for('unauthorized'))

    table = 'MsgProgram'
    cname = eval(table)
    prog = cname.query.filter_by(id = id).first()
    acctId = prog.accountId
    item = cname.query.filter_by(id = id ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    db.session.commit()
    return redirect(url_for('progListAdd', id=acctId))


##########################################################################################################################
###END OF PROGRAM #######################################################################################
##########################################################################################################################
##########################################################################################################################

