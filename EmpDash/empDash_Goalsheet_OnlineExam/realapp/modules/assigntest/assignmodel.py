"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: Model (DB-link) defining the Exam and QuestionSet Classes have the save/add methods and should be used. 
    db object should NOT be imported anywhere except in the model-classes
TODO: None

KNOWN BUGs: None
"""

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
    
    def __init__(self, testName="", candiateEmail="",candiateID=0,numQuestions=0, passNum=0,numAttemptsAllowed=0, \
        numAttemptsMade=0,dtAssigned=dt.date(2000,1,1), dtCompleted=dt.date(2000,1,1) ,dtStart=dt.date(2000,1,1), \
        dtDue =dt.date(2000,1,1),dtLastNotified=dt.date(2000,1,1), score=0, \
        resultStatus = "NA", examStatus = "Assigned"  ):
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

#Update the data after candidate has taken the test
    def updateAfterTest(self, resultStatus, score, examStatus = "Completed", dtCompleted=dt.datetime.today(), dtLastNotified=dt.datetime.today()) :
        self.resultStatus = resultStatus # Pass/Fail
        self.score = score
        self.examStatus = examStatus
        self.dtCompleted = dtCompleted
        self.dtLastNotified = dtLastNotified
        self.numAttemptsMade += 1 # bump-up the number of attemps
        db.session.commit() # Commit to DB
        return    

#Update the data before candidate has completed the test (but after starting)
    def updateBeforeTest(self, examStatus = "Started") :
        self.examStatus = examStatus
        self.numAttemptsMade += 1 # bump-up the number of attemps
        db.session.commit() # Commit to DB
        return    


# This one needs work
# DB COmmit should have a try-catch, will add once UI validation is done
    def add(self) :
        db.session.add(self)
        db.session.commit()
        return 

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

#Update Question After the test
    def updateAfterTest(self, selectedOption) :
        self.selectedOption = selectedOption # add the answer
        return   # don't Commit to DB

    def getSelectedOption(self) :
        return self.selectedOption # add the answer
    
    def getCorrectAnswer(self) :
        return self.correctAnswer # add the answer

# Put a error handler instead of try-catch here
# DB COmmit should have a try-catch, will add once UI validation is done
    def addNocommit(self) :
        db.session.add(self)
        return

    def commit(self) :
        db.session.commit()
        return 

    def __repr__(self):
        return '<question %r>' % self.question
