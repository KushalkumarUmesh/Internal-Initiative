"""
K.Srinivas, 22-Mar-2018

Project: Multiple (starting with OnlineExam, Goalsheet)
Description: This is the view+controller for the listing and editing data in the legacy HRMS. The original HRMS, designed as portlets
    in Liferay 6.2 has become a maintance challenge due to lack of source-code control and other reasons. However, it has
    lot of existing functionality that can be enhanced/used. In addition, maintance of master-data (list of managers, departments, etc.)
    and reports requires direct DB-access and SQL scripting. This is an attempt to augment the existing functionality and also use
    the existing data in newer application. Currently the following services are planned.

getEmployee - Given the liferay userID, get the Employee Object
getDCLead - given Employee Object, get DC-lead
getLineManager - given Employee Object, get manager
get2ndLineManager - given Employee Object, get manager
getDepartment - given Employee Object, get Dept.

TODO: 
a) Define a full list of methods needed to support the requirements. This is an ongoing process but the initial few are identified.

KNOWN BUGs: None
"""

from flask_wtf import FlaskForm 
from wtforms import *
from wtforms.validators import DataRequired
from flask_login import login_required, current_user
from flask import render_template, redirect, request, flash
from realapp import app, login_manager, testBank , csrf

from hrmsmodels import *
from hrmsdomain import *
from hrmsdatafix import *
from hrmsempdata import *

#### GoalSheet myprofile
@app.route('/goals/myprofile', methods = ['GET'])
@login_required
def myprofile() :
    return render_template('goalsheet/myprofile.html',msgDict = getEmpDictbyEmail(current_user.username))

@app.route('/hrms', methods=['GET'])
def hrmshome() :
    return app.send_static_file('hrmshome.html')

#TODO: Make this ADMIN only OR remove the Select Field (i.e a person can assign exams to himself/herself)
@app.route('/hrms/hrmslist', methods=('GET', 'POST'))
def hrmslist() :
    emp = getAllEmployees()
    retstr = ""
    for e in emp :
        retstr += "Name:%s, Emp.No:%s, email=%s" % (e.FIRST_NAME, e.Manager_ID, e.OFFICE_EMAIL_ID) + "<p>"
    return (retstr)

@app.route('/hrms/getmgr', methods=('GET', 'POST'))
def getMgr() :
    return getLineManager('srinivas.kambhampati@msg-global.com')

@app.route('/hrms/fixmgr', methods=('GET', 'POST'))
def fixMgr() :
    fixReportingManagerAll()
    return ("Employee-table, Manager_ID fixes for all employees...please check in DB")

#Created for Siddu and Shubham so that can work on this
@app.route('/hrms/getmyprofile/<email>', methods=('GET', 'POST'))
def getMyProfile(email) :
    msgDict = getEmpDictbyEmail(email)
    return render_template ('goalsheet/myprofile.html', msgDict = msgDict)

#No Definition of getEmpProfile
@app.route('/hrms/getprofile/<email>', methods=('GET', 'POST'))
def getProfile(email) :
    message= getEmpProfile(email)
    message = "<html><body>" + message + "</body></html>"
    return ( message)


@app.route('/hrms/senddatamissingmsgtoall', methods=('GET', 'POST'))
def sendDataMissingMsg() :
#    return sendDataMissingMsgToAll(sendEmailToEmp=True)
    return dataMissingMsg(email="sunil.rathod@msg-global.com")

@app.route('/hrms/getempinfo', methods=('GET', 'POST'))
def getEmpInfo() : 
    return getEmpProfile('srinivas.kambhampati@msg-global.com')

#For Testing/Display only.
@app.route('/hrms/getreportees/<email>', methods=['GET'])
def getReporteesbyManagerEmail(email) :
    reportees = getReportees(email)
    myStr = ""
    for r in reportees :
        myStr += empToString(r)
    return myStr        

@app.route('/hrms/getDCmembers/<id>', methods=['GET'])
def getDCmembers(id) :
    reportees = getEmployeesInDC(id)
    myStr = ""
    for r in reportees :
        myStr += empToString(r)
    return myStr        

@app.route('/hrms/notifyAllEmployees', methods=('GET', 'POST'))
def notifyAllEmployees() :
    getAllDCs()
    getAllManagers()
    return "See Console Log"

@app.route('/hrms/listallmanagers', methods=('GET', 'POST'))
def listallmanagers() :
    retstr = ""
    msgrs = getAllManagers()
    for e in msgrs :
        retstr += "Name:%s, Emp.No:%s, email=%s" % (e.FIRST_NAME, e.Manager_ID, e.OFFICE_EMAIL_ID) + "<p>"
    return (retstr)

@app.route('/hrms/listalldcleads', methods=('GET', 'POST'))
def listalldcleads() :
    retstr = ""
    msgrs = getAllDCLeads()
    for e in msgrs :
        retstr += "Name:%s, Emp.No:%s, email=%s" % (e.FIRST_NAME, e.Manager_ID, e.OFFICE_EMAIL_ID) + "<p>"
    return (retstr)


@app.route('/hrms/fixReportingManagers', methods=('GET', 'POST'))
def fixReportingManagers() :
    fixManagers()
    return "Done"
