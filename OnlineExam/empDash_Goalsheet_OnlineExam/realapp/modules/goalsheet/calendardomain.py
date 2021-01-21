"""
K.Srinivas, 3-Jul-2018

Project: Goal Sheet
Description: These are the domain methods for the Calendar module of the Goal Sheet module. 

TODO: 
a) DroPPED- Move the number of levels to a config-file
KNOWN BUGs: None
"""
import logging
import datetime as dt
from hrmsdomain import *
from goalmodel import *
from readmaillist import MsgEmailList
from emailstrings import *
from realapp import db, cache
from calendarmodel import GoalCalendar
from notification import notify
######################################################################################
# New concept implementation.
# Flags depend on: the Sheet-Status, Auth-level and Phase-type. A unique row needs
# to exist as a combination of these. The flags obtain from DB are further adjusted
# Based on goal/task status at individual levels
# 23-Dec-2018: Changes:
# a) Added the "PERFORM" phase as a default BASE phase i.e. its always active. and is used
# Only if no other phase is active. Phase-number ZERO is reserved for this one.
# b) SuperUser NOW is part of the CODE and not an AUTH level. ALL flags are set to TRUE and the
# DB-Data is never consulted. This was done to reduce clutter in the DB and there is not reason
# to set any flag to FALSE for the super user
@cache.memoize()
def getCalFlags(authLevel, sheetStatus, year, todayDate=None) :
    flagDict = dict() 
    defaultFlag = False
    if authLevel == 10 :
        defaultFlag = True
    flagDict['gs_enable_assignment'] = defaultFlag
    flagDict['gs_enable_self'] = defaultFlag
    flagDict['gs_enable_approve'] = defaultFlag
    flagDict['gs_enable_end_year_self'] = defaultFlag
    flagDict['gs_enable_end_year_dc_approve'] = defaultFlag
    flagDict['gs_enable_end_year_closure'] = defaultFlag
    flagDict['goal_enable_task_approve'] = defaultFlag
    flagDict['goal_enable_edit'] = defaultFlag
    flagDict['goal_enable_approve'] = defaultFlag
    flagDict['task_enable_update'] = defaultFlag
    flagDict['task_enable_delete'] = defaultFlag
    flagDict['task_enable_activity_edit'] = defaultFlag
    flagDict['task_enable_status_change'] = defaultFlag
    flagDict['task_file_download_enable'] = defaultFlag
    flagDict['file_upload_enable'] = defaultFlag
    flagDict['ask_feedback_enable'] = defaultFlag

    flagDict['phase'] = "Inactive Phase "
    flagDict['actionString'] = "No Action"
    flagDict['actionId'] = 0

    #20-Dec-2018: Cal table is getting too big, remove super-user entries, they are all true anyway
    #Lets ensure that we add any new flags ABOVE THIS LINE
    if authLevel == 10 : return flagDict

    #For Scanning and error-checking the calendar
    if not todayDate:
        todayDate = dt.datetime.today()

    calList = GoalCalendar.query.filter_by(assessmentYear=year). \
        filter_by(authlevel=authLevel).filter_by(sheetStatus=sheetStatus). \
        filter( todayDate >= GoalCalendar.dateStart, todayDate <= GoalCalendar.dateEnd). \
        all()
    
    calFinal = None
   # print('--------------Kush:test----------')
    calCount = len(calList)
   # print(calCount)
   # print('--------------Kush:test----------')
   # print(calList)

    #SRINI: Logic has been changed to create a "default phase" where there is nothing "special"
    #This is available through out the year IF not other phase is active. This logic avoids nuisence
    #As we extend phases for reviews, etc. Currently defined ONLY for Approved-status
    if calCount > 2:
        mesgStr = "Too many Phases found for:" + str(todayDate) + ":" + str(sheetStatus) + ":" + str(authLevel)
        print(mesgStr)
#        notify('srinivas.kambhampati@msg-global.com', "FATAL ERROR:GoalSHEET CALENDER",mesgStr )
        return flagDict

    if calCount == 1 : # Only Perform phase can be there, but we really don't care as long as there is only ONE
        calFinal = calList[0]

    elif calCount == 2 : # calCount == 2, take the one where phaseType is NOT zero, ZERO reserved for PERFORM phase
        if calList[0].phaseType :
            calFinal = calList[0]
        else : 
            calFinal = calList[1]
    elif calCount == 0 :
        print("No Valid Phase found for:" + str(todayDate) + ":" + str(sheetStatus) + ":" + str(authLevel))
        return flagDict
    else : # We really cannot come here, leave it from past code just to be safe.
        mesgStr = "THIS CANNOT HAPPEN: Too many Phases found for:" + str(todayDate) + ":" + str(sheetStatus) + ":" + str(authLevel)
        print(mesgStr)
#        notify('srinivas.kambhampati@msg-global.com', "FATAL ERROR:GoalSHEET CALENDER",mesgStr )
        return flagDict

        
    flagDict['phase'] = calFinal.phase
    flagDict['actionString'] = calFinal.actionString
    flagDict['actionId'] = calFinal.actionId
        
    flagDict['gs_enable_assignment'] = calFinal.gs_enable_assignment

    flagDict['gs_enable_self'] = calFinal.gs_enable_self
    flagDict['gs_enable_approve'] = calFinal.gs_enable_approve
    flagDict['gs_enable_end_year_self'] = calFinal.gs_enable_end_year_self
    flagDict['gs_enable_end_year_dc_approve'] = calFinal.gs_enable_end_year_dc_approve
    flagDict['gs_enable_end_year_closure'] = calFinal.gs_enable_end_year_closure

    flagDict['goal_enable_task_approve'] = calFinal.goal_enable_task_approve
    flagDict['goal_enable_edit'] = calFinal.goal_enable_edit
    flagDict['goal_enable_approve'] = calFinal.goal_enable_approve

    flagDict['task_enable_update'] = calFinal.task_enable_update
    flagDict['task_enable_delete'] = calFinal.task_enable_delete
    flagDict['task_enable_activity_edit'] = calFinal.task_enable_activity_edit
    flagDict['task_enable_status_change'] = calFinal.task_enable_status_change
    flagDict['file_upload_enable'] = calFinal.file_upload_enable
    flagDict['task_file_download_enable'] = calFinal.task_file_download_enable
    flagDict['ask_feedback_enable'] = calFinal.ask_feedback_enable

    return flagDict

# Old jungle saying Hardcoding is ok, as long as everything is in one place :-)
# method to return a STRING YYYY-MM-DD for start and end of an assessment year
# This is required for because 2018-2019 had a different start and end dates
# Going forward its calendar year. By hard-coding it here, its in one place
# and if the extremely unlikely event that it changes again, we only need to change it here
# Caching makes the over-head minimal
@cache.memoize()
def getAssessmentYearStart(year) : #Year='2019'
    if '2018' in year : # its 2018-2019
        return "2018-04-01"
    return year + "-01-01"

@cache.memoize()
def getAssessmentYearEnd(year) :
    if '2018' in year : # its 2018-2019
        return "2019-03-31"
    return year + "-12-31"

########################################################################################3
#This is only for Creating a default CAL-DB data (till we have a UI)
def createDefaultCalendar() :
    #Phases and states as Agreed with Ashish on 27-Dec-2018
    phases = ('GoalSetting','TermReview','EndTermAssessment','Perform','Closed' )
    sheetStates = dict()
    sheetStates['GoalSetting'] = ['Assigned','Pending1stApproval','Pending2ndApproval','Returned']
    sheetStates['Perform'] = ['Approved','Reviewed']
    sheetStates['Review'] = ['Approved','Pending1stReview','Pending2ndReview','Reviewed']
    sheetStates['Assessment'] = ['Approved','Reviewed','Pending-1st Level','Pending-2nd Level', \
                                'Pending-MGMT','Completed', 'Closed']
#    sheetStates['Closed'] = ['Completed'] 

    #Goal Setting Phase is available at ANY TIME from START of the year till end of 11th Month
    for authLevel in (0,1,2,3) : #Super user flags are now hard-coded for convenience
        for sheetStatusEntry in sheetStates['GoalSetting'] :
            c = GoalCalendar()
            c.phase="Goal Setting"
            c.phaseType = 1
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Define Tasks/Get Mgr Approval"
            c.description="Set Goals:'Assigned','Pending1stApproval','Pending2ndApproval','Returned'"
            c.dateStart='2019-01-01'
            c.dateEnd='2019-11-30'
            c.authlevel = authLevel
            c.assessmentYear='2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()

    #Review Phase
    #TODO: Cron to swtich to Approved phase at the end of Review Phase
    for authLevel in (0,1,2,3) : #Super user flags are now hard-coded for convenience
        for sheetStatusEntry in sheetStates['Review'] :
            c = GoalCalendar()
            c.phase="MidYearReview"
            c.phaseType = 2
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Enter comments/Obtain Feedback"
            c.description="Get Feedback:'Approved','Pending1stReview','Pending2ndReview','Reviewed'"
            c.dateStart='2019-06-01' 
            c.dateEnd='2019-06-30' #One month for Review
            c.authlevel = authLevel
            c.assessmentYear='2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()

    #Assessment Phase
    for authLevel in (0,1,2,3) : #Super user flags are now hard-coded for convenience
        for sheetStatusEntry in sheetStates['Assessment'] :
            c = GoalCalendar()
            c.phase="Assessment"
            c.phaseType = 3
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Perform Assessment"
            c.description="Employee Assessment and ratings"
            c.dateStart='2020-01-01' 
            c.dateEnd='2020-02-28' #Two months for Review
            c.authlevel = authLevel
            c.assessmentYear='2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()


    #Assessment Phase FOR 2018-2019
    for authLevel in (0,1,2,3) : #Super user flags are now hard-coded for convenience
        for sheetStatusEntry in sheetStates['Assessment'] :
            c = GoalCalendar()
            c.phase="Assessment"
            c.phaseType = 3
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Perform Assessment"
            c.description="Employee Assessment and ratings"
            c.dateStart='2019-01-01' 
            c.dateEnd='2019-02-28' #Two months for Review
            c.authlevel = authLevel
            c.assessmentYear='2018-2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()

    #Perform Phase - Default phase Lets make it automatic i.e. Use PhaseType Zero if nothing else is found
    #So,there is never an "inactive phase", unless the goal-sheet is in a funky state
    for authLevel in (0,1,2,3) : 
        for sheetStatusEntry in sheetStates['Perform'] :
            c = GoalCalendar()
            c.phase="Perform"
            c.phaseType = 0
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Perform Tasks and update"
            c.description="Employee performs the tasks as per goal-sheet and updates the activities"
            c.dateStart='2019-01-01' #Entire Year, Approved sheets can be acted on 
            c.dateEnd='2019-12-31' 
            c.authlevel = authLevel
            c.assessmentYear='2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()

    #Perform Phase - for 2018-19, last 4-5 days!!
    for authLevel in (0,1,2,3) : 
        for sheetStatusEntry in sheetStates['Perform'] :
            c = GoalCalendar()
            c.phase="Perform"
            c.phaseType = 0
            c.sheetStatus = sheetStatusEntry
            c.actionString = "Perform Tasks and update"
            c.description="Employee performs the tasks as per goal-sheet and updates the activities"
            c.dateStart='2018-12-01' #Entire Year, only 3-4 days left :-) 
            c.dateEnd='2018-12-31' 
            c.authlevel = authLevel
            c.assessmentYear='2018-2019'
            setDefaultFlags(c)
            db.session.add(c)
    db.session.commit()

    return


def setDefaultFlags(c) : #authLevel, phaseType are already in c
    #Create flagDict 
    # flagDict['gs_enable_assignment'] = calFinal.gs_enable_assignment

    # flagDict['gs_enable_self'] = calFinal.gs_enable_self
    # flagDict['gs_enable_approve'] = calFinal.gs_enable_approve
    # flagDict['gs_enable_end_year_self'] = calFinal.gs_enable_end_year_self
    # flagDict['gs_enable_end_year_dc_approve'] = calFinal.gs_enable_end_year_dc_approve
    # flagDict['gs_enable_end_year_closure'] = calFinal.gs_enable_end_year_closure

    # flagDict['goal_enable_task_approve'] = calFinal.goal_enable_task_approve
    # flagDict['goal_enable_edit'] = calFinal.goal_enable_edit
    # flagDict['goal_enable_approve'] = calFinal.goal_enable_approve

    # flagDict['task_enable_update'] = calFinal.task_enable_update
    # flagDict['task_enable_delete'] = calFinal.task_enable_delete
    # flagDict['task_enable_activity_edit'] = calFinal.task_enable_activity_edit
    # flagDict['task_enable_status_change'] = calFinal.task_enable_status_change
    pass
    return



