"""
K.Srinivas, 22-Mar-2018

Project: Online Exam
Description: Login/Logout handler views
    a) load_user : This is the key menthod that needs to return the object passed to login_user with is_authorized=  True.

TODO: Add a "Remember Me" button

KNOWN BUGs: It is unclear, how the is_authorized flag should be reset. There was on unexpected logged-in status on fresh server start.
Needs further testing to confirm if the browser stored anything...

"""
from flask import  request, render_template, redirect, url_for, flash, session
from candidateinterface import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from wtforms import Form, TextField, PasswordField, validators, BooleanField, SelectField
from realapp import app, login_manager, csrf
from flask_wtf import FlaskForm 
from logindomain import *
import logging
from home import *
#from calendardomain import getValidYearsForSelect
"""
#For Checking authorization from HRMS
import requests
from requests.auth import HTTPBasicAuth
import json
hrmsAuthUrl = 'http://10.144.0.21:8091/api/jsonws/user/get-user-by-email-address/company-id/10155/email-address/'
"""

@login_manager.user_loader
def load_user(userid):
    return getLoggedInUser(userid)

class UserLoginForm(FlaskForm):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    assessmentYear = SelectField(u'Assessment Year', choices=[('2018-2019','2018-2019') ,('2019','2019')], default ='2019' )
    rememberme = BooleanField("Keep me logged in")


@app.route('/login/<appName>', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login(appName = ""):
#    print("user_agent.browser: chrome" + str(request.user_agent.browser) )
    browserStr = request.user_agent.browser
    if "edge" in browserStr or "msie" in browserStr or 'firefox' in browserStr:
        return render_template('message.html', message = "Please  use Chrome only. Other browsers, particularly IE and Edge are not supported.")

    form = UserLoginForm(request.form)
    #TODO: Generate this from valid years from Cal-table
    form.assessmentYear.choices = [('2018-2019','2018-2019') ,('2019','2019'),('2020','2020')] #Hard coded till 2020, else we create a dependency on goal-sheet Calendar module. How to deal with this?
    
    #Simplify - Handle GET first
#    print("AppName=" + appName)
    if appName :
        if appName == "goalsheet" :
#            print("Setting Templates for AppName=" + appName)
            loginTemplate = 'goalsheet/login.html'
            homeurl = 'goalhome'
        elif appName == "bcsproj" :
            loginTemplate = 'bcsdata/login.html'
            homeurl = 'projhome'
        elif appName == 'ole' :
            loginTemplate = 'login.html'
            homeurl = 'olehome'
        else :
            return   render_template('message.html', message = "Application specified cannot be found.")
    else : #No Application specified
            loginTemplate = 'login.html'
            homeurl = 'home'

    next = request.args.get('next')
    """
    if next :
        print ("Next=" + str(next))
        print ("Nextbcsproj=" + str(next.find("/bcsproj" , 0)))
        print ("Nextgoal=" + str(next.find("/goals", 0)))
        print ("Nextole=" + str(next.find("/ole", 0) ))
    """
    if next and (next.find("/bcsproj", 0) >= 0) :
        loginTemplate = 'bcsdata/login.html'
        homeurl = 'projhome'
    elif next and (next.find("/goals", 0) >= 0) :
        loginTemplate = 'goalsheet/login.html'
        homeurl = 'goalhome'
    elif next and (next.find("/ole", 0) >= 0) :
        loginTemplate = 'login.html'
        homeurl = 'olehome'

    if request.method == 'GET':
        return render_template(loginTemplate, form=form)

    if request.method == 'POST' and form.validate():
        #print("Next = " + str(next))
#         username=request.form["username"].strip().lower()
#         password=request.form["password"]
#         try :
#             lu = checklogin(username, password)
#         except :
#             app.logger.exception("HRMS-Unknown exception:%s" % (username))
#             flash("Authentication Failed due to an Internal Error. Please try after some time.") # Just put it here, just in case            
#             return render_template(loginTemplate, form=form)
#         else : # No exception            
#             if lu.is_authenticated :
# #                session.permanent = True
# #                app.permanent_session_lifetime = timedelta(minutes=5)
#                 login_user(lu)

# #                if request.form["assessmentYear"] :
#                 session['year'] = form.assessmentYear.data # Create and add session
# #                else: 
# #                session['year'] = '2018-2019' # For backward compatibility, should this go into production by mistake

#                 app.logger.info("Login Successful:%s" % (username))
#                 #Avoid logout AGAIN on login
#                 if next and next.find("logout") == -1 : #Not from Logout screen
#                     return redirect(next or url_for(homeurl))
#                 else:
#                     return redirect(url_for(homeurl))                    
#             else :
#                 flash('Authentication Failed. Please use msg-email and HRMS password')
#                 app.logger.info("Login Failed:%s" % (username))
#                 return render_template(loginTemplate, form=form)
#     else: 
#         # form.validate failed
#         flash(form.errors)
        return render_template(loginTemplate, form=form)
    # God knows what happend, cannot come here in the first place
    flash(form.errors) # Just put it here, just in case
    return render_template(loginTemplate, form=form)

@app.route('/logout/<appName>', methods=['GET'])
@app.route('/logout', methods=['GET'])
@login_required
def logout(appName = ""):
    if appName :
        if appName == "goalsheet" :
#            print("Setting Templates for AppName=" + appName)
            loginTemplate = 'goalsheet/login.html'
            homeurl = 'goalhome'
        elif appName == "bcsproj" :
            loginTemplate = 'bcsdata/login.html'
            homeurl = 'projhome'
        elif appName == 'ole' :
            loginTemplate = 'login.html'
            homeurl = 'home'
        else :
            return   render_template('message.html', message = "Application specified cannot be found.")
    else :
            loginTemplate = 'login.html'
            homeurl = 'home'
    
    current_user.is_authenticated = 0
#    current_user.save()
    username = current_user.username
#    removeLoggedInUser(username)
    logout_user()
    flash(username + ' logged out successfully.')
    return redirect(url_for(homeurl))


@app.route('/makenormal', methods=['GET'])
@login_required
def makeNormal() :
    if current_user.is_admin :
        current_user.is_admin = False
    return redirect(url_for('home'))

@app.route('/makenormal1lstlevel', methods=['GET'])
@login_required
def makenormal1lstlevel() :
    if current_user.is_admin :
        current_user.is_admin = False
        current_user.is_dclead = False
        current_user.is_Manager = True
    return redirect(url_for('home'))

@app.route('/makenormal2ndlevel', methods=['GET'])
@login_required
def makenormal2ndlevel() :
    if current_user.is_admin :
        current_user.is_admin = False
        current_user.is_dclead = True
        current_user.is_Manager = False
    return redirect(url_for('home'))
