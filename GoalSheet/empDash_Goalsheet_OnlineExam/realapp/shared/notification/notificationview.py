"""
K.Srinivas, 22-Mar-2018

Project: Multiple (starting with OnlineExam, Goalsheet)
Description: This is the view+controller for the Group-Notification Service written by Arun. The purpose is to provide
    a UI for adding/deleting groups and e-mail IDs to the Group-Notification Server. The following is needed:
a) Done-List Groups
b) Done-List e-mail IDs in a Group
c) Done-Create Group : Blank
d) DROP-File-Upload added. Copy emails from an one Group into another (good to have)
e) DROP-File-Upload added. Copy emails from an multiple Groups into another (good to have)
f) DONEAdd/delete e-mail IDs to/from a Group

TODO: Clean-up the import list

KNOWN BUGs: None
"""

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required
from flask import render_template, redirect, request, flash
from realapp import app, login_manager, testBank , csrf
from notification import *
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea

#ForFileUpload
from flask import send_from_directory
from werkzeug import secure_filename
from notification import addEmailsFromFile
from hrmsdomain import getEmailSetForSelect
from hrmsdatafix import getAllEmpCell
from smsnotification import *

class NotificationGroup(FlaskForm) :
    item = StringField(u'Group Name', widget=TextArea())
#    item = TextField("Enter a Group Name", [validators.data_required()])
#    itemdesc = TextAreaField("Description", [validators.data_required()])
    itemdesc =StringField(u'Description', widget=TextArea())
    submit = SubmitField('Add') #   


@app.route('/listgroups', methods=('GET', 'POST'))
@login_required
def listgroups() :
    form = NotificationGroup()
    if request.method == "POST" and form.validate_on_submit():
        groupname= str(form.item.data).strip()
        desc = str(form.itemdesc.data).strip()
        flash (createGroup(groupname,desc) )
        items = getGroups()
        if not len(items) : # Just to be sure
            flash("No groups could be found. Possible internal error.")
        return render_template('notify/notifylistgroup.html', items = items, form = form)
    flash(form.errors)
    items = getGroups()
    if not len(items) :
        flash("No groups could be found. Possible internal error.")
    return render_template('notify/notifylistgroup.html', items = items, form = form)

class FileUpload(FlaskForm) :
    candiateEmail = SelectField(u'Assign To Individual', choices=[], default ='' )
    addemail = SubmitField('Add') #   
    item = FileField("Enter Value")
    submit = SubmitField('Upload') #   

#TODO: The FIleUpload object is not being used..it is just a hack...need to understand
#How to use it OR figure out how to put the form.hidden_tag() on our own.
#TODO: THe file-upload part is to be moved out to fileupload methods
@app.route('/listemailsingroup/<id>', methods=('GET', 'POST'))
@login_required
def listEmailsIngroup(id) :
    form  = FileUpload(request.form)
    form.candiateEmail.choices = getEmailSetForSelect()  + [("","")]
    gname = getGroupName(id)
    if request.method == 'POST':
#        print("In ListEmailsInGroup-5" + str(request.form))
        if 'submit' in request.form.keys() : 
#            print("File Upload has come-in")
            f = request.files['item']
            fname = secure_filename(f.filename)
            f.save(fname)
            print ("fname=" + fname)
            flash(addEmailsFromFile(fname, id))
        elif 'addemail' in request.form.keys() : 
#            print("In ListEmailsInGroup-6")
            if request.form['candiateEmail'] :
                em = request.form['candiateEmail'].strip()
                if em : # Check after stripping, just be sure
                    flash(addEmailToGroup(em, id))
    items = getEmailsInGroup(id)
    if not items or not len(items) :
        flash("No emails could be found. Possible internal error.")
    return render_template('notify/notifylistemails.html',form = form, items = items, groupName = gname, id=id)

@app.route('/testgroupemail/<id>', methods=('GET', 'POST'))
def testGroupEmail(id) :
    if notifyGroup("PMO", "Test Subject", "Test body") :
        return ("Success")
    else :
        return ("Failed")


@app.route('/deletegroup/<id>', methods=('GET', 'POST'))
@login_required
def deletegroup(id) :
    return deleteGroup(id)

@app.route('/deleteemail/<id>/<email>', methods=('GET', 'POST'))
@login_required
def deleteemailfromgroup(id, email) :
    return deleteEmail(id,email)


## IS THIS USED? Can it be deteled?
@app.route('/notification/upload', methods=['GET'])
def upload() :
    if request.method == 'GET' :
        return  """
                <html>
                <body>
                
                    <form action = "http://localhost:5000/uploader" method = "POST" 
                        enctype = "multipart/form-data">
                        <input type = "file" name = "file" />
                        <input type = "submit"/>
                    </form>
                    
                </body>
                </html>
                """

@app.route('/notification/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
#      f.save(f.filename)
      return 'file uploaded successfully'

@app.route('/notification/test', methods=['GET'])
def testNotifyMethod() :
    return sendSMStoOne("9535719960,7019828902", \
"""HRMS: This is a Test. Thanks for updating the correct cell phone number in HRMS.
 
- msg Global HRMS team""")
#    (numList, mesgList) = getAllEmpCell() 
#    resp = sendSMStoList(numList, mesgList)
#    return resp + "OK:" + str(numList) + ":" + str(mesgList)

"""
class NotificationGroup(FlaskForm) :
    item = StringField(u'Group Name', widget=TextArea())
#    item = TextField("Enter a Group Name", [validators.data_required()])
#    itemdesc = TextAreaField("Description", [validators.data_required()])
    itemdesc =StringField(u'Description', widget=TextArea())
    submit = SubmitField('Add') #   
"""