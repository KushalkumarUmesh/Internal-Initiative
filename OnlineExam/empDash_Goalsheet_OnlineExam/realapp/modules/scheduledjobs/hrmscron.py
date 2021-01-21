"""
K.Srinivas, 18-May-2018

Project: Hrms and others
Description: This implements the basic Scheduler functionality for scheduling CRON jobs.
Currently implemented:
    - Happy B'day
    - Anniversary e-mail

TODO: 
a) Define a pages for listing, starting and stoping jobs
b) Jobs for: Weekly reminders for filling various fields
c) Job for: Reminders before Passport expiry

KNOWN BUGs: None
"""
import logging

from flask import render_template, redirect, request
from realapp import app, myscheduler
from flask_apscheduler import *
from hrmsjobs import notifyOnBirthDate, notifyOnWorkAnniversary, notifyOnDataMissing
from goalcron import *
#from apscheduler.triggers.interval import add_interval_job
#from apscheduler.schedulers.background import BackgroundScheduler



@app.route('/schedule', methods = ['GET'])
def schedule() :
    return hrmsScheduleTasks()

def hrmsScheduleTasks():
#    job=myscheduler.add_job(func=myjob, trigger='cron',  hour=11,  minute=42, id="Myjob" ) 
    job1=myscheduler.add_job(func=notifyOnBirthDate, trigger='cron', hour=0, minute=30, id="BirthdayWishes" ) 
    job2=myscheduler.add_job(func=notifyOnWorkAnniversary, trigger='cron', hour=0, minute=35, id="WorkAnniversary" ) 
    #HRMS-Data Fix Nag e-mail, Mon, Wed, Fri
    job3=myscheduler.add_job(func=notifyOnDataMissing, trigger='cron', day_of_week="0,2,4", hour=8, minute=30, id="HRMSDataFix" )

    retStr = "From Schedule:"
    for j in myscheduler.get_jobs() :
        retStr += str(j) + '\n'
    return retStr

def goalScheduleTasks():
    #Job to send emails for any feedback requests
    job4=myscheduler.add_job(func=notifyFeedbackToEmployees, trigger='interval', minutes=15 , id="notifyFeedbackToEmployees" )
    #Job to send check for errors in goal-calendar, send e-mail to GoalSheetAdmins group
    job5=myscheduler.add_job(func=calFlagsVerifyCron, trigger='cron', hour=0, minute=10 , id="calFlagsVerifyCron" )
    #Job to send emails for Ask For Feedback requests
    job6=myscheduler.add_job(func=sendAskFeedbackNotificationsCron, trigger='interval', minutes=5 , id="sendAskFeedbackNotificationsCron" )

    retStr = "From Schedule:"
    for j in myscheduler.get_jobs() :
        retStr += str(j) + '\n'
    return retStr

#For Manually clearing the calandar flags
#Method for testing the jobs by calling directly instead of the scheduler
@app.route('/clearcalcache', methods = ['GET'])
def clearCalCache():
    calFlagsVerifyCron()
    return "calFlagsVerifyCron Called..for clearing the cache...check console"


#For TESTING ONLY
#Method for testing the jobs by calling directly instead of the scheduler
# @app.route('/calldirect', methods = ['GET'])
# def calldirect():
#     #return notifyOnBirthDate()
#     calFlagsVerifyCron()
# #    sendAskFeedbackNotificationsCron()
#     return "calFlagsVerifyCron Called..check console"
"""
def myjob() :
    import datetime as dt
    t = dt.datetime.now()
    app.logger.info("This is a job:%s \n" % ( str(t)) )

#This works perfectly. Copied here for future ref.
@app.route('/schedule', methods = ['GET'])
def scheduletask():
#Definition, init and Start moved to realapp/__init__.py
    #myscheduler = APScheduler()
    #myscheduler.init_app(app)
#    job=myscheduler.add_job(func=myjob, trigger='cron',  hour=11,  minute=36, id="Myjob" ) 
    job1=myscheduler.add_job(func=notifyOnBirthDate, trigger='cron', hour=0, minute=30, id="BirthdayWishes" ) 
    job2=myscheduler.add_job(func=notifyOnWorkAnniversary, trigger='cron', hour=0, minute=35, id="WorkAnniversary" ) 
#    myscheduler.start()
    retStr = "From Schedule:"
    for j in myscheduler.get_jobs() :
        retStr += str(j) + '\n'
    return retStr

def myjob() :
    import datetime as dt
    t = dt.datetime.now()
    print("This is a job:%s \n" % ( str(t)) )

#    scheduler = BackgroundScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True

    # Run every 2nd minute of every hour
    #job=scheduler.add_job(func=myjob, trigger='cron',  minute=2, id="Myjob" ) 
    # Run every day at 10:02 PM
    #job=scheduler.add_job(func=myjob, trigger='cron',  hour=22, minute=2, id="Myjob" ) 
    # Internal-timer : every 2 seconds    
    #job=scheduler.add_job(func=myjob, trigger='interval',  seconds=2, id="Myjob" ) 
    # Run every Sunday at 10:2 PM
#    job=scheduler.add_job(func=myjob, trigger='cron',  day_of_week=6, hour=22, minute=2, id="Myjob" ) 
"""