"""
K.Srinivas, 27-Mar-2018

Project: Online Exam
Description: These are the methods for interfacing with the notification REST APIs. 

TODO: getGroupSelectionList needs to be tested
TODO: Define the upload directory!! It is working fine..but I don't know where the uploaded files go
KNOWN BUGs:
This needs to be called to avoid running out of network ports  myResponse.connection.close()
FIX needs to be tested!! - 26-Jul-2018
"""
import requests
from requests.auth import HTTPBasicAuth
import json
import string
from readmaillist import MsgEmailList

#Define your URLs here, Ideally, the 1st one should go in __init__.py in realapp directory
notificationUrl = 'http://10.144.0.21:1111/'
getGroupurl = notificationUrl + 'admin/groups'
getEmailsInGroupurl = notificationUrl + 'admin/getAllEmailsInAGroup/'
sendEmailsToGroupurl = notificationUrl + 'send-email/group'
sendEmailUrl = notificationUrl + 'send-email'
getTemplatesUrl = notificationUrl + 'admin/templates'
delGroupUrl = notificationUrl + 'admin/deleteGroup'
delEmailsUrl = notificationUrl + 'admin/deleteAEmailFromAGroup'
createGroupUrl = notificationUrl + 'admin/groups' # Same as getGroupUrl but we need to use POST
addEmailUrl = notificationUrl + 'admin/addEmailsToGroup'

#Works
def addEmailsFromFile(fname, id) :
    eObj = MsgEmailList("", [], fname) 
    emailDict = eObj.getEmailDict()

    #Ensure that duplicates are not added
    existingList = getEmailsInGroup(id) # Get existing e-mails
    for e in existingList :
        if e in emailDict.keys() :
            del emailDict[e] # Delete it
    if not emailDict : # If its empty
        return("No new e-mails found in the uploaded file" )

    elist = [ "\"" + e.strip().lower() + "\""  for e in emailDict.keys()] # Add double qoutes around each email
    eStr = ""
    n = len(elist)
    for i in range(n) :
        e = elist[i]
        eStr += e
        if (i+1) < n :
            eStr += ","

    jStr = '{ \"emailIds\": [ %s ], \"groupId\": \"%s\" }' % (eStr, str(id))
    #print('JSON=' + jStr)
    headers = {'content-type': 'application/json'}
    try :
        myResponse = requests.post(addEmailUrl, data=jStr, headers=headers)
    except :
        return("Due to an internal error, it is possible that e-mails could not added to the group. Please check the list and retry later." )        
    if(myResponse.ok):
        return("Added emails :%s" % (eStr) )
    
#    print (addEmailUrl + " gave return code:"  + str(myResponse.status_code))
    return (addEmailUrl + " gave return code:"  + str(myResponse.status_code))

#Add only one e-mail
def addEmailToGroup(email, id) :
    existingList = getEmailsInGroup(id)
    if email in existingList : # Email already exists
        return ("Email (%s) is already in the group" % (email))

    eStr = "\"" + email.strip().lower() +  "\""
    jStr = '{ \"emailIds\": [ %s ], \"groupId\": \"%s\" }' % (eStr, str(id))

    headers = {'content-type': 'application/json'}
    try :
        myResponse = requests.post(addEmailUrl, data=jStr, headers=headers)
    except :
        return("Due to an internal error, it is possible that e-mails could not added to the group. Please check the list and retry later." )        

    if(myResponse.ok):
        return("Added emails :%s" % (eStr) )
#    print (addEmailUrl + " gave return code:"  + str(myResponse.status_code))
    return (addEmailUrl + " gave return code:"  + str(myResponse.status_code))

def createGroup(name, desc) :
    headers = {'content-type': 'application/json'}

    obj = '{ "description":"%s" , "groupName": "%s" }' % (desc, name)
    print('JSON=' + obj)
    try :
        myResponse = requests.post(createGroupUrl, data=obj, headers=headers)
    except :
        return("Due to an internal error, it is possible that group is not created. Please check the list and retry later." )        

    if(myResponse.ok):
        return("Group with Name:%s Created with ID:%s" % (name, str(myResponse.text)) )
    return (createGroupUrl + " gave return code:"  + str(myResponse.status_code))

#Testing Complete
def deleteGroup(id) :
    headers = {'content-type': 'application/json'}
    obj = '{ \"groupId\": \"%s\" }' % (str(id))
    try :
        myResponse = requests.delete(delGroupUrl, data=obj, headers=headers )
    except :
        return("Due to an internal error, it is possible that group is not deleted. Please check the list and retry later." )        

    if(myResponse.ok):
        return("Group with ID:%s deleted" % (str(id)) )
    return (delGroupUrl + " gave return code:"  + str(myResponse.status_code))

def deleteEmail(id, emails) :
    headers = {'content-type': 'application/json'}
    obj = '{ \"emailIds\": [ \"%s\" ], \"groupId\": \"%s\" }' % (emails, str(id))

    try :
        myResponse = requests.delete(delGroupUrl, data=obj, headers=headers )
    except :
        return("Due to an internal error, it is possible that the email is not deleted. Please check the list and retry later." )        

    if(myResponse.ok):
        return("Mails :%s deleted" % (str(emails)) )
    return (delEmailsUrl + " gave return code:"  + str(myResponse.status_code))
    
def getGroups() :
    try :
        myResponse = requests.get(getGroupurl)
    except :
        return {}       
    if(myResponse.ok):
        jData = json.loads(myResponse.content)
    else :
        jData = {}
    #print(jData)
    return jData 

def getGroupName(id) :
    jData = getGroups()
    for item in jData :
#        print(str(id) + ":" + str(item['groupId']) + ":" + item['groupName'])
        if str(item['groupId']) == str(id) :
            return item['groupName']
    return False

def getGroupId(groupName) :
    jData = getGroups()
    for item in jData :
#        print(str(id) + ":" + str(item['groupId']) + ":" + item['groupName'])
        if str(item['groupName']) == str(groupName) :
            return item['groupId']
    return False
    
def getGroupSelectionList() :
#Fake it for testing
#    emaiList = [("1","group1"), ("4","group4"),("2","group2"),("3","group3"),]
#    return sorted(emaiList, key=get2nd)
    return sorted(getList(getGroupurl,'groupId','groupName' ), key=get2nd)
#Used above for sorted
def get2nd(elem) :
    return elem[1].lower()

#Return a list of e-mails in a group. Used for listing e-mails page
def getEmailsInGroup(id) :
    emaiList = []
#    print("came in...") 
    try :
        myResponse = requests.get(getEmailsInGroupurl + str(id))
        if(myResponse.ok):
            jData = json.loads(myResponse.content)
            emaiList = jData['emailIds']
            groupId = jData['groupId']
#            print("emails=%s" % (str(emaiList)) )
        else :
            emaiList = []
#            print("Not-OK Response") 
        return emaiList
    except :
#        print("Exception Response") 
        return emaiList
#    print("Cannot come here Response") 
    return emaiList

def notify(to, subject, body, fromemail="hrms-notify@msg-global.com",  \
    field1="", field2="", field3="", field4="", field5="", header="", templateId="-1") :
    obj = {
            "body": body,
            "field1": field1,
            "field2": field2,
            "field3": field3,
            "field4": field4,
            "field5":field5 ,
            "from": fromemail,
            "header": header,
            "subject": subject,
            "templateId": templateId,
            "to": to
            }
    try :
        myResponse = notifyPost(sendEmailUrl, obj)
        if(myResponse.ok):
            myResponse.connection.close()
            return True
        else :
            #Need to implement Logging
            print ("Notify Failed:" + str(myResponse.content))
            myResponse.connection.close()
            return False
    except:
        print ("Notify Exception caught")
#        myResponse.connection.close()
        return False
    myResponse.connection.close() # Paranoia?
    return False

#6-Sep:Srinivas: Changed the "id" to "groupName" as no one is using it so far.        
def notifyGroup(groupName, subject, body, fromemail = "onlineexam@msg-global.com" , templateId="-1") :
    id = getGroupId(groupName)
    #print("Sending to ID:" + str(id))
    obj =  {
            "body": body,
            "from": fromemail,
            "groupId": id,
            "subject": subject,
            "templateId": templateId
            }
    try :
        myResponse = notifyPost(sendEmailsToGroupurl, obj)
        if(myResponse.ok):
            return True
        else :
            #Need to implement Logging
            print ("Nofiy Group Failed:" + str(myResponse.content))
            return False
    except:
        print ("Notify Exception caught")
        return False
    return False

def notifyPost(url, obj) :
    headers = {'content-type': 'application/json'}
    return requests.post(url, data=json.dumps(obj), headers=headers)

def notifyGet(url) :
    return requests.get(getGroupurl)

#Generic Key/value pair list from Url, returned as a list of key-values, useful in select-function
def getList(url, key, value, value1= None ) :
    retList = []
    myResponse = requests.get(url)
    if(myResponse.ok):
        jData = json.loads(myResponse.content)
        if value1 == None:
            for j in jData :
                retList += [(j[key], j[value])]
        else :
            for j in jData :
                retList += [(j[key], j[value],j[value1] )]
    return retList
