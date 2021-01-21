"""
K.Srinivas, 10-Apr-2018

Project: Goal Sheet
Description: This will contain the basic views for goal-sheet. Objective is for folks to be able to input ASAP.
Approach is as follows:
a) Copied the list-mgmt procedures from hrmslistmanagement.py. So far, Items with ID and Name can be handled.
b) Check if FORM can have attributes added dynamically. We will start with Description
    => If this is feasible, all form-fields to be added dynamically by using a naming convention for form-entities
    => If this is successful, most of basic UI will be completed in one go.
c) Else, if (c) does not work out or is way too complicated, we go for straight-forward implementation of each page

TODO: 
a) DONE-This is being developed independently of the runapp.py at the top-level. To be integrated later.

KNOWN BUGs: None
"""
import logging

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required ,  current_user
from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextArea
from flask import Flask, url_for
#ForFileUpload
from flask import send_from_directory, render_template, redirect, request, flash
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from goalmodel import *
from calendarmodel import *
from calendardomain import *
from realapp import app, db

##########################################################################################################################
#### Attempt at Generic 2-column Table editor UI e.g. Department, address_type, asset_status##############################
##########################################################################################################################
# Key=table-name, values is list of elements
# ID/id, what-ever be the 1st element needs to be an INT!! String will not work
# This effort has been dropped for not. The returns does not appear to be work the copy-paste effort
# But table_list concept is till being used as it reduces the copy-paste effort as well :-)
##########################################################################################################################
table_list = { 
    'MasterGoalSection': ['id', 'title', 'description'] ,
    'MasterGoal': ['id', 'title', 'description', 'goalSectionId'] ,
    'AssignmentTemplate': ['id', 'title', 'description'] ,
}

##########################################################################################################################
#### Master Goal Section s##############################
class Generic2ElementForm(FlaskForm) :
    id = IntegerField()
    title = TextField("Enter")
    description = TextField("Enter")
    submit = SubmitField('Add/Update') #   

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/mastergoalssectionlist', methods=('GET', 'POST'))
@login_required
def masterGoalsSectionList() :
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    table = 'MasterGoalSection'
    cname = eval(table)
    itemSet = MasterGoalSection.query.all()
    print("No.of Items:" + str(len(itemSet)))
    eleItems = table_list[table]
    form = Generic2ElementForm(request.form)  # Create an itemList from request.form, in case of post
    if request.method == "POST" and form.validate_on_submit():
        if form.title.data :
            obj = MasterGoalSection() 
            setattr(obj, eleItems[1],form.title.data) # Populate the Exam Object from the request.form return-value
            setattr(obj, eleItems[2],form.description.data) # Populate the Exam Object from the request.form return-value
            db.session.add(obj) # Add it to the data base
            db.session.commit()
            db.session.flush()
            itemSet = MasterGoalSection.query.all()
            print("No.of Items:" + str(len(itemSet)))
            form = Generic2ElementForm()  # Create an itemList from request.form, in case of post
            return render_template('goalsheet/goalsectionshow.html', itemSet = itemSet, form = form, eleItems = eleItems, table=table)
    form = Generic2ElementForm()  # Create an itemList from request.form, in case of post
    return render_template('goalsheet/goalsectionshow.html', itemSet = itemSet, form = form, eleItems = eleItems, table=table)

#            for i in range(len(itemSet)) :
#                mydict = vars(itemSet[i])
#        print("Dept Name=" + getattr(itemSet[i], "DEPARTMENT_NAME"))
        #mydict = vars(itemSet[i])

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/mastergoalssectionupdate/<int:id>', methods=('GET', 'POST'))
@login_required
def masterGoalsSectionUpdate(id) :
    if not current_user.is_admin :
        return redirect("unauthorized.html")

    table = 'MasterGoalSection'

    cname = eval(table)
    eleItems = table_list[table]
    
    item = MasterGoalSection.query.filter_by(id = int(id) ).first() # Assuming ID to be an INT!! Watchout
    form = Generic2ElementForm(request.form)
    form.title.data = getattr(item,  eleItems[1])
    form.description.data = getattr(item,  eleItems[2])
    if request.method == "POST" :
        setattr(item, eleItems[1] , request.form[eleItems[1]])
        setattr(item, eleItems[2] , request.form[eleItems[2]])
        db.session.commit()
        db.session.flush()
        return redirect(url_for('masterGoalsSectionList'))
    return render_template('goalsheet/goalsectionupdate.html',  form = form, id=id)

##########################################################################################################################
#### Master Goal ########################################################################################################
#TODO: ADD the Jinja tempate for this one
#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/mastergoalslist/<int:id>', methods=('GET', 'POST'))
def masterGoalsList(id) : # id is the id of the GoalSection, goes as is into the object creation
    if not current_user.is_admin :
        return redirect("unauthorized.html")

    table = 'MasterGoal'
    cname = eval(table)
    itemSet = MasterGoal.query.filter_by(goalSectionId = int(id)).all()
#    if itemSet :
#        print("SectionTitle:" + str(itemSet[0].goalSectionRef.title))
    eleItems = table_list[table]
    form = Generic2ElementForm(request.form)  # Create an itemList from request.form, in case of post
    if request.method == "POST" and form.validate_on_submit():
        obj = cname() 
        setattr(obj, eleItems[1],form.title.data) # Populate the Exam Object from the request.form return-value
        setattr(obj, eleItems[2],form.description.data) # Populate the Exam Object from the request.form return-value
        setattr(obj, eleItems[3],id) # Populate the Exam Object from the request.form return-value
        db.session.add(obj) # Add it to the data base
        db.session.commit()
        db.session.flush()
        itemSet = cname.query.filter_by(goalSectionId = int(id)).all()
        form = Generic2ElementForm()  # Create an itemList from request.form, in case of post
        return render_template('goalsheet/goalshow.html', itemSet = itemSet, form = form, eleItems = eleItems, parentid=id)
    form = Generic2ElementForm()  # Create an itemList from request.form, in case of post
    return render_template('goalsheet/goalshow.html', itemSet = itemSet, form = form, eleItems = eleItems, parentid=id)



#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/mastergoalsedit/<int:id>', methods=('GET', 'POST'))
@login_required
def masterGoalEdit(id) : # id of the GoalSection is passed here
    if not current_user.is_admin :
        return redirect("unauthorized.html")

    table = 'MasterGoal'

    cname = eval(table)
    eleItems = table_list[table]
    itemNum = eleItems[0]
    
    item = cname.query.filter_by(id = int(id) ).first() # Assuming ID to be an INT!! Watchout
    form = Generic2ElementForm(request.form)
    form.title.data = getattr(item,  eleItems[1])
    form.description.data = getattr(item,  eleItems[2])
    if request.method == "POST" :
        setattr(item, eleItems[1] , request.form[eleItems[1]])
        setattr(item, eleItems[2] , request.form[eleItems[2]])
        db.session.commit()
        return redirect(url_for('masterGoalsList', id=item.goalSection))
    return render_template('goalsheet/goalupdate.html',  form = form, id=id)

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/mastergoalsdelete/<int:id>', methods=('GET', 'POST'))
@login_required
def masterGoalDelete(id) : # id of the GoalSection is passed here
    if not current_user.is_admin :
        return redirect("unauthorized.html")

    table = 'MasterGoal'

    cname = eval(table)
    eleItems = table_list[table]
    item = cname.query.filter_by(id = int(id) ).first() # Assuming ID to be an INT!! Watchout
    parentid = item.goalSectionId
    item = cname.query.filter_by(id = int(id) ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    print(str(item))
#    item.execute()
    db.session.commit()
    return redirect(url_for('masterGoalsList', id=parentid))

##########################################################################################################################
#### Template Creation ########################################################################################################
#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/templatelist', methods=('GET', 'POST'))
@login_required
def templateList() :
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    table = 'AssignmentTemplate'
    cname = eval(table)
    itemSet = cname.query.all()
    print("No.of Items:" + str(len(itemSet)))
    eleItems = table_list[table]
    form = Generic2ElementForm(request.form)  # Create an itemList from request.form, in case of post
    if request.method == "POST" and form.validate_on_submit():
        if form.title.data :
            obj = cname() 
            setattr(obj, eleItems[1],form.title.data) # Populate the Exam Object from the request.form return-value
            setattr(obj, eleItems[2],form.description.data) # Populate the Exam Object from the request.form return-value
            db.session.add(obj) # Add it to the data base
            db.session.commit()
            db.session.flush()
            itemSet = cname.query.all()
            print("No.of Items:" + str(len(itemSet)))
            return render_template('goalsheet/templateshow.html', itemSet = itemSet, form = form, eleItems = eleItems, table=table)
    form = Generic2ElementForm()  # Create an itemList from request.form, in case of post
    return render_template('goalsheet/templateshow.html', itemSet = itemSet, form = form, eleItems = eleItems, table=table)


#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/templateUpdate/<int:id>', methods=('GET', 'POST'))
@login_required
def templateUpdate(id) :
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    table = 'AssignmentTemplate'
    cname = eval(table)
    eleItems = table_list[table]
    item = cname.query.filter_by(id = int(id) ).first() # Assuming ID to be an INT!! Watchout
    form = Generic2ElementForm(request.form)
    form.title.data = getattr(item,  eleItems[1])
    form.description.data = getattr(item,  eleItems[2])
    if request.method == "POST" :
        setattr(item, eleItems[1] , request.form[eleItems[1]])
        setattr(item, eleItems[2] , request.form[eleItems[2]])
        db.session.commit()
        db.session.flush()
        return redirect(url_for('templateList'))
    return render_template('goalsheet/templateupdate.html',  form = form, id=id)

def getGoalSectionTitle(id) :
    goalSection = MasterGoalSection.query.filter_by(id = id).first() # All goal sections
    if goalSection :
        return goalSection.title
    return "NoGoalSectionFound"

##########################################################################################################################
#### Template Content Addition ########################################################################################################
@app.route('/goals/templategoals/<int:id>', methods=('GET', 'POST'))
@app.route('/goals/templategoals/addgoal', methods=('GET', 'POST'))
@login_required
def templateGoals(id=-1, goalId=-1) : # id = Template ID, goalID = goal to be added to the template
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    table = 'AssignmentTemplate'
    cname = eval(table)
    if id == -1 :
        id = request.args.get("id")
        goalId = request.args.get("goalId")

    if goalId == -1 and id == -1 :
        return("I dont know what happened")
    tempObj = cname.query.filter_by(id = int(id) ).first() # Get Template Object

    print("ID=%s and goalID=%s" % (id,goalId))

    if not tempObj:
        return("Template with ID:%s:not found" %(id))

    tempContents = TemplateGoalList.query.filter_by(templateId = id).all() #Get all goals in this Template
    
    #Get Goals assigned to this template into a nice array for display
    tempConList = []
    tempGoalsList = [] # Used for filtering the goals already in the template
    for tgmap in tempContents :
        item = MasterGoal.query.filter_by(id = tgmap.mastergoalId ).first() # Get the Master Goal Object
        tempConList += [{'sectionTitle':getGoalSectionTitle(item.goalSectionId), 'title': item.title, 'goalId':item.id, 'tempListId':tgmap.id }]
        tempGoalsList += [item.id]
    print("TempConList:" + str(tempConList))

    #Get ALL Goals available into an array for display
    #TODO: Remove the goal-IDs from tempConList
    itemSet = []
    goals = MasterGoal.query.all() # All goals
    for goal in goals :
        if goal.id not in tempGoalsList : # Only show Goals that are NOT already added
            itemSet += [{'sectionTitle':getGoalSectionTitle(goal.goalSectionId), 'title': goal.title, 'goalId':goal.id }]
    print("itemSet:" + str(itemSet))

    #Prepare a list for display: GoalSection-Title, Goal-Title, Goal-ID
    if (goalId == -1) :
        return render_template('goalsheet/templategoals.html', tempObj = tempObj, goals = itemSet, tempList=tempConList)
    else : # A goal was selected to be added
        obj = TemplateGoalList()
        obj.templateId = id
        obj.mastergoalId = goalId
        db.session.add(obj) # Add it to the data base
        db.session.commit()
        #Add the selection to before rendering
        item = MasterGoal.query.filter_by(id = goalId ).first() # Get the Master Goal Object
        tempConList += [{'sectionTitle':getGoalSectionTitle(item.goalSectionId), 'title': item.title, 'goalId':item.id, 'tempListId':obj.id }]
        return render_template('goalsheet/templategoals.html', tempObj = tempObj, goals = itemSet, tempList=tempConList)
    return("Cannot reach here")

#    return render_template('goalsheet/templateshow.html', itemSet = itemSet, form = form, eleItems = eleItems, table=table)
#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/templategoaldelete/<int:id>', methods=('GET', 'POST'))
@login_required
def templateGoalDelete(id) : # id of the entry to be deleted, this ID is used ONLY here
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    table = 'TemplateGoalList'
    cname = eval(table)

    # Save the template ID for redirect after delete
    item = cname.query.filter_by(id = int(id) ).first() # Assuming ID to be an INT!! Watchout
    templateId = item.templateId 
    # Delete the entrie
    item = cname.query.filter_by(id = int(id) ).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
    print(str(item))
#    item.execute()
    db.session.commit()
    return redirect(url_for('templateGoals', id=templateId))




#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/goals/home', methods=('GET', 'POST'))
@login_required
def goalsHome() : # id of the GoalSection is passed here
    if not current_user.is_admin :
        return redirect("unauthorized.html")
    return render_template('goalsheet/goalmgmt.html')

#Method to show "all pages" available
@app.route('/impersonate/<emailId>', methods = ['GET'])
@login_required
def impersonate(emailId):
    from logindomain import impersonateEmployee
    loginAs = emailId
    if not current_user.is_admin :
        return redirect(url_for("unauthorized"))
    emp = getEmpIdByEmail(emailId)
    if not emp : #Not found, see if you can find by ID (ID given instead of email)
        emp = getEmployeebyId(emailId)
        if emp : #Cannot be found
            loginAs = emp.OFFICE_EMAIL_ID
        else :
            return render_template("message.html", message="Employee could not be found")
            
    impersonateEmployee(loginAs, current_user) 
    return redirect(url_for("goalhome"))


#Method for testing various methods
@app.route('/goals/goalstest', methods=('GET', 'POST'))
@login_required
def goalsTest() : # id of the GoalSection is passed here
    createDefaultCalendar()    
    return render_template('goalsheet/goalmgmt.html')




