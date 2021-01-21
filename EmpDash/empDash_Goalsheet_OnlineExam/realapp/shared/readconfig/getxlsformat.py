"""
K.Srinivas, 6-Sep-2018
Description: For reading XLS-files, this method provides mechanisms to confirm that the file needs
the requirements:
a) Only ONE sheet
b) Contains all the required Headers
c) No Duplicate Headers ("Start Date" in Leave-file)
"""
import openpyxl

class GetXLSFormat(object) :
    def __init__(self, configInfile, maxCol=50) :
        self.configInfile = configInfile
        self.attribute = {}  # Dict of Attributes
        self.noOfSheets = 0 #
        self.maxCol = maxCol
        
    #Reading the file, and save key:Value pairs, convert everything into String
    def chkXLSFileFormat(self, headerList) :
        foundError = 0
        mesgStr = ""
        if ".xls" not in self.configInfile:
            foundError +=1
            mesgStr = "FATAL:Only XLS and XLSX formats are supported(%s)" %(self.configInfile)
            return (foundError, mesgStr)
            
        conf_wb = openpyxl.load_workbook(self.configInfile)
        self.noOfSheets = len(conf_wb.worksheets)
        if self.noOfSheets != 1 :
            foundError +=1
            mesgStr += "FATAL:More than ONE Work-Sheet Found in %s" % (self.configInfile)
            return (foundError, mesgStr)

        ws = conf_wb.worksheets[0]
        c_row = 1 # We only read the 1st coll of fist sheet
        c_col = 0
        circuitBreaker = self.maxCol
        while circuitBreaker :
            c_col += 1
            circuitBreaker -= 1 # Decrement
            if not circuitBreaker : # Hit zero
                break # get out of the loop, enough
            c = ws.cell(row=c_row, column=c_col).value
            c= str(c) # Convert to String, just to be sure
            c= c.strip() # Remove white space
            if c and 'None' not in c:
                if c in self.attribute.keys() : # Duplicate Column Name
                    foundError +=1
                    mesgStr += "Duplicate Column Name Found:" + c + " in " + self.configInfile
                self.attribute[c] = 1                
            else :
                break # Stop on 1st Empty Col
        conf_wb.close()
        for i in headerList :
            if i not in self.attribute.keys() :
                foundError +=1  # Flag error
                mesgStr +=  "FATAL: Colum Header:%s: not found in:%s" % (i, self.configInfile)
        return (foundError, mesgStr)

    def noOfSheetsMoreThanOne(self) :
        if self.noOfSheets == 1 :
            return False
        else :
            return True

    #Confirm that Header contains the headings we need. List should contain the head-titles
    def confirmHeader(self, list, printerror = False ) :
        ret_val = True # Return true if everything is hunky-dory
        for i in list :
            if i not in self.attribute.keys() :
                ret_val = False # Flag error
                if printerror : 
                    print("Fatal: Header Item:%s: not a column in the file:%s" % (i, self.configInfile)) # Print on screen if needed
            else :
                continue
        return(ret_val)

