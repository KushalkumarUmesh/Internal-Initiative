"""
K.Srinivas, 10-Oct-2019

Project: Online Exam
Description: This is the view+controller for proving APIs for integration with other modules (e.g. Recruitment)

"""
import logging
from flask import jsonify
from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required, current_user
from flask import render_template, redirect, request, flash, url_for
from realapp import app, login_manager, testBank , csrf, questionsBanks
from assignmodel import ExamObj, QuestionSet
from assigndomain import getCandidateSelectionList, getGroupSelectionList, assignExam , assignExamToGroup, getEmailsInGroup, notifyGroup
from checkauthorization import check_auth
from dateutil import parser
import datetime as dt


#Get a set of questions
@app.route('/apiole/getquestionsbytopicandlevel', methods=('GET', ))
def getQuestionsByTopicAndLevel() :
    topic ="Life Insurance"
    subtopic = "Basics of Life Insurance"
    level = '0'
    if "topic" in request.args.keys() :
        topic = request.args.get("topic")
    if "subTopic" in request.args.keys() :
        subtopic = request.args.get("subTopic")
    if "level" in request.args.keys() :
        level = request.args.get("level")
    # questionsBanks.getQuestions( topic, subtopic, level = '0', numOfQuestions = 0, exam = False , retType = 'J')
    dfSet = questionsBanks.getQuestions( topic, subtopic, level = '0', numOfQuestions = 5, exam = False , retType = 'D')
    retStruct = dict()
    retStruct["topic"] = topic
    retStruct["subTopic"] = subtopic
    retStruct["level"] = 1
    retStruct["questions"] = []
    retStruct["totalQuestions"] = len(dfSet)
    qSet  = retStruct["questions"]
    for i in range(0, len(dfSet) ) :
        questionAnswer = dict()
        questionAnswer["question"] = dfSet.iloc[i].Question
        questionAnswer["answer"] = ""
        questionAnswer["expectedAnswer"] = dfSet.iloc[i].Description
        qSet.append(questionAnswer)
    # print(jsonify(retStruct))
    return jsonify(retStruct)


@app.route('/apiole/getalltopics', methods=('GET', ))
def getAllTopics() :
    return questionsBanks.getTopics()

@app.route('/apiole/getallsubtopics/<topic>', methods=('GET', ))
def getAllSubTopics(topic) :
    return questionsBanks.getSubTopics(topic)
