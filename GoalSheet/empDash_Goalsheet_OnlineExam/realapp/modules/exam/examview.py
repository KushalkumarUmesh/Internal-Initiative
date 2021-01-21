"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: This implements the views for the Exam list and assignment and forms the heart of the application. 

DONE: Make this Admin-only or based on the parameters defined in the test
DONE: List assignments should not need an admin login. However, putting it in to filter-by the logged-in user
TODO: Admin Screen should have a "show all"
DONE: Check that loggedin users is taking a test assigned to him/her

KNOWN BUGs: None
"""
import logging

from flask_wtf import FlaskForm
from wtforms import RadioField,SubmitField, FieldList,FormField
from wtforms.validators import DataRequired
from flask import render_template, redirect, request, flash, url_for
from realapp import app, login_manager, csrf
import datetime as dt
from examdomain import getTests, updateTest, getTestList, markInprogress
from flask_login import login_required, current_user
from assignmodel import ExamObj, QuestionSet
from checkauthorization import check_auth

#DONE: Make this Admin-only or based on the parameters defined in the test
@app.route('/exam/showtest/<int:id>', methods=['GET'])
@app.route('/ole/exam/showtest/<int:id>', methods=['GET'])
@login_required
def showAnswerPaper(id) :
    if not current_user.is_admin :
        return redirect(url_for('unauthorized'))
    exam = ExamObj.query.filter_by(examId = id).first()
    qlist = QuestionSet.query.filter_by(examId = id).all()
    return render_template("exam/examanswer.html", exam=exam, ques=qlist )

#DONE: List assignments should not need a login. However, putting it in to filter-by the logged-in user
#TODO: Admin Screen should have a "show all"
@app.route('/exam/listassignments', methods=['GET', 'POST'])
@app.route('/ole/exam/listassignments', methods=['GET', 'POST'])
@login_required
def listassignments() :
    elist = getTestList(current_user.username, current_user.is_admin)
    return render_template("exam/examlist.html", tnames=elist )

#TODO: Update comments..what 
@app.route('/exam/listtests', methods=['GET'])
@app.route('/ole/exam/listtests', methods=['GET'])
@login_required
def listtests() :
    if not check_auth("ListTests") :
        return redirect(url_for('unauthorized'))
    (tnames, tdesc, tnumq , tpass, tdiff ) = getTests()
    return render_template("exam/testlist.html", tnames=tnames, tdesc=tdesc, tnumq = tnumq, tpass=tpass, tdiff=tdiff )

# Basic Qustion-Answer Form, relicated in QuestionForm
class QuestionAns(FlaskForm) :
    ques = ""
    answer = RadioField('Label')

# Replicate QuestionAns form and add a Submit button
class QuestionForm(FlaskForm) :
    submit = SubmitField('Submit Answers') #   
    questions = FieldList(FormField(QuestionAns), min_entries=100)

# Actual EXAM taken by the candidate.
# DONE: Check that loggedin users is taking a test assigned to him/her
@app.route('/ole/exam/taketest', methods=('GET', 'POST'))
@app.route('/ole/exam/taketest/<int:id>', methods=('GET', 'POST'))
@app.route('/ole/exam/taketest/<int:id>,<accept>', methods=('GET', 'POST'))
@app.route('/exam/taketest', methods=('GET', 'POST'))
@app.route('/exam/taketest/<int:id>', methods=('GET', 'POST'))
@app.route('/exam/taketest/<int:id>,<accept>', methods=('GET', 'POST'))
@login_required
def taketest(id = -1, accept = "") :
    if (id < 0 ) :
        return redirect(url_for("home"))
    exam = ExamObj.query.filter_by(examId = id).first()
    if not exam : # Unlikely but always possible :-)
        flash("Internal Error: Examm Object not found, please inform the administrator")
        return redirect(url_for('home'))
        
    # Only you can take your test, Even an admin cannot take test for someone else.
    if exam.candiateEmail != current_user.username.lower() :
        return redirect(url_for('unauthorized'))

    if request.method == "GET" :
        if (exam.numAttemptsMade > 0)    : #Removing multiple attempts on the same exam as it can leak the questin-paper
            return render_template('message.html', message = 'Too many attempts to take the exam.')
    elif request.method == "POST" :
        if (exam.numAttemptsMade != 1)  : # Something is wrong
            return render_template('message.html', message = 'Too many attempts to take the exam.')

    print("Reached before accept-check")
    if request.method == "GET" :
        print("1Reached before accept-check")
        if accept != "Yes":
            print("Reached aftersaccept-check: " + str(accept))
            return redirect(url_for('startexam', id=id))
    qlist = QuestionSet.query.filter_by(examId = id).all()
    numQ = len(qlist) 
    form = QuestionForm(request.form)
    #Set-up the Options in the radio buttons, and finally the question itself
    for i in range(0,numQ) : 
        q= qlist[i]
        id = q.id
        options= []
        options.append(["optionA", q.optionA])
        options.append(["optionB", q.optionB])
        options.append(["optionC", q.optionC])
        options.append(["optionD", q.optionD])
        form.questions[i].answer.choices = options
        form.questions[i].ques = qlist[i].question

    if request.method == "POST" :
        updateQlistWithAnswers(qlist, request.form) #Get the answers and update the qlist vaiable
        ( result, rights ) =  updateTest(exam, qlist) # Qlist-Form
        if result :
            return render_template('exam/exampassed.html', rights=rights, exam=exam, numq = numQ, time = dt.datetime.today())
        else :
            remaining = exam.numAttemptsAllowed - exam.numAttemptsMade
            return render_template('exam/examfailed.html', rights=rights, exam=exam, numq = numQ, attempts=remaining)
    else:
        #Question Paper is served
        markInprogress(exam) #Mark Exam as Attempted
        return render_template('exam/examanswer.html', form=form, exam=exam, numq = numQ)


@app.route('/exam/startexam/<int:id>', methods=('GET', 'POST'))
@app.route('/exam/startexam/resp', methods=('GET', 'POST'))
@app.route('/ole/exam/startexam/<int:id>', methods=('GET', 'POST'))
@app.route('/ole/exam/startexam/resp', methods=('GET', 'POST'))
#@login_required
def startexam(id = -1) :
    ok = ""
    if (id < 0 ) :
        ok = request.args.get("accept")
        id= request.args.get("id")
        #return redirect(url_for("home"))
    id = int(id)
    exam = ExamObj.query.filter_by(examId = id).first()

    if ok == "ok" :
        print("Accept OK")
        return redirect(url_for("taketest", id=id, accept="Yes"))
    elif ok == "notok" : # Declined
        return redirect(url_for("listassignments")) 
    #Simply render the page          
    return render_template('exam/examstart.html', accept = "/exam/startexam/resp?accept=ok&id=" + str(id), decline = "/exam/startexam/resp?accept=notok&id=" + str(id), exam=exam)

#Method to populate the answers in the question-list.
#This is needed to separate the domain and models from the UI, but not moving to the domain object as the "fkey" is UI-specific
def updateQlistWithAnswers(qlist, answers) :
    for i in range(0,len(qlist)) :
        fkey = "questions-" + str(i) + "-answer"
        if fkey in answers.keys() :
            qlist[i].updateAfterTest(answers[fkey][-1]) # Get last Charecter
        else :
            continue
    return # qlist is updated with answers
    