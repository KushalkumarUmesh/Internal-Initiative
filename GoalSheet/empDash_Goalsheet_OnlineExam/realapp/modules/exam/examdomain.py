"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: These are the domain methods for the Exam module. 
    a) getTests: Returns a set of lists containing Test-attributes for ALL tests.
    b) updateTest: Updates the Exam Object and all the Questions with the answers given

TODO: This was written when I was not fully up to speed on Jinja templates. getTests() is not really required.
The values can be populated directly in the template

KNOWN BUGs: None
"""
#from realapp import db, app, testBank, csrf
import datetime as dt
from realapp import testBank

from assignmodel import ExamObj, QuestionSet

#TODO: Map request.form.key to Question-ID : This needs to be done in examanswer first and correct dict sent here

def getTests() :
    tlist = testBank.getTestList(retType = 'D')
    tnames = []
    tdesc = []
    tnumq = []
    tpass = []
    tdiff =[]

    for k in tlist.keys() :
        tnames.append(k)
        tdesc.append(tlist[k])
        tnumq.append(testBank.getTestNoOfQuestions(k))
        tpass.append(testBank.getTestPassNum(k))
        tdiff.append(testBank.getTestDifficultyLevel(k))
    return (tnames, tdesc, tnumq , tpass, tdiff )

def updateTest(exam, qlist) :
    rights = 0 
    wrongs = 0
    for i in range(0,len(qlist)) :
        ca = qlist[i].getCorrectAnswer().upper()
        ans = qlist[i].getSelectedOption()
        # Update Score
        if (ans.endswith(ca)) :
            rights += 1
        else :
            wrongs += 1

    if rights >= exam.passNum :
        res = "Passed"
        exam.updateAfterTest(res,rights) # Needs to be here as res is defined based on Pass/Fail
        return (True, rights) # Passed 
    else :
        res = "Failed"
        exam.updateAfterTest(res,rights)
        return (False, rights) # Failed

def markInprogress(exam) :
    exam.updateBeforeTest()
    return 

def getTestList(email, is_admin=False) :
    if is_admin :
        elist = ExamObj.query.order_by(ExamObj.dtAssigned.desc()).all()        
    else : 
        elist = ExamObj.query.filter( ExamObj.examStatus != "Completed", ExamObj.candiateEmail == email).all()
        elist += ExamObj.query.filter (ExamObj.examStatus == "Completed", ExamObj.candiateEmail == email).all()
    return elist

