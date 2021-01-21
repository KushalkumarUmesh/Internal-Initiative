from peerreview import db,login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return EmployeeDetails.query.get(int(user_id))

class EmployeeDetails(db.Model,UserMixin):
    __tablename__ = 'PRD_EMPLOYEE_DETAILS'

    id = db.Column(db.Integer,primary_key=True)
    EMP_NAME = db.Column(db.Unicode(30))
    LOGIN_USR_ID = db.Column(db.Unicode(50),unique=True,index=True)
    LOGIN_PASSWORD = db.Column(db.Unicode(120))
    USR_LEVEL_ID = db.Column(db.Integer,db.ForeignKey('PRD_USER_LEVEL.USR_LEVEL_ID'),nullable=False)
    USR_STATUS_ID = db.Column(db.Integer,db.ForeignKey('PRD_USER_STATUS.USR_STATUS_ID'),nullable=False)
    CREATED_AT = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    CREATED_BY = db.Column(db.Unicode(20))

    def __init__(self,EMP_NAME,LOGIN_USR_ID,LOGIN_PASSWORD,USR_LEVEL_ID,USR_STATUS_ID):
        self.EMP_NAME = EMP_NAME
        self.LOGIN_USR_ID = LOGIN_USR_ID
        self.LOGIN_PASSWORD = generate_password_hash(LOGIN_PASSWORD) 
        self.USR_LEVEL_ID = USR_LEVEL_ID
        self.USR_STATUS_ID = USR_STATUS_ID

    def __repr__(self):
        return f"User Name: {self.EMP_NAME} and Email: {self.LOGIN_USR_ID} and User Level ID: {self.USR_LEVEL_ID} and UserStatus ID: {self.USR_STATUS_ID}"


class UserLevel(db.Model):
    __tablename__ = 'PRD_USER_LEVEL'

    USR_LEVEL_ID = db.Column(db.Integer,primary_key=True)
    USR_LEVEL = db.Column(db.Unicode(20))

    def __init__(self,USR_LEVEL):
        self.USR_LEVEL = USR_LEVEL

    def __repr__(self):
        return f"User Level ID: {self.USR_LEVEL_ID} and User Level is: {self.USR_LEVEL}"


class UserStatus(db.Model):
    __tablename__ = 'PRD_USER_STATUS'

    USR_STATUS_ID = db.Column(db.Integer,primary_key=True)
    USR_STATUS = db.Column(db.Unicode(20))

    def __init__(self,USR_STATUS):
        self.USR_STATUS = USR_STATUS

    def __repr__(self):
        return f"User Status ID: {self.USR_STATUS_ID} and User Status is: {self.USR_STATUS}"


class Login(db.Model):
    __tablename__ = 'PRD_LOGIN_INFO'

    LOGIN_INFO_KEY = db.Column(db.Integer,primary_key=True)
    LOGIN_NAME = db.Column(db.String(50))
    LOGIN_USR_ID = db.Column(db.String(50),unique=True,index=True)
    LOGIN_DATE = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __init__(self,LOGIN_NAME,LOGIN_USR_ID,LOGIN_DATE):
        self.LOGIN_NAME = LOGIN_NAME
        self.LOGIN_USR_ID = LOGIN_USR_ID
        self.LOGIN_DATE = LOGIN_DATE


class ChecklistDetails(db.Model):
    __tablename__ = 'PRD_CHECKLIST_DETAILS'

    CHECKLIST_ID = db.Column(db.Integer,primary_key=True)
    CHECKLIST_NAME = db.Column(db.Unicode(50))
    TYPE_ID = db.Column(db.Integer,db.ForeignKey('PRD_TESTING_TYPE.TYPE_ID'),nullable=False)

    def __init__(self,CHECKLIST_NAME,TYPE_ID):
        self.CHECKLIST_NAME = CHECKLIST_NAME
        self.TYPE_ID = TYPE_ID

    def __repr__(self):
        return f"Checklist Name: {self.CHECKLIST_NAME} and Type Id: {self.TYPE_ID}"


class TestingType(db.Model):
    __tablename__ = 'PRD_TESTING_TYPE'

    TYPE_ID = db.Column(db.Integer,primary_key=True)
    TESTING_TYPE = db.Column(db.Unicode(50))

    def __init__(self,TESTING_TYPE):
        self.TESTING_TYPE = TESTING_TYPE

    def __repr__(self):
        return f"Type ID: {self.TYPE_ID} and Testing Type is: {self.TESTING_TYPE}"


class BusinessInfo(db.Model):
    __tablename__ = 'PRD_BUSINESS_INFO'

    BUSINESS_INFO_KEY = db.Column(db.Integer,primary_key=True)
    LOGIN_USR_ID = db.Column(db.Unicode(50),unique=True,index=True)
    REVIEW_TASK_ID = db.Column(db.Integer,db.ForeignKey('PRD_REVIEW_TASK.REVIEW_TASK_ID'),nullable=False)
    CREATED_AT = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    CREATED_BY = db.Column(db.Unicode(20))

    def __init__(self,LOGIN_USR_ID,REVIEW_TASK_ID):
        self.LOGIN_USR_ID = LOGIN_USR_ID
        self.REVIEW_TASK_ID = REVIEW_TASK_ID

    def __repr__(self):
        return f"Business Info Id: {self.BUSINESS_INFO_KEY} and Logged In User: {self.LOGIN_USR_ID} and Review Task ID: {self.REVIEW_TASK_ID}"


class ReviewTask(db.Model):
    __tablename__ = 'PRD_REVIEW_TASK'

    REVIEW_TASK_ID = db.Column(db.Integer,primary_key=True)
    REVIEW_TASK = db.Column(db.Unicode(50))

    def __init__(self,REVIEW_TASK):
        self.REVIEW_TASK = REVIEW_TASK

    def __repr__(self):
        return f"Review Task ID: {self.REVIEW_TASK_ID} and Review Task is: {self.REVIEW_TASK}"


class CreateProject(db.Model):
    __tablename__ = 'PRD_CREATE_PROJECT'

    PRJ_KEY = db.Column(db.Integer,primary_key=True)
    PRJ_NAME = db.Column(db.String(50))
    MANUAL_CHECKLIST = db.Column(db.String(30))
    MANUAL_DEFECT_CHECKLIST = db.Column(db.String(30))
    MANUAL_TESTCASE_CHECKLIST = db.Column(db.String(30))
    MANUAL_TRACEABILITY_CHECKLIST = db.Column(db.String(30))
    AUTOMATION_CHECKLIST = db.Column(db.String(30))
    AUTO_STD_CHECKLIST = db.Column(db.String(30))
    AUTO_PYTHON_CHECKLIST = db.Column(db.String(30))
    AUTO_JAVA_CHECKLIST = db.Column(db.String(30))
    AUTO_C_CHECKLIST = db.Column(db.String(30))
    AUTO_TOSCA_CHECKLIST = db.Column(db.String(30))
    AUTO_UFT_CHECKLIST = db.Column(db.String(30))
    MANAGEMENT_CHECKLIST = db.Column(db.String(30))
    MGMT_TESTPLAN_CHECKLIST = db.Column(db.String(30))
    MGMT_TESTREPORT_CHECKLIST = db.Column(db.String(30))
    MGMT_TESTENVISETUP_CHECKLIST = db.Column(db.String(30))
    PERFORMANCE_CHECKLIST = db.Column(db.String(30))
    SECURITY_CHECKLIST = db.Column(db.String(30))
    SPOC_ID = db.Column(db.String(50),nullable=False)
    REVIEWERS = db.Column(db.String(50))
    FREQUENCY_ID = db.Column(db.String(30))
    CREATED_AT = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __init__(self,PRJ_NAME,MANUAL_CHECKLIST,MANUAL_DEFECT_CHECKLIST,MANUAL_TESTCASE_CHECKLIST,MANUAL_TRACEABILITY_CHECKLIST,AUTOMATION_CHECKLIST,AUTO_STD_CHECKLIST,AUTO_PYTHON_CHECKLIST,AUTO_JAVA_CHECKLIST,AUTO_C_CHECKLIST,AUTO_TOSCA_CHECKLIST,AUTO_UFT_CHECKLIST,MANAGEMENT_CHECKLIST,MGMT_TESTPLAN_CHECKLIST,MGMT_TESTREPORT_CHECKLIST,MGMT_TESTENVISETUP_CHECKLIST,PERFORMANCE_CHECKLIST,SECURITY_CHECKLIST,SPOC_ID,REVIEWERS,FREQUENCY_ID):

        self.PRJ_NAME = PRJ_NAME
        self.MANUAL_CHECKLIST = MANUAL_CHECKLIST
        self.MANUAL_DEFECT_CHECKLIST = MANUAL_DEFECT_CHECKLIST
        self.MANUAL_TESTCASE_CHECKLIST = MANUAL_TESTCASE_CHECKLIST
        self.MANUAL_TRACEABILITY_CHECKLIST = MANUAL_TRACEABILITY_CHECKLIST
        self.AUTOMATION_CHECKLIST = AUTOMATION_CHECKLIST
        self.AUTO_STD_CHECKLIST = AUTO_STD_CHECKLIST
        self.AUTO_PYTHON_CHECKLIST = AUTO_PYTHON_CHECKLIST
        self.AUTO_JAVA_CHECKLIST = AUTO_JAVA_CHECKLIST
        self.AUTO_C_CHECKLIST = AUTO_C_CHECKLIST
        self.AUTO_TOSCA_CHECKLIST = AUTO_TOSCA_CHECKLIST
        self.AUTO_UFT_CHECKLIST = AUTO_UFT_CHECKLIST
        self.MANAGEMENT_CHECKLIST = MANAGEMENT_CHECKLIST
        self.MGMT_TESTPLAN_CHECKLIST = MGMT_TESTPLAN_CHECKLIST
        self.MGMT_TESTREPORT_CHECKLIST = MGMT_TESTREPORT_CHECKLIST
        self.MGMT_TESTENVISETUP_CHECKLIST = MGMT_TESTENVISETUP_CHECKLIST
        self.PERFORMANCE_CHECKLIST = PERFORMANCE_CHECKLIST
        self.SECURITY_CHECKLIST = SECURITY_CHECKLIST
        self.SPOC_ID = SPOC_ID
        self.REVIEWERS = REVIEWERS
        self.FREQUENCY_ID = FREQUENCY_ID

    def __repr__(self):
        return f"Project Name: {self.PRJ_NAME} and Reviewer: {self.REVIEWERS } and SPOC ID: {self.SPOC_ID} and FREQUENCY: {self.FREQUENCY_ID}"



class Frequency(db.Model):
    __tablename__ = 'PRD_FREQUENCY'

    FREQUENCY_ID = db.Column(db.Integer,primary_key=True)
    FREQUENCY_TYPE = db.Column(db.Unicode(20))

    def __init__(self,FREQUENCY_TYPE):
        self.FREQUENCY_TYPE = FREQUENCY_TYPE

    def __repr__(self):
        return f"Frequency ID: {self.FREQUENCY_ID} Frequency Type is: {self.FREQUENCY_TYPE}"
