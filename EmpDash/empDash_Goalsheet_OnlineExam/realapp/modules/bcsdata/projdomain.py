"""
K.Srinivas, 30-May-2018

Project: Projects and BCS
Description: Domain menthods related to the MsgProject and related objects. The following methods are visualized
c) Generic LIST for select
a) getAccountsForSelect
b) getProgramsForSelect
b) getProjectTypeForSelect
b) getDeliveryStatusForSelect
b) getContractStatusForSelect


TODO: 
a) DONE-This is being developed independently of the runapp.py at the top-level. To be integrated later.

KNOWN BUGs: None
"""
from bcsmodel import *
from realapp import db, app
from hrmsdomain import getDCListForSelect
##############################################################################################################
### generic Tabelist ########################################################################
##############################################################################################################

def getSelectSet(table) :
    cname = eval(table)
    objList = cname.query.all()
    selectList = [(o.name,o.name)  for o in objList]
    return sorted(selectList)

def getProjectTypeForSelect() :
    return getSelectSet("ProjectType")

def getDeliveryStatusForSelect() :
    return getSelectSet("DeliveryStatus")

def getContractStatusForSelect() :
    return getSelectSet("ContractStatus")

def getStaffingStatusForSelect() :
    return getSelectSet("StaffingStatus")

def getBillingModelForSelect() :
    return getSelectSet("BillingModel")

def getAccountsForSelect() :
    cname = eval("MsgAccount")
    objList = cname.query.all()
    selectList = [(o.id,o.accountName)  for o in objList]
    return sorted(selectList)

def getProgramsForSelect(acc = 0) :
    cname = eval("MsgProgram")
    if acc :
        objList = cname.query.filter_by(accountId = acc).all()       
    else:
        objList = cname.query.all()

    selectList = [(o.id,o.programName)  for o in objList]
    return sorted(selectList)

def getAccountName(id) :
    cname = eval("MsgAccount")
    obj = cname.query.filter_by(id = id).first()
    if obj :
        return obj.accountName
    else:
        return "No Account with ID:%d" % (id)
    
def getProgramName(id) :
    cname = eval("MsgProgram")
    obj = cname.query.filter_by(id = id).first()
    if obj :
        return obj.programName
    else:
        return "No Program with ID:%d" % (id)

#Need to move these into an interface file, currentingly mocking it. Data comes from Skill-Interface
def  getSkillCatSetForSelect() :
    return [("1","Technical"),("2","Functional"),("3","Managerial"),("4","Non-Technical"),]

def  getSkillForSelect(cat) :
    return getDCListForSelect() #Using DC-List for Skill as a temporary

def  getCareerLevelForSelect() :
    return [("1","Level 1"),("2","Level 2"),("3","Level 3"),("4","Level 4"),]
    
