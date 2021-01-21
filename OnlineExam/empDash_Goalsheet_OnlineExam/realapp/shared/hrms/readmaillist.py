"""
Project: HRMS Data Consistance Check

STATUS: Just started. This file is there to read available emails from an XLS-file (provided by Mukundan for BCS-Checks)
TODO:

K.Srinivas
28-Mar-2018

"""
# Import smtplib for the actual sending function
import logging

import pandas as pd
from appconfig import AppConfig

class MsgEmailList(object) :
    def __init__(self, appConf, error_message, eMailMap="") :
        if not eMailMap : #Optionally email file can be given directly
            self.eMailMap =  appConf.attribute["EmailFile"]
        else: 
            self.eMailMap = eMailMap
        self.emailDict = dict()

        print("Reading to DF from file:%s" % self.eMailMap)
        self.df = pd.read_excel(self.eMailMap) # eMailMap:XLS-file-path containing "EmployeeName" as per BCS-data and "EmailID" columns
        
        s = self.df.Name
        for n in s.index : # For each index of s, assuming it to be same as that in DF
            eName = s[n] # EmployeeName
            e = str(self.df.iloc[n]["Email"]) # email-ID
            if '@' in e:
                e = e.lower() # Convert to all lower-case
                self.emailDict[e] = e # Assign email in the map
            
            
    #get e-mail address of an Employee, based on Name as per BCS-data (last, First)
    def getEmailDict(self) :
        return (self.emailDict)
