# My modules/and stuff
import sys

from flask import Flask
# Login Implimentation
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_apscheduler import APScheduler


sys.path.insert(0, 'realapp')
sys.path.insert(0, 'realapp/modules')
sys.path.insert(0, 'realapp/modules/masterdata')
sys.path.insert(0, 'realapp/modules/exam')
sys.path.insert(0, 'realapp/modules/assigntest')
sys.path.insert(0, 'realapp/modules/goalsheet')
sys.path.insert(0, 'realapp/modules/scheduledjobs')
sys.path.insert(0, 'realapp/shared/hrms')
sys.path.insert(0, 'realapp/shared/candidateinterface')
sys.path.insert(0, 'realapp/shared/readconfig')
sys.path.insert(0, 'realapp/shared/notification')
sys.path.insert(0, '../..')

# from candidateinterface import CandidateInteface
from questionbank import QuestionBank
from testbank import TestBank
from appconfig import AppConfig
from flask_cache import Cache

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

# Create our own items and get ready
# TODO: ALl DB Parameters need to come from the XLS-FILE..but that gets more UNSAFE from security perspective
appC = AppConfig("OnlineExamConfig.xlsx")
questionsBanks = QuestionBank(appC)
testBank = TestBank(appC)
testBank.setQuestionBank(questionsBanks)
testBank.checkConsistancy()

# app = Flask(__name__)

# login = LoginManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.unauthorized_handler = '/login'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://ks:Kambh12#@localhost:3306/online_exam"
app.config['SECRET_KEY'] = "ZXFGHJKLPwefghjm"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_SECRET_KEY'] = 'srini random string'
# Setting Debug true
app.config['DEBUG'] = True
app.config["SQLALCHEMY_BINDS"] = {
    'goalsheet': 'mysql://ks:Kambh12#@localhost:3306/goal_sheet',
    'hrms': 'mysql://ks:Kambh12#@localhost:3306/hrms',
    'bcsproj': 'mysql://ks:Kambh12#@localhost:3306/bcsproj',
    'hrmsdocuments': 'mysql://ks:Kambh12#@localhost:3306/hrmsdocuments'
}

app.config['DOCTYPE_TASK'] = 1
app.config['DOCTYPE_SHEET'] = 3


UPLOAD_FOLDER = 'C:/onlineexam'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xls', 'xlsx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit File-Upload SIZE to 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#Element TYPE definition used in Feedback and AskFeedback domains
ELEMENT_TYPE_SHEET = 1
ELEMENT_TYPE_GOAL = 2
ELEMENT_TYPE_TASK = 3

# Start DB Session
db = SQLAlchemy(app)

#Task Scheduler
myscheduler = APScheduler()
myscheduler.init_app(app)
myscheduler.start()

#################################################################################################################################
#Extremely Common Methods
#Small method to confirm that empID obtained is really an Int
def RepresentsInt(s):
    if not s:
        return False
    try: 
        int(s)
        return True
    except ValueError:
        return False



#################################################################################################################################

if __name__ == "__main__":
    print(str(testBank))
