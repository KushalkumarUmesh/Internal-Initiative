"""
K.Srinivas, 6-Apr-2018

Project: HRMS-Support
Description: HRMS contains many "lists" used for restricting various values. These include Department, Manager_Info, Project, and so on.
Currently, entries are being added directly into the DB by the admins. A simple UI for these tables will will allow HR and other non-technical
folks to manage it on their own. Currently, UI requirement is identified for:
a) Manager
b) Department
c) Project (for Immigration Module)

TODO: 
a) Done-To Start, some initial POC was done...but nothing after that
b) Identify ALL tables that will work here and list them out, create a static page with correct links

KNOWN BUGs: None
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required 
from realapp import app, login_manager, testBank , csrf
from notification import *
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from werkzeug import secure_filename
from notification import addEmailsFromFile
from hrmsdomain import getEmailSetForSelect
from hrmsmodels import *
##########################################################################################################################
#### Attempt at Generic 2-column Table editor UI e.g. Department, address_type, asset_status##############################
##########################################################################################################################
# Key=table-name, values is list of elements
# ID/id, what-ever be the 1st element needs to be an INT!! String will not work
table_list = { 
    'Departmant': ['ID', 'DEPARTMENT_NAME'] ,
    'AddressType': ['ID', 'name'] ,
    'Assetstatu' : ['id' ,'status'],
    'Assetcategory' : ['id' ,'category'],
    'Assetcondition' : ['id' ,'cond'],
    'Assetrole' : ['roleId' ,'roleName'],
    'CertificationType' : ['ID' ,'name'],
    'Demandstatu' : ['id' ,'status'],
    'Designation' : ['ID' ,'DESIGNATION_NAME'],
    'ExpenseGroup' : ['id' ,'expense_group'],
    'Postatu' : ['id' ,'status'],
    'QualificationType' : ['ID' ,'name'],
    'Quotestatu' : ['id' ,'status'],
    'Relationship' : ['ID' ,'name'],
    'Role' : ['ID' ,'name'],
    'SkillCategory' : ['ID' ,'name'],
    'UniversityType' : ['ID' ,'name'],
    
}

class Generic2ElementForm(FlaskForm) :
    ID = IntegerField()
    element = TextField("Enter")
    submit = SubmitField('Add/Update') #   

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/hrms/listadd/<table>', methods=('GET', 'POST'))
def listElementsAndAdd(table = "") :
    if not table : # Nothing was returned
        return("need an table tname")
    cname = eval(table)
    itemSet = cname.query.all()
    elementSet = []
    eleItems = table_list[table]
    for i in range(len(itemSet)) :
#        print("Dept Name=" + getattr(itemSet[i], "DEPARTMENT_NAME"))
        mydict = vars(itemSet[i])
        elementSet += [{'ID' : getattr(itemSet[i], eleItems[0]) , 'element':getattr(itemSet[i],  eleItems[1])}]

    print(str(elementSet))
    form = Generic2ElementForm(request.form)  # Create an itemList from request.form, in case of post
    obj = cname() # Need to see this
    if request.method == "POST" and form.validate_on_submit():
        if form.element.data :
            setattr(obj, eleItems[1],form.element.data) # Populate the Exam Object from the request.form return-value
            db.session.add(obj) # Add it to the data base
            db.session.commit()
            itemSet = cname.query.all()
#            for i in range(len(itemSet)) :
#                mydict = vars(itemSet[i])
            elementSet += [{'ID' : getattr(obj, eleItems[0]) , 'element':getattr(obj,  eleItems[1])}]
        return render_template('mylistshowadd.html', itemSet = elementSet, form = form, eleItems = eleItems, table=table, num= len(itemSet))

    return render_template('mylistshowadd.html', itemSet = elementSet, form = form, eleItems = eleItems, table=table, num= len(itemSet))

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
#@app.route('/hrms/listupdate/<int:id>', methods=('GET', 'POST'))
@app.route('/hrms/listupdate/resp', methods=('GET', 'POST'))
def listElementsAndUpdate() :
    table = request.args.get("table")
    id= request.args.get("id")

    cname = eval(table)
    eleItems = table_list[table]
    itemNum = eleItems[0]
    
    item = cname.query.filter(getattr(cname,itemNum) == int(id)).first() # Assuming ID to be an INT!! Watchout
    element = {'ID' : getattr(item, eleItems[0]) , 'element':getattr(item,  eleItems[1])}
    form = Generic2ElementForm(request.form)
    form.submit.data = "Update"
    form.element.data = getattr(item,  eleItems[1])
    if request.method == "POST" :
        setattr(item, eleItems[1] , request.form['element'])
        db.session.commit()
        return redirect(url_for('listElementsAndAdd', table = table))
    return render_template('mylistupdate.html',  form = form, id=id)

