"""
K.Srinivas, 29-Jun-2018

Project: Goal Sheet
Description: These are the domain methods for setting flags in goalsheet, goals and tasks. These flags
    will allow edit/update/delete based on the flag being true or false in the UI. The approach is as
    follows:
        a) A scheduled job will run at night and based on the date and calendar, set a bunch of flags
        b) The scheduled job will also trigger e-mails about the state-change of the goal-sheet process
        c) The global-flags, goal/task status and user-credentials will be used to derive specific flags
        d) These flags will be added to the objects being returned for rendering
        e) UI will use these flags for enabling/disabling the screen-elements
        f) Back-end controls will not be implmented at this time. 
            If needed be, these flags will need to be re-computed before saving
Primary insert-points are:
    getAllTasks  - when tasks are returned, flags will be populated
    getAllGoalsAndSections - allgoals will have flags updated 
    createTask - Can control if a task can be created or not
    assignTemplate - to control of a goal-sheet can be assigned or not 
        - prevent creating sheets for completed year
TODO: 
a) DONE-Define a list of flags at sheet, goal and task level
    goals- enable_edit, enable_submit_for_review, enable_approve, 
        enable_submit_mid_year, enable_submit_end_year,
    tasks- enable_update, enable_delete, enable_activity_edit, 
        enable_status_change
        enable_create
        enable_status_change_to_complete - REMOVED as activity-edit implies this 
    goal-sheet: enable_assignment, enable_mid_year_self,
        enable_end_year_self, enable_end_year_closure
b) Define global flags : cycle-phase : 
            start-year-tasks-definition, start-year-tasks-closing, start-year-approval-closing, 
                start-year-approval
            mid-year-about-to-start, mid-year-self-assessment, about-to-end, mid-year-review, about-to-end 
            end-year-self, end-year-1stlevel-review, end-year-2ndlevel-review
c) UPDATE global-Flags once per day at mid-night
"""
from goalmodel import *
from goaldomain import getAuthLevel, getGoalSheet
from calendardomain import getCalFlags
#Default flags based on Goal-Calender. Its an array of Dicts. Levels-0-3

#######################################################################################################
# Method to set the Modify-flags for the goal-sheet. These flags will enable or disable the functionality
# in the UI. As there are multiple factors to consider, the flags are set based on following priority
# Calendar->Status-> User. This allows a super-user to simply edit anything she/he wants to
# authLevel = 0 - Default, employee, 1- DC-lead/1st level, 2- 2nd level manager, 3- HR/Admin
#######################################################################################################
def setGoalSheetFlags(gs, allTasks, authLevel=0 ) :
    gs.enable_assignment = False
    gs.enable_self = False
    gs.enable_approve = False
    gs.enable_end_year_dc_approve = False
    gs.enable_end_year_self = False
    gs.enable_end_year_closure = False
    gs.self_all_tasks_assessment = False
    #Set Flags based on Calendar
    sheetStatus= gs.status
    flagDict = getCalFlags(authLevel, sheetStatus, year=gs.assessmentYear) 

    gs.enable_assignment = flagDict['gs_enable_assignment']
    gs.enable_self = flagDict['gs_enable_self']
    gs.enable_approve = flagDict['gs_enable_approve']

    gs.enable_end_year_self = flagDict['gs_enable_end_year_self']
    gs.enable_end_year_dc_approve = flagDict['gs_enable_end_year_dc_approve']
    gs.enable_end_year_closure = flagDict['gs_enable_end_year_closure']
    #Set Flags based on Status

    gs.phase = flagDict['phase']
    gs.actionString = flagDict['actionString']
    gs.actionId = flagDict['actionId']    

    gs.ask_feedback_enable = flagDict['ask_feedback_enable']
    gs.task_file_download_enable = flagDict['task_file_download_enable']

    gs.returned_task_exists = checkForReturnedTasks(allTasks)
    gs.minimum_tasks_exist = checkForMinimumNumberOfTasks(allTasks)
    if gs.enable_end_year_self :
        gs.self_all_tasks_assessment = checkForAllTasksNonZeroRating(allTasks) # Has self=assessent been given for ALL task? 

    if authLevel <= 2 : return # We are done unless user had some special privileges
    #Set Flags based on User

    return

def checkForReturnedTasks(allTasks) :
    for tg in allTasks.values() :# Task-list by goal
        for t in tg : # Task in each goal
            if t.completionstatus == "Returned" : return True
    return False

#Ensure ONE task PER goal
def checkForMinimumNumberOfTasks(allTasks) :
    for tg in allTasks.values() : # Task-list by goal
        if not len(tg) : return False
    return True # True only of non-zero num. of tasks in each goal

#Srini: Used in Self-Assessment phase to ensure that EVERY task is self-assessed
def checkForAllTasksNonZeroRating(allTasks) :
    for tg in allTasks.values() : # Task-list by goal
        for t in tg : # Task in each goal
            if not t.selfRating : return False # At least One task exists without self-rating
    return True


def setAllGoalsFlags(glist, authLevel=0) :
    for gl in glist : #get a set of goals for each section
        for g in gl : #get each goal with-in the section
            setGoalFlags(g, authLevel)
    return

#######################################################################################################
# Method to set the Modify-flags for the goal-display. 
#######################################################################################################
def setGoalFlags(goal,authLevel=0) :
    goal.enable_task_approve = False # Leaving this as True by default
    goal.enable_edit = False
    goal.enable_approve = False 
    gs = getGoalSheet(goal.goalSheetId)
    sheetStatus= gs.status
    goalSheetCalendarFlags = getCalFlags(authLevel, sheetStatus, year=gs.assessmentYear) 
    
    goal.enable_task_approve |= goalSheetCalendarFlags['goal_enable_task_approve']
    goal.enable_edit |= goalSheetCalendarFlags['goal_enable_edit']
    goal.enable_approve |= goalSheetCalendarFlags['goal_enable_approve']
    goal.enable_manager_approve = goal.enable_approve
    if authLevel >= 3 : return # We are done unless user had some special privileges
    #Reset/Set Flags based on Status to handle work-flow cases

    return



def setAllTasksFlags(tlist, authLevel=0) :
    for tl in tlist.values() :
        for t in tl :
            setTaskFlags(t, authLevel)
    return

def setTaskListFlags(tlist, authLevel=0) :
    for t in tlist :
#        print("setting flags for task:" + t.description)
        setTaskFlags(t, authLevel)
    return

#######################################################################################################
# Method to set the Modify-flags for the task-level buttons. 
#######################################################################################################
def setTaskFlags(task, authLevel=0) :
    task.enable_update = False # Allows a task-text and dates to be updated
    task.enable_delete = False # Allows a task to be deleted  
    task.enable_activity_edit = False # Allows the task-activity to be updated
    task.enable_status_change = False # Allows for changing the task-status to any valid value
    task.enable_manager_approve = False # Allows manager to approve/return a task with feedback

    gs = getGoalSheet(task.goalSheetId)
    sheetStatus= gs.status
    goalSheetCalendarFlags = getCalFlags(authLevel, sheetStatus, year=gs.assessmentYear) 

    #Set Flags based on Calendar
    task.enable_update = goalSheetCalendarFlags['task_enable_update']
    task.enable_delete = goalSheetCalendarFlags['task_enable_delete']
    task.enable_status_change = goalSheetCalendarFlags['task_enable_status_change']
    task.enable_manager_approve = not (task.completionstatus == "Approved" or task.completionstatus == "1stLevelReviewed")
    task.enable_activity_edit = goalSheetCalendarFlags['task_enable_activity_edit']

    task.file_upload_enable = goalSheetCalendarFlags['file_upload_enable']

        # or task.completionstatus == "Completed") #Removed as a completed task can be returned
    #Set Flags based on Status and User
    if authLevel >= 3 : 
        task.enable_manager_approve = True
        return # He/She wins, status does not matter

    if authLevel >= 1: # Emp. and DC-Lead are not allowed to change completed items
        if  (task.completionstatus == "Completed") :
            task.enable_status_change = False
            task.enable_update = False
            task.enable_delete = False
            task.enable_activity_edit = False # Completed activity cannot be updated
        return

    if authLevel == 0: # Emp. not allowed to change an approved items
        if  (task.completionstatus == "Completed") :
            task.enable_status_change = False
            task.enable_update = False
            task.enable_delete = False
            task.enable_activity_edit = False # Completed activity cannot be updated

        if  (task.completionstatus == "Approved" or task.completionstatus == "1stLevelReviewed") :
            task.enable_status_change = False
            task.enable_update = False
            task.enable_delete = False
#            print("task-delete set to false")
    return
