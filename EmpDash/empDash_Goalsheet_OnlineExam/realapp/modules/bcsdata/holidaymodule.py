# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 13:50:30 2018

@author: Srini
"""

import pandas as pd
import re
import datetime as dt

class HolidayData(object) :
    def __init__(self, Infile, sheet_name = 0) :
        self.datafile = Infile
        self.df = pd.read_excel(self.datafile)
        self.holList = self.df.Date # Series of Dates
        
    def isHoliday(self, date) :
        return pd.Timestamp(date) in set(self.holList) # Hope this works
        
