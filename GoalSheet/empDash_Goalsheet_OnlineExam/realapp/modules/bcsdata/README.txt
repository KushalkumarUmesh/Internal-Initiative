This folder will contain modules for loading and processing BCS-Data (claim-data, leave-data)
It will also include holidays-data, that is needed for BCS-methods

Approach is as follows:
Phase-1:
a) Load BCS-claim Data into a table (add/update - we might need to refresh the data couple of times)
	-> Locate data by emp-date : delete and upload
b) Load BCS-Leave-Data into a table 
c) Keep the same data-structures, so everything works.
	-> Test normal weekly BCS-Check functionality
Emp-Dash-board: Stage-1 : Utilization (current functionality in DB)

d) Emp - BCS-Errors in DB 
Emp-Dash-board: Stage-1a : Error-metrics (current functionality in DB)

Phase-2:
a) Create Project Datatables and methods
b) Employee allocation tables and methods
c) Utilization by Project/DC, etc.

Emp-Dashboard: Stage-2 : Availablility, available-date, notification before project-end, etc.

Phase-3:
a) Training Datatables and methods

Emp-Dashboard: Stage-3 : Training, skills, initiatives, etc.

Questions that need to be answered:
Employee Details: Billability, Project status, training status, initiatives, 
Project Details

Goals -> Tasks -> Activities


