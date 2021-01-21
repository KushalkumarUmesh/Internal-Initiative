#My modules/and stuff

import sys
import os
sys.path.insert(0,'realapp')
sys.path.insert(0,'realapp/modules')
sys.path.insert(0,'realapp/modules/masterdata')
sys.path.insert(0,'realapp/modules/bcsdata')
sys.path.insert(0,'realapp/modules/scheduledjobs')
sys.path.insert(0,'realapp/modules/exam')
sys.path.insert(0,'realapp/modules/assigntest')
sys.path.insert(0,'realapp/modules/goalsheet')
sys.path.insert(0,'realapp/shared/hrms')
sys.path.insert(0,'realapp/shared/candidateinterface')
sys.path.insert(0,'realapp/shared/readconfig')
sys.path.insert(0,'realapp/shared/notification')
sys.path.insert(0,'realapp/shared/emails')
sys.path.insert(0,'realapp/shared/fileupload')
sys.path.insert(0,'../..')
from realapp import app, csrf, db

from home import home
from login import *

from assignview import *
from exam import examview

from hrmsview import *
from hrmslistmanagement import *

from bcsprojview import *
from bcsdataloadview import *
from bcscheckview import *

from goalview import *
from goaldisplay import *
from goaldisplaymanagers import *
from calendarview import *
from goalassignment import *
from goalsheetmgmt import *
from feedbackview import *
from goaljson import *
from askfeedbackview import *

from notificationview import *
from hrmscron import hrmsScheduleTasks, goalScheduleTasks

from documentmodel import *

from onetimefix import * #Goal Sheet weight and other fixes
from apiole import *

"""
from loadtargetview import *

"""


"""
#Create our own items and get ready
#TODO: ALl DB Parameters need to come from the XLS-FILE..but that gets more UNSAFE from security perspective
appC = AppConfig("C:\\Users\\kambhs\\Desktop\\Projects\\OnlineExam\\OnlineExamConfig.xlsx")
questionsBanks = QuestionBank(appC)
testBank = TestBank(appC)
testBank.setQuestionBank(questionsBanks)
"""

if app.config['DEBUG']:
    #print("Dropping all tables and re-creating them")
#    db.drop_all(bind = 'bcsproj')
    db.create_all(bind = 'goalsheet')
    db.create_all(bind = 'hrmsdocuments')
    app.debug = True
#    readBCSClaimData("C:\\Users\\kambhs\\Desktop\\Learning\\OpenPyxl\\BCS\\Employee BCS Bookings_May18_21-05-2018.xlsx")

#Check if On PROD
OnPROD=False

if os.path.isfile('E:/onlineexam/thisisprod.txt') :
    OnPROD=True

#Disaster created by scheduled tasks running on UAT DB and sending bogus e-mails caused this one :-(
if OnPROD :
    from waitress import serve
    hrmsScheduleTasks() # Start the jobs automatically from hrmscron.py
    goalScheduleTasks() # 
    serve(app, host='0.0.0.0', port=5000, threads=10)
else :
    app.run(host = '0.0.0.0', port=5000)