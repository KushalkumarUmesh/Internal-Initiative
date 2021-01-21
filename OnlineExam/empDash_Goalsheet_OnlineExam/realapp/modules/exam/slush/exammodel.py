"""
a)	Exam-ID (Unique-Key) – Created automatically when an EXAM is “assigned” to a person
b)	Assigned To –Candidate – Emp. No? e-mail ID? Login-name?
c)	PassNum- Default copied from the test, but can be changed
d)	Date Start (Date after which a candidate can take the exam)
e)	Date Due (Date before which a candidate can take the exam)
f)	Date assigned (today’s date, automatically entered)
g)	Date Completed –Actual completion date – After the candidate passes the exam
h)	Date Last Notified (Date when last e-mail, with whatever content was sent)
i)	Max No. of attempts allowed
j)	No. of attempts made
k)	Result-Status : Result of the last exam attempted:  NotAttempted, Pass, Fail : 
l)	Action-Status: Management-status of the exam: Planned, Due (Start date has passed), OverDue (Due Date has passed), Withdrawn
Need to Decide How to store and retrieve this aggregates
Create a separate table for this one
m)-	Set of Questions (Do we store in JSON format in DB?) – Created at the time of exam assignment, cannot be changed later. If needed, delete the exam and re-assign
n)-	Set of Answers (Selected by the Candidate) [Storage format?, separate table for questions/answers with exam-ID?] – Stored along with EACH attempt.
"""
from realapp import db
import datetime as dt


class ExamObj(db.Model):
    examId =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    testName = db.Column(db.String(80), nullable=False )
    candiateEmail = db.Column(db.String(120),  nullable=False )
    candiateID = db.Column(db.Integer, nullable=False )
    numQuestions = db.Column(db.Integer,  nullable=False  )
#    candiateEmail = db.Column(db.String(120), unique=True, nullable=False ) # Candidate can have multiple exams
#    candiateID = db.Column(db.Integer, unique=True, nullable=False )
    passNum = db.Column(db.Integer,  nullable=False  )
    numAttemptsAllowed = db.Column(db.Integer,  nullable=False  )
    numAttemptsMade = db.Column(db.Integer,  nullable=False  )
    dtAssigned = db.Column(db.DateTime)
    dtCompleted = db.Column(db.DateTime)
    dtStart = db.Column(db.DateTime)
    dtDue = db.Column(db.DateTime)
    dtLastNotified = db.Column(db.DateTime)
    score = db.Column(db.Integer,  nullable=False  )
    resultStatus = db.Column(db.String(80), nullable=False )
    examStatus = db.Column(db.String(80), nullable=False )
    
    def __init__(self, testName, candiateEmail,candiateID,numQuestions, passNum,numAttemptsAllowed,numAttemptsMade,dtAssigned, \
        dtCompleted ,dtStart, dtDue,dtLastNotified, score, resultStatus, examStatus  ):
        self.testName = testName
        self.candiateEmail = candiateEmail
        self.candiateID = candiateID
        self.numQuestions = numQuestions
        self.passNum = passNum
        self.numAttemptsAllowed = numAttemptsAllowed
        self.numAttemptsMade = numAttemptsMade
        self.dtAssigned = dtAssigned
        self.dtCompleted = dtCompleted
        self.dtStart = dtStart
        self.dtDue = dtDue
        self.dtLastNotified = dtLastNotified
        self.score = score
        self.resultStatus = resultStatus
        self.examStatus = examStatus
    
    def __repr__(self):
        return '<candiateEmail %r>' % self.candiateEmail

class QuestionSet(db.Model) :
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    examId = db.Column(db.Integer, db.ForeignKey("exam_obj.examId") ) # This comes from the ExamObj
    question = db.Column(db.String(240), nullable=False )
    optionA = db.Column(db.String(80), nullable=False )
    optionB = db.Column(db.String(80), nullable=False )
    optionC = db.Column(db.String(80), nullable=False )
    optionD = db.Column(db.String(80), nullable=False )
    difficulty = db.Column(db.String(10), nullable=False )
    correctAnswer = db.Column(db.String(2), nullable=False )
    description = db.Column(db.String(500) )
    selectedOption = db.Column(db.String(2) )
   
    def __init__(self,examId,question,optionA,optionB,optionC,optionD, difficulty, correctAnswer, \
        description,  selectedOption  ):
        self.examId = examId
        self.question = question
        self.optionA = optionA
        self.optionB = optionB
        self.optionC = optionC
        self.optionD = optionD
        self.difficulty = difficulty
        self.correctAnswer = correctAnswer
        self.description = description
        self.selectedOption = selectedOption
    
    def __repr__(self):
        return '<question %r>' % self.question

