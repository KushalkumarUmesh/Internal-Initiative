"""
K.Srinivas
17-Aug-2018: Read the BCS Org-Structure XLS, that is downloaded from BCS to extract BCS-Name<->email ID mapping
"""

import pandas as pd
import re
from getxlsformat import GetXLSFormat
##############################################################################################################
### Read BCS Org Structure ########################################################################
##############################################################################################################
def readBCSOrgStructure(bcsInfile) :
    xlsfile = GetXLSFormat(bcsInfile)
    (error, message) = xlsfile.chkXLSFileFormat(("Name", "Email"))
    if error :
        return (error, message)
    del xlsfile # Delete the object

    xls = pd.ExcelFile(bcsInfile) # we can use pd.read_csv
    mylist = xls.sheet_names
    sheet = mylist[0]
    df = xls.parse(sheet, na_filter=False)
    #bcs_df = pd.read_excel(bcsInfile)
    df.fillna('')
    s = df.Name
    bcsNameHash = dict()
    for n in s.index : # For each index of s, assuming it to be same as that in DF
        eName = s[n] # EmployeeName
        bcsNameHash[eName] = df.iloc[n]["Email"] # email-ID
    #Check if there are any e-mails not in HRMS and notify    
    return (0, bcsNameHash)

