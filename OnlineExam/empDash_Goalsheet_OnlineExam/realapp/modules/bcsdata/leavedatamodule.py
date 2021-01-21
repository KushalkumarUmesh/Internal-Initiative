# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 13:50:30 2018

@author: Srini
"""

import pandas as pd
import re
import datetime as dt

class LeaveData(object) :
    def __init__(self, Infile, fix_names = True, sheet_name = 0) :
        self.datafile = Infile
        self.df = pd.read_excel(self.datafile, sheet_name = sheet_name)
        self.emp_names = dict()
        if fix_names:
            self.fixEmpNames()
            
    def fixEmpNames(self) : # Change all values in employee Name col to have last name to 1-char
        s = self.df.Employee # Get a Series of Employees
        p = re.compile(r'([^,]+),([^,]+)')
        for name in s.index : # For each index of s, assuming it to be same as that in DF
            x = p.search(s[name]) 
            fn = (x.group(2)).strip() # First Name
            ln = (x.group(1)).strip() # Last name
            full_name = fn + " " + ln  # for a full name from first and last
 #           print("Full Name Found:"  + full_name)
            self.emp_names[full_name] = 1 # Record the legitimate name
            self.df.set_value(name, "Employee", full_name)  # Name the Employee column to full name
    
    def getLeaveHours(self, name, date, error_message): # btw this can throw an AssertionError
        year, month, date = date.split('-')
        year, month, date = int(year), int(month), int(date)
        date = dt.date(year, month, date) # let's get this as a 'datetime' datatype. Makes comparison easy.
        
        #first, we filter by Employee
        emps = self.df.loc[ self.df['Employee'] == name ]
        if emps.empty:
#            err_str = "Name: " + name + " not in Leave-names list."
#            if err_str not in error_message : error_message.append(err_str)
            return(0)
        
        #next, we look for all Approved leaves
        approved = emps.loc[emps['Status'] == 'Approved']
        if approved.empty:
#            err_str = "Name: " + name + "'s leave in not approved."
#            if err_str not in error_message : error_message.append(err_str)
            return(0)
        
        #finally, look in the date range we need
        yays = approved.loc[ ( (approved['Start.1'] <= date) &  (date <= approved['End']) ) ]
        
        #assert yays.shape[0] <= 1 # because otherwise that means we have multiple leaves for the same person on the same day.
        if yays.shape[0] > 1:
            raise ValueError("More than one approved leave for this person on this date.")
        
        if yays.empty: return(0) #no hours leave
        else:
            duration = (yays.iloc[0])['Duration']
            if duration == '0.50d' or duration == '0.5d': return(4) # half-day, so 4 hours leave
            else: return(8) # full-day leave so 8 hours

    def getAppliedLeaveHours(self, name, date, error_message): # btw this can throw an AssertionError
            year, month, date = date.split('-')
            year, month, date = int(year), int(month), int(date)
            date = dt.date(year, month, date) # let's get this as a 'datetime' datatype. Makes comparison easy.
            
            #first, we filter by Employee
            emps = self.df.loc[ self.df['Employee'] == name ]
            if emps.empty:
#                err_str = "Name: " + name + " not in Leave-names list."
#                if err_str not in error_message : error_message.append(err_str)
                return(0)
            
            #next, we look for all Approved leaves
            applied_for = emps.loc[emps['Status'] == 'Applied For']
            if applied_for.empty:
 #               err_str = "Name: " + name + "'s leave in not approved."
 #               if err_str not in error_message : error_message.append(err_str)
                return(0)
            
            #finally, look in the date range we need
            yays = applied_for.loc[ ( (applied_for['Start.1'] <= date) &  (date <= applied_for['End']) ) ]
            
            #assert yays.shape[0] <= 1 # because otherwise that means we have multiple leaves for the same person on the same day.
            if yays.shape[0] > 1:
                raise ValueError("More than one approved leave for this person on this date.")
            
            if yays.empty: return(0) #no hours leave
            else:
                duration = (yays.iloc[0])['Duration']
                if duration == '0.50d' or duration == '0.5d': return(4) # half-day, so 4 hours leave
                else: return(8) # full-day leave so 8 hours