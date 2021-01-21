#For Checking authorization from HRMS
import requests
from flask_login.mixins import UserMixin
from candidateinterface import *
from requests.auth import HTTPBasicAuth
import json
import logging
from realapp import app
from hrmsdomain import is_DCLead, is_Manager
import os

#hrmsAuthUrl = 'http://10.144.0.21:8091/api/jsonws/user/get-user-by-email-address/company-id/10155/email-address/'
hrmsSSLAuthUrl = 'https://10.144.0.21:8443/api/jsonws/user/get-user-by-email-address/company-id/10155/email-address/'


class LoggedInUser(UserMixin) :
    username = "" # We are using e-mail ID as username, but leaving this OPEN for using ANYTHING
    is_authenticated = False

    is_active = True
    is_admin = False
    is_anonymous = False
    is_dclead = False
    is_Manager = False
    numTries = 0 # Number of login attempts

    def get_id(self) :
        return(self.username )


logged_in_users = {} # Username who are either logged in or tried, is the hash, user-Object

def getLoggedInUser(emailid) :
    if emailid in logged_in_users.keys() : # Object was there
        return logged_in_users[emailid] # Return the user object
    return None

#On Logout, email needs to be removed from logged_in_users hash
def removeLoggedInUser(emailid) :
    logged_in_users.pop(emailid, None) # Remove the logged-in user
    return None


# Generic high-level method, should return LoggedInUser Object
# Multiple authentication mechanisms can be used here
def checklogin(emailid, password) : 
    return authHRMSEmployee(emailid, password )
    return alwaysSucceedSpecial(emailid, password )
    return alwaysSucceed(emailid, password )

#TO BE TESTED in OFFICE, cannot be tested from home
def authHRMSEmployee(emailid, password) : # Returns the logged-in User Object using HRMS authentication and locat DB
    lu = LoggedInUser()  # Create an empty user-object
    lu.numTries += 1 # Bump-up the number of attempts (currently NOT IMPLEMENTED, but puttin it in there for max-retries)
    lu.username = emailid  # Create a default object to return
    lu.is_dclead = False
    lu.is_Manager = False
    lu.is_admin = False

#    url = hrmsAuthUrl +emailid
#    myResponse = requests.get(url, auth=HTTPBasicAuth(emailid,password))
    url = hrmsSSLAuthUrl +emailid
    myResponse = requests.get(url, auth=HTTPBasicAuth(emailid,password), verify=True)

    if(myResponse.ok):
        jData = json.loads(myResponse.content)
        if "greeting" in jData.keys() :
            lu.is_authenticated = True
            if is_DCLead(emailid) :
                lu.is_dclead = True
            if is_Manager(emailid) :
                lu.is_Manager = True
    # Check local DB if this person has any special previledges
    myResponse.connection.close()
    user = User.query.filter_by(username=emailid).first()
    if user:
        lu.is_admin = user.is_admin

    #Add to our list before returning the object
    logged_in_users[emailid] = lu # Add lu to the list of users who are logged in
    return lu

#TO BE TESTED in OFFICE, cannot be tested from home
def impersonateEmployee(emailid, lu) : # Returns the logged-in User Object using HRMS authentication and locat DB
    lu.username = emailid  # Create a default object to return
#    url = hrmsAuthUrl +emailid
#    myResponse = requests.get(url, auth=HTTPBasicAuth(emailid,password))
    lu.is_dclead = False
    lu.is_Manager = False
    lu.is_admin = False
    
    if is_DCLead(emailid) :
        lu.is_dclead = True
    if is_Manager(emailid) :
        lu.is_Manager = True
    # Check local DB if this person has any special previledges
    user = User.query.filter_by(username=emailid).first()
    if user:
        lu.is_admin = user.is_admin

    #Add to our list before returning the object
    logged_in_users[emailid] = lu # Add lu to the list of users who are logged in
    return lu


# This will alway login the user without checking the password, uses the local DB for admin
# Used for testing purposes only
def alwaysSucceed(emailid, password ) : 
    #Ensure that this does NOT execute on PROD
    if os.path.isfile('E:/onlineexam/thisisprod.txt') :
        return authHRMSEmployee(emailid, password)
    
    lu = LoggedInUser()  # Create an empty user-object
    lu.username = emailid  # Create a default object to return
    lu.is_authenticated = True
    lu.is_dclead = True

    # Check local DB if this person has any special previledges
    user = User.query.filter_by(username=emailid).first()
    if user:
        lu.is_admin = user.is_admin

    #Add to our list before returning the object
    logged_in_users[emailid] = lu # Add lu to the list of users who are logged in
    return lu

# This will alway login the user without checking the password, uses the local DB for admin
# Used for testing purposes only

def alwaysSucceedSpecial(emailid, password ) : 
    #Ensure that this does NOT execute on PROD
    if os.path.isfile('E:/onlineexam/thisisprod.txt') :
        return authHRMSEmployee(emailid, password)

    lu = LoggedInUser()  # Create an empty user-object
    lu.numTries += 1 # Bump-up the number of attempts (currently NOT IMPLEMENTED, but puttin it in there for max-retries)
    lu.username = emailid  # Create a default object to return
    lu.is_dclead = False
    lu.is_Manager = False
    lu.is_admin = False

    lu.is_authenticated = True
    if is_DCLead(emailid) :
        lu.is_dclead = True
    if is_Manager(emailid) :
        lu.is_Manager = True
    # Check local DB if this person has any special previledges
    user = User.query.filter_by(username=emailid).first()
    if user:
        lu.is_admin = user.is_admin

    #Add to our list before returning the object
    logged_in_users[emailid] = lu # Add lu to the list of users who are logged in
    return lu
