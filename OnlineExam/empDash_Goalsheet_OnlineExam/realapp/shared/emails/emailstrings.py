"""
K.Srinivas, 7-Apr-2018

Project: Multiple (starting with OnlineExam, Goalsheet)
Description: Store constants for sending e-mail notifications in all modules

TODO: Clean-up the import list

KNOWN BUGs: None
"""

htmlhead = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns:th="http://www.thymeleaf.org" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <!-- <title>Sending Email with Thymeleaf HTML Template Example</title> -->

    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>

    <link href='http://fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type='text/css'/>

    <!-- use the font -->
    <style>
         body {
            font-family: 'Roboto', sans-serif;
            font-size: 12px;
        }
    </style>
    </head>
    <body style="margin: 0; padding: 0;">
    """
htmlfooter = "</body></html>"
hrmsfooter ="""<h4  style=\"margin-bottom:0px;\">Instructions:</h4>
<p  style=\"margin:0px;\">a) Please use Chrome or Firefox browser only and access HRMS at: http://10.144.0.21:8091</P>
<P  style=\"margin:0px;\">b) HRMS PASSWORD: You can reset the password by clicking on 'Forgot Password' at: http://10.144.0.21:8091 </P>
<P  style=\"margin:0px;\">c) HRMS SUPPORT: Bishwajeet.Mandal@msg-global.com and Mayur.Mohan@msg-global.com can address data-related concerns.</P>
<P  style=\"margin:0px;\">d) Documents uploaded should be less than 2MB in size.</P>
<P  style=\"margin:0px;\">e) Address updated should be "Home" (current residence) and "Permanent". Please ADD Row and then submit.</P>
<P  style=\"margin:0px;\">f) Note that some fields can only be modified by our HR team. Please contact them if required.</P><P>
<P  style=\"margin:0px;\">g) APPLICATION SUPPORT: If issues with the application itself (e.g. cannot access URL), please contact SandeshGadabanahalli.Suresh@msg-global.com</P><P>
    """
hrmsdatacheck ="""<p>Please verify, and update if required, your data in HRMS. Please pay special attention to items in <b style=\"color:red;\">RED</b>.
    Instructions are provided below to help you get started.</P><P>"""

olefooter ="""<h4  style=\"margin-bottom:0px;\">Instructions:</h4>
<p  style=\"margin:0px;\">a) Please use Chrome or Firefox browser only and access OLE at: http://10.144.0.21:5000</P>
<P  style=\"margin:0px;\">b) HRMS PASSWORD: You can reset the password by clicking on 'Forgot Password' at: http://10.144.0.21:8091 </P>
<P  style=\"margin:0px;\">c) HRMS-SUPPORT: Bishwajeet.Mandal@msg-global.com and Mayur.Mohan@msg-global.com can help you.</P>
<P  style=\"margin:0px;\">d) Please ensure that you do not logout or close the window once the exam has started.</P>
<P  style=\"margin:0px;\">e) Once the question-set is displayed on the screen, it cannot be displayed again.</P>
<P  style=\"margin:0px;\">f) Your test results may be provided to your Manager/DC-Lead/Trainer.</P><P>
    """


oleassign = """
Dear Employee,
<p>As part of your development program, an online test,titled \"%s\", has been assigned to you.</p>


<p>Window for your Assessment is, <b>from %s to %s</b>. Please ensure that you complete your assessment before the due-date.
Good Luck!!</p>

<p>All tests assigned to you are available OLE, please see instructions below. </p>
<p>Please click <a href='http://10.144.0.21:5000/exam/startexam/%s'>here</a> start now!!</p>

<p>Best Regards,</p>
<p>Team msg global</p>
    """

oleassignNoDueDate = """
Dear Employee,
<p>As part of your development program, an online test,titled \"%s\", has been assigned to you.</p>

<p>There is no specific due-date. Please ensure that you complete your assessment in a timely manner.
Good Luck!!</p>

<p>All tests assigned to you are available OLE, please see instructions below. </p>
<p>Please click <a href='http://10.144.0.21:5000/startexam/%s'>here</a> start now!!</p>

<p>Best Regards,</p>
<p>Team msg global</p>
    """

assignemailNoDueDate = htmlhead + oleassignNoDueDate + olefooter + htmlfooter
assignemail = htmlhead + oleassign + olefooter + htmlfooter

goalsheetFooter = """<h4  style=\"margin-bottom:0px;\">Instructions:</h4>
<p  style=\"margin:0px;\">a) Please use Chrome or Firefox browser only and access GoalSheet at: http://10.144.0.21:5000/goals</P>
<P  style=\"margin:0px;\">b) HRMS PASSWORD: You can reset the password by clicking on 'Forgot Password' at: http://10.144.0.21:8091 </P>
<p  style=\"margin:0px;\">c) Following strict timeline is critical for our success. Application behavior changes based on date and Goalsheet Status!!</P>
<P  style=\"margin:0px;\">d) Its your responsibility to ensure that the goal sheet is in 'Approved' Status. Request your Manager/DC Lead to approve the Goalsheet ASAP.</P>
<P  style=\"margin:0px;\">e) For any questions please contact Ashish.Sharma@msg-global.com or Ben.Jonathan.Pottipadu@msg-global.com.</P>
<P  style=\"margin:0px;\">f) HRMS-SUPPORT: Bishwajeet.Mandal@msg-global.com and Mayur.Mohan@msg-global.com can help you with HRMS data-related concerns.</P>
<P  style=\"margin:0px;\">g) APPLICATION SUPPORT: If issues with the application itself (e.g. cannot access URL), please contact kushalkumar.Umesh@msg-global.com</P><P>
    """

goalsheetFooterDC = """<h4  style=\"margin-bottom:0px;\">Instructions:</h4>
<P  style=\"margin:0px;\">a) Please ensure to act on the Goalsheet before the deadline.</P>
<p  style=\"margin:0px;\">b) Application behavior changes based on (today's)date and Goalsheet Status!! Following the process is part of your performance.</P>
<p  style=\"margin:0px;\">c) Please use Chrome or Firefox browser only and access GoalSheet at: http://10.144.0.21:5000/goals</P>
<P  style=\"margin:0px;\">d) HRMS PASSWORD: You can reset the password by clicking on 'Forgot Password' at: http://10.144.0.21:8091 </P>
<P  style=\"margin:0px;\">e) Goalsheet once approved by you(DC_Lead) cannot be altered or changed.</P>
<P  style=\"margin:0px;\">g) For any questions please contact Ashish.Sharma@msg-global.com or Ben.Jonathan.Pottipadu@msg-global.com.</P>
<P  style=\"margin:0px;\">h) HRMS-SUPPORT: Bishwajeet.Mandal@msg-global.com and Mayur.Mohan@msg-global.com can help you with HRMS data-related concerns.</P>
<P  style=\"margin:0px;\">g) APPLICATION SUPPORT: If issues with the goalsheet-app itself (e.g. cannot access URL), please contact kushalkumar.Umesh@msg-global.com</P><P>
    """

goalsheetAssigned = """Dear Employee,
<p>As part of your performance management, you have been assigned your goals for the Assessment Year %s.
Please follow the instructions below and <b>add the tasks to goals</b> assigned to you.</p>
<p>Once satisfied, please submit the Goalsheet for Manager approval.</p>
    """

goalsheetAssignedDC = """Dear Manager,
<p>Goals have been assigned to your reportee %s</p>
    """

goalsheetPendingApproval = """Dear Employee,
<p>Your Goalsheet has been sent to %s for approval</p>
    """

goalsheetPendingApprovalDC = """Dear Manager,
<p>Your Team Member, %s, has Re/submitted the Goalsheet. Please review and approve/return the Goalsheet at the earliest.</p>
    """

goalsheetReturned = """Dear Employee,
<p>Your Goalsheet has been returned to you for changes/corrections by your DC_lead/Country Manager.Please make the changes and re-submit in a timely manner.</p>
<p>Comments given were:%s</p>
    """

goalsheetReturnedDC = """Dear Manager,
<p>You have returned the Goalsheet for %s.</p>
<p>Comments given were:%s</p>
    """

goalsheetApproved = """Dear Employee,
<p>Your Goalsheet has been approved by your DC_lead/Country Manager.</p>
<p>Please update the Goalsheet as soon as you complete your tasks.</p>
<p>Comments given were:%s</p>
    """

goalsheetApprovedDC = """Dear Manager,
<p>You have Goalsheet for %s.</p>
<p>Comments given were:%s</p>
    """


goalAssign = htmlhead + goalsheetAssigned + goalsheetFooter + htmlfooter
goalAssignDC = htmlhead + goalsheetAssignedDC + goalsheetFooterDC + htmlfooter

goalPendingApproval = htmlhead + goalsheetPendingApproval + goalsheetFooter + htmlfooter
goalPendingApprovalDC = htmlhead + goalsheetPendingApprovalDC + goalsheetFooterDC + htmlfooter

goalApproved = htmlhead + goalsheetApproved + goalsheetFooter + htmlfooter
goalApprovedDC = htmlhead + goalsheetApprovedDC + goalsheetFooterDC + htmlfooter

goalReturned = htmlhead + goalsheetReturned + goalsheetFooter + htmlfooter
goalReturnedDC = htmlhead + goalsheetReturnedDC + goalsheetFooterDC + htmlfooter

goalEmailSubject = "Action Required: Goalsheet Update"

###############################################################################################
# HRMS JOB Notifications
###############################################################################################
bdaySubject = "Happy Birthday!!"
bdayBody = "Happy Birthday!! From HRMS-team, we wish you Many Happy Returns of the day."
aniversarySubject = "Today is your work aniversary!"
aniversaryBody = "Congratulations on your work anniversary. We wish you a wonderful career at msg Global"
bdayManagerSubject = "Wish your reportee(s)."
bdayManagerBody = "One or more of your reportees has a Birthday today:"
aniverasaryManagerSubject = "Your reportee(s) DOJ today."
aniverasaryManagerBody = "One or more of your reportees has a Work Aniversary today:"


###############################################################################################
# Goal-Sheet Feedback JOB Notifications
###############################################################################################
feedbackSubject = "Goal/Task Feedback has been given"
feedbackSubjectMgr = "Goal/Task Feedback has been to your employee(s)"
feedbackHeader = """Dear Employee,
<p>Comments/Feedback has been added to your Goals/Tasks. Please read and act accordingly.</p>
    """

feedbackHeaderDC = """Dear Manager,
<p>Feedback about the Goals/Tasks given your reportee. Please see the details below.</p>
    """
askfeedbackSubject = "GoalSheet:Ask/Give Feedback"
askfeedbackHeader = """Dear Employee,
<p>Please login to GoalSheet application and click on 'Feedback' to give/view responses.</p>
 """
