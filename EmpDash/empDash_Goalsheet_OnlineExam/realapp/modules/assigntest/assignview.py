"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: This is the view+controller for the listing and assigning an Exam to a person or group.
Terminology: Test is the definition of a question-paper. Exam is an instance of a Test that is assigned to a person.
TODO: 
a) DONE: Candidate-Selection needs to come from a list
b) DONE: Candidate-individual or group option is required : Separate methods to make it easy
c) DONE: If assigner his NOT admin, he/she can assign tests only to himself/herself OR make it admin-only functionality
d) Navigate to a different page on successful/failed assignment
e) DONE:Number of questions/pass-marks needs to be non-editable
f) E-mail notifications need to be sent to assignees (Done only for group, not for individual, should be in the domain)

KNOWN BUGs: Resubmitting the same test to multiple people, without leaving the page is causing SAME questions to be assigned.
"""
import logging
from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required, current_user
from flask import render_template, redirect, request, flash, url_for
from realapp import app, login_manager, testBank , csrf
from assignmodel import ExamObj, QuestionSet
from assigndomain import getCandidateSelectionList, getGroupSelectionList, assignExam , assignExamToGroup, getEmailsInGroup, notifyGroup
from checkauthorization import check_auth
from dateutil import parser
import datetime as dt

# Form for taking inputs for assignment
# Done: SelectField needs to be fixed - moved to assigndomain
# Done: numQuestions, passNum need to be non-editable
class AssignForm(FlaskForm) :
    candiateEmail = SelectField(u'Assign To Individual', choices=[], default ='' )
    group = SelectField(u'Assign To Group', choices=[], default = "" )
    dtStart  = DateTimeField('Start Date(MM-DD-YY)',[validators.required()], format='%m/%d/%y')
    dtDue  = DateTimeField('Complete By(MM-DD-YY)',[validators.required()], format='%m/%d/%y')
    submit = SubmitField('Assign Test')

#This is assigning test to ONE person
#Done: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
#TODO: After assignment, take to a different page
@app.route('/assign/assigntest/<testname>', methods=('GET', 'POST'))
@app.route('/ole/assign/assigntest/<testname>', methods=('GET', 'POST'))
@login_required
def assigntest(testname) :
    form = AssignForm(request.form)
    examObj = testname
             
    if check_auth("AssignTest") : # Admin can assign any test, to anyone
#    if current_user and current_user.is_admin : # Admin can assign any test, to anyone
        form.candiateEmail.choices = getCandidateSelectionList()  + [("","")]
    else : # user is not authorized to Assign a Test
        return redirect(url_for('unauthorized'))

    obj = ExamObj(testName = testname) # Create an empty exam object with the given testname
    obj.numQuestions = testBank.getTestNoOfQuestions(testname) 
    obj.passNum = testBank.getTestPassNum(testname)
    obj.numAttemptsAllowed = 1 # Default is set to one, multiple-attempts functionality is removed due to security reasons.

    if request.method == "POST" :
        form.populate_obj(obj) # Populate the Exam Object from the request.form return-value
        print(str(request.form))
        if request.form['dtStart'] :
            obj.dtStart = parser.parse(request.form['dtStart'])
        if request.form['dtDue'] :
            obj.dtDue = parser.parse(request.form['dtDue'])

        if obj.candiateEmail :
            flash( assignExam(obj, current_user.username) )
            return render_template('assigntest/assign_test.html', form=form, exam=testname)
        else : 
            flash("Please select a valid user email ID.")
            return render_template('assigntest/assign_test.html', form=form, exam=examObj)
            
    else :
        return render_template('assigntest/assign_test.html', form=form, exam=examObj)
    return ("Internal Error: Please contact your admin. Regret the inconvenience.")

###############################################################################################################################
# Form for taking inputs for GROUP assignment
class GroupAssignForm(FlaskForm) :
    candiateEmail = SelectField(u'Assign To Group', choices=[], default = "" )
    dtStart  = DateTimeField('Start Date(MM-DD-YY)', format='%m/%d/%y')
    dtDue  = DateTimeField('Complete By(MM-DD-YY)', format='%m/%d/%y')
    submit = SubmitField('Assign Test')


#Done: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/assign/assigntesttogroup/<testname>', methods=('GET', 'POST'))
@app.route('/ole/assign/assigntesttogroup/<testname>', methods=('GET', 'POST'))
@login_required
def assignTestToGroup(testname) :

    form = GroupAssignForm(request.form)
             
    if check_auth("AssignTest") : # Admin can assign any test, to anyone
        try :
            form.candiateEmail.choices = getGroupSelectionList()  + [("","")]
        except :
            return render_template("message.html", message="Notification Service could not be contacted. Please try after some time.")
            
    else : # Force selection of only himself/herself
#        form.candiateEmail.choices=[(current_user.username,current_user.username )] 
        return redirect(url_for('unauthorized'))

    obj = ExamObj(testName = testname) # Create an empty exam object with the given testname
    obj.numQuestions = testBank.getTestNoOfQuestions(testname) 
    obj.passNum = testBank.getTestPassNum(testname)
    obj.numAttemptsAllowed = 1 # Default is set to one, the option for more retries will be added later ONLY for ADMINs !!
    if request.method == "POST" :
        form.populate_obj(obj) # Populate the Exam Object from the request.form return-value
        if not obj.dtStart :
            obj.dtStart = dt.date(2000,1,1)
        if not obj.dtDue :
            obj.dtDue = dt.date(2000,1,1)
            
        if obj.candiateEmail :
            flash( assignExamToGroup(obj, current_user.username) )
            return render_template('assigntest/assign_test.html', form=form, exam=testname)
        else :
            flash("Please select a valid Group")
            return render_template('assigntest/assign_test.html', form=form, exam=testname)
    else :
        return render_template('assigntest/assign_test.html', form=form, exam=testname)
    return ("Internal Error: Please contact your admin. Regret the inconvenience.")

###################################################################################################################
# Cut-Paste Material only
#        return(obj)
#        return redirect("/success")
#   return redirect("/failure")
#    testName = SelectField(u'Test Name', choices=[])
#    testName = SelectField(u'Test Name', choices=[('Java Level 1', 'Insurance Basics'), \
#            ('ABAP Level 1', 'ABAP Level 1'), ('Sample Test Retval', 'Sample Test')])
#   assignTo = EmailField('Select Name', [validators.DataRequired(), validators.Email()])
# For Debugging purposes only...
"""
#    numQuestions = IntegerField('Number of Questions', [validators.required()])
#    passNum = IntegerField('Pass Score', [validators.required()])
#    numAttemptsAllowed = IntegerField('No. of Attempts Allowed')

        af.candiateEmail.choices=[('srinivas.kambhampati@msg-global.com', 'srinivas.kambhampati@msg-global.com'), \
                ("tulsi.Das.bhatt@msg-global.com", "tulsi.Das.bhatt@msg-global.com"), \
                ("mohitchandra.tuli@msg-global.com","mohitchandra.tuli@msg-global.com"), \
                ("sridhar.kalyanam@msg-global.com","sridhar.kalyanam@msg-global.com")
                ] 

 def printExamObj(eObj) :
    print("examId =" + str(eObj.examId) )
    print("testName =" + eObj.testName )
    print("candiateEmail =" + eObj.candiateEmail) 
    print("candiateID =" + str(eObj.candiateID) )
    print("numQuestions =" + str(eObj.numQuestions) )
    print("passNum =" + str(eObj.passNum)  )
    print("numAttemptsAllowed =" + str(eObj.numAttemptsAllowed) )
    print("numAttemptsMade =" + str(eObj.numAttemptsMade) )
    print("dtAssigned =" + str( eObj.dtAssigned))
    print("dtCompleted =" + str(eObj.dtCompleted))
    print("dtStart =" + str( eObj.dtStart))
    print("dtDue =" + str( eObj.dtDue))
    print("dtLastNotified =" + str(eObj.dtLastNotified))
    print("score = " + str(eObj.score  ))
    print("resultStatus =" + eObj.resultStatus)
    print("examStatus =" + eObj.examStatus)
"""
