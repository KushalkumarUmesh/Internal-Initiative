"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: This implements the top-level home and index view

TODO: Redirect to different pages depending on logged-in (yes/no) and Admin(yes/no)
TODO: Test after removing all teh imports. -DONE

KNOWN BUGs: None
"""
import logging

from flask import render_template, redirect, request, session
from realapp import app
from flask_apscheduler import *
#from apscheduler.triggers.interval import add_interval_job
#from apscheduler.schedulers.background import BackgroundScheduler


#Do NOT put @login_required here!! These are the default-pages someone could come to.
#No Application is specified..need a app-neutral page
@app.route('/index.html', methods = ['GET'])
@app.route('/', methods = ['GET'])
def home() :
    return render_template('home.html')

#OLE
@app.route('/ole/index.html', methods = ['GET'])
@app.route('/ole', methods = ['GET'])
@app.route('/ole/', methods = ['GET'])
def olehome() :
    return render_template('home.html')

#goalsheet
@app.route('/goals/index.html', methods = ['GET'])
@app.route('/goals', methods = ['GET'])
@app.route('/goals/', methods = ['GET'])
def goalhome() :
    return render_template('goalsheet/goalhome.html')

#bcsproj
@app.route('/bcsproj/index.html', methods = ['GET'])
@app.route('/bcsproj/', methods = ['GET'])
@app.route('/bcsproj', methods = ['GET'])
def goalprojs() :
    return render_template('bcsdata/projhome.html')

@app.route('/unauthorized', methods = ['GET'])
def unauthorized() :
    return render_template('unauthorized.html')

def index() :
    return redirect('/home')

#Method to show "all pages" available
@app.route('/showroutes', methods = ['GET'])
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)
    return str(output)


#POC for scheduleing Jobs, to be used for various reasons
#https://apscheduler.readthedocs.io/en/v2.1.2/cronschedule.html
## Simple internal executiion
    #sched.add_interval_job(job_function, hours=2) 
## Cron-style executiion
    #sched.add_cron_job(job_function, month='6-8,11-12', day='3rd fri', hour='0-3') 
## "at" style one-time executiion
    #job = sched.add_date_job(my_job, datetime(2009, 11, 6, 16, 30, 5), ['text'])
#scheduler.add_job(func, 'cron', day='1st tue')
#scheduler.add_job(func, 'cron', day='1st mon,3rd mon')
#scheduler.add_job(func, 'cron', day='1st fri,last fri')
#@sched.scheduled_job('cron', id='my_job_id', day='last sun')
#def some_decorated_task():
#    print("I am printed at 00:00:00 on the last Sunday of every month!")
"""
def myjob() :
    import datetime as dt
    t = dt.datetime.now()
    print("This is a job:%s \n" % ( str(t)) )

@app.route('/schedule', methods = ['GET'])
def scheduletask():
#    scheduler = BackgroundScheduler()
    scheduler = APScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    print(str(myjob))
    scheduler.init_app(app)
    # Run every 2nd minute of every hour
    #job=scheduler.add_job(func=myjob, trigger='cron',  minute=2, id="Myjob" ) 
    # Run every day at 10:02 PM
    #job=scheduler.add_job(func=myjob, trigger='cron',  hour=22, minute=2, id="Myjob" ) 
    # Internal-timer : every 2 seconds    
    #job=scheduler.add_job(func=myjob, trigger='internal',  seconds=2, id="Myjob" ) 
    # Run every Sunday at 10:2 PM
    job=scheduler.add_job(func=myjob, trigger='cron',  day_of_week=6, hour=22, minute=2, id="Myjob" ) 
    scheduler.start()
    return "From Schedule:" + str(job) + ":" + str(scheduler.get_jobs())
"""