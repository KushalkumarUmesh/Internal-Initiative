"""
K.Srinivas, 22-Mar-2018

Project: HRMS - Retrofit
Description: This is the Model-classes extracted from HRMS-DB, as available on UAT-server on 22-Mar-2018. Primary purpose
    is to provide access to HRMS-entity objects for reporting and extending the functionality. Editing/Modifying is essentially
    planned only for updating master data that does not have an interface (list of managers, etc.)
Instruction for generating this one:
a) flask-sqlacodegen is used. 
b) Its output is further editing to add __bind__ = 'hrms' so that flask can establish a connection to a separate DB
c) Text-clean-up scripts were written..key menthods are there on this laptop a folder with the name given above.


TODO: Nothing for now. In case we need to update any objects, __init__ methods may be needed (but are not required according to some web-sites)

KNOWN BUGs: Had issues iwht BIT, LONGBLOB and TINYBLOB. It works FINE if the DB-is connected!! 
    Cannot CREATE a new DB...it gives strange errors
"""
# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIT, LONGBLOB, TINYBLOB
from sqlalchemy.orm import relationship, backref
#from sqlalchemy.schema import FetchedValue

from realapp import db
#import datetime as dt


class Employee(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'employee'

    SID = db.Column(db.BigInteger, primary_key=True)
    EMPLOYEE_ID = db.Column(db.String(255))
    FIRST_NAME = db.Column(db.String(255))
    MIDDLE_NAME = db.Column(db.String(255))
    LAST_NAME = db.Column(db.String(255))
    PASSWORD = db.Column(db.String(255))
    GENDER = db.Column(db.String(255))
    DATA_OF_BIRTH = db.Column(db.Date)
    DATE_OF_JOINING = db.Column(db.Date)
    DESIGNATION = db.Column(db.String(255))
    OFFICE_EMAIL_ID = db.Column(db.String(255))
    PERSONAL_EMAIL_ID = db.Column(db.String(255))
    ALTERNATE_EMAIL_ID = db.Column(db.String(255))
    EMERGENCY_NO = db.Column(db.String(255))
    TOTAL_EXPERIENCE = db.Column(db.String(255))
    MOBILE_NO = db.Column(db.String(255))
    OFFICE_NO = db.Column(db.String(255))
    HOME_NO = db.Column(db.String(255))
    PAN_NO = db.Column(db.String(255))
    UAN_NO = db.Column(db.String(255))
    PF_NO = db.Column(db.String(255))
    NOTICE_PERIOD = db.Column(db.String(255))
    UserId = db.Column(db.String(255))
    Is_Save_OR_UPDATE = db.Column(BIT(1))
    DEPARTMENT_ID = db.Column(db.ForeignKey('departmant.ID'), index=True)
    DESIGNATION_ID = db.Column(db.ForeignKey('designation.ID'), index=True)
    Manager_ID = db.Column(db.String(255))
    User_Name = db.Column(db.String(255))
    COUNTRY_ID = db.Column(db.ForeignKey('country.ID'), index=True)
    STATE_ID = db.Column(db.ForeignKey('state.ID'), index=True)
    Status = db.Column(db.String(255))
    ROLE_OF_EMPLOYEE = db.Column(db.String(255))
    Nationality = db.Column(db.String(255))
#Additional fields added
    BLOOD_GROUP = db.Column(db.String(255))
    BANK_ACCOUNT_NO = db.Column(db.String(255))
    ENGINEERING_OR_NON_ENGINEERING = db.Column(db.String(255))
#    TOTAL_RELEVANT_EXPERIENCE = db.Column(db.String(255))
#    TOTAL_RELEVANT_EXPERIENCE_DATE = db.Column(db.String(255))

    country = db.relationship('Country', primaryjoin='Employee.COUNTRY_ID == Country.ID', backref='employees')
    departmant = db.relationship('Departmant', primaryjoin='Employee.DEPARTMENT_ID == Departmant.ID', backref='employees')
    designation = db.relationship('Designation', primaryjoin='Employee.DESIGNATION_ID == Designation.ID', backref='employees')
    state = db.relationship('State', primaryjoin='Employee.STATE_ID == State.ID', backref='employees')



class Addres(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'address'

    ID = db.Column(db.BigInteger, primary_key=True)
    LINE1 = db.Column(db.String(100))
    LINE2 = db.Column(db.String(100))
    LINE3 = db.Column(db.String(100))
    COUNTRY_ID = db.Column(db.ForeignKey('country.ID'), index=True)
    STATE_ID = db.Column(db.ForeignKey('state.ID'), index=True)
    CITY = db.Column(db.String(100))
    PINCODE = db.Column(db.BigInteger)
    IS_ENABLE = db.Column(BIT(1))
    ADDRESS_TYPE = db.Column(db.ForeignKey('address_type.ID'), index=True)
    EMPLOYEE_ID = db.Column(db.ForeignKey('employee.SID'), index=True)
    EFFECTIVE_DATE = db.Column(db.String(50))
    TILL_DATE = db.Column(db.String(50))

    address_type = db.relationship('AddressType', primaryjoin='Addres.ADDRESS_TYPE == AddressType.ID', backref='address')
    country = db.relationship('Country', primaryjoin='Addres.COUNTRY_ID == Country.ID', backref='address')
    employee = db.relationship('Employee', primaryjoin='Addres.EMPLOYEE_ID == Employee.SID', backref=backref('address', uselist=False))
    
    state = db.relationship('State', primaryjoin='Addres.STATE_ID == State.ID', backref='address')



class AddressType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'address_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class Adminuploaddocument(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'adminuploaddocuments'

    document_id = db.Column(db.Integer, primary_key=True)
    check_list_document = db.Column(LONGBLOB)
    check_list_document_file_name = db.Column(db.String(255))
    country = db.Column(db.String(255))
    visa_form = db.Column(LONGBLOB)
    visa_form_file_name = db.Column(db.String(255))
    visa_type = db.Column(db.String(255))



class AirlineRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'airline_request'

    airline_request_id = db.Column(db.String(255), primary_key=True)
    arrival_date = db.Column(db.String(255))
    departure_date = db.Column(db.String(255))
    employee_id = db.Column(db.String(255), nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    place_of_arrival = db.Column(db.String(255))
    place_of_departure = db.Column(db.String(255))
    preferred_airline = db.Column(db.String(255))
    preferred_time = db.Column(db.String(255))
    travel_request_id = db.Column(db.ForeignKey('travel_details.travel_request_id'), db.ForeignKey('travel_request.travel_request_id'), index=True)

    travel_request = db.relationship('TravelDetail', primaryjoin='AirlineRequest.travel_request_id == TravelDetail.travel_request_id', backref='airline_requests')
    travel_request1 = db.relationship('TravelRequest', primaryjoin='AirlineRequest.travel_request_id == TravelRequest.travel_request_id', backref='airline_requests')


"""
class Approver(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'approver'
    Id = db.Column(db.Integer),
    Approver = db.Column(db.String(45))

10-Apr-2018: K.Srinivas: Not sure why this was generated instead of a call
Ok...there is no primary key for this table.
"""

t_approver = db.Table(
    'approver',
    db.Column('Id', db.Integer),
    db.Column('Approver', db.String(45))
)


class Asset(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'asset'

    assetId = db.Column(db.String(255), primary_key=True)
    mode_ofReceive = db.Column(db.String(255))
    Make = db.Column(db.String(255))
    model = db.Column(db.String(255))
    serialNo = db.Column(db.String(255))
    description = db.Column(db.String(255))
    receivedON = db.Column(db.Date)
    invoiceDate = db.Column(db.Date)
    warrantyExpDate = db.Column(db.Date)
    amcVendor = db.Column(db.String(255))
    amcFromdate = db.Column(db.Date)
    amcTodate = db.Column(db.Date)
    hasInsurance = db.Column(db.String(255))
    insufromdate = db.Column(db.Date)
    insutodate = db.Column(db.Date)
    assetLife = db.Column(db.Date)
    poFileName = db.Column(db.String(255))
    poFileData = db.Column(LONGBLOB)
    invoiceFileName = db.Column(db.String(255))
    invoiceData = db.Column(LONGBLOB)
    otherdocData = db.Column(LONGBLOB)
    otherDocName = db.Column(db.String(255))
    poId = db.Column(db.BigInteger)
    itemId = db.Column(db.ForeignKey('quotation.id'), index=True)
    status = db.Column(db.ForeignKey('assetstatus.id'), index=True)
    category = db.Column(db.ForeignKey('assetcategory.id'), index=True)
    subCategory = db.Column(db.ForeignKey('assetsubcategory.id'), index=True)
    cond = db.Column(db.ForeignKey('assetcondition.id'), index=True)

    assetcategory = db.relationship('Assetcategory', primaryjoin='Asset.category == Assetcategory.id', backref='assets')
    assetcondition = db.relationship('Assetcondition', primaryjoin='Asset.cond == Assetcondition.id', backref='assets')
    quotation = db.relationship('Quotation', primaryjoin='Asset.itemId == Quotation.id', backref='assets')
    assetstatu = db.relationship('Assetstatu', primaryjoin='Asset.status == Assetstatu.id', backref='assets')
    assetsubcategory = db.relationship('Assetsubcategory', primaryjoin='Asset.subCategory == Assetsubcategory.id', backref='assets')



class Assetcategory(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetcategory'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))



class Assetcondition(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetcondition'

    id = db.Column(db.Integer, primary_key=True)
    cond = db.Column(db.String)



class Assetfile(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetfiles'

    id = db.Column(db.BigInteger, primary_key=True)
    assetList = db.Column(db.String(255))
    invoiceFileName = db.Column(db.String(255))
    invoiceData = db.Column(LONGBLOB)
    otherDocName = db.Column(db.String(255))
    otherdocData = db.Column(LONGBLOB)
    createdDate = db.Column(db.Date)



class Assetrole(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetroles'

    roleId = db.Column(db.Integer, primary_key=True)
    roleName = db.Column(db.String(255))



class Assetstatu(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetstatus'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)



class Assetsubcategory(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'assetsubcategory'

    id = db.Column(db.Integer, primary_key=True)
    categoryId = db.Column(db.ForeignKey('assetcategory.id'), index=True)
    subCategory = db.Column(db.String)

    assetcategory = db.relationship('Assetcategory', primaryjoin='Assetsubcategory.categoryId == Assetcategory.id', backref='assetsubcategories')



class CabRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'cab_request'

    cab_request_id = db.Column(db.String(255), primary_key=True)
    drop_location = db.Column(db.String(255))
    employee_id = db.Column(db.String(255), nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    pickup_address = db.Column(db.String(255))
    pickup_date = db.Column(db.String(255))
    pickup_time = db.Column(db.String(255))
    type_of_cab = db.Column(db.String(255))
    travel_request_id = db.Column(db.ForeignKey('travel_details.travel_request_id'), db.ForeignKey('travel_request.travel_request_id'), index=True)

    travel_request = db.relationship('TravelRequest', primaryjoin='CabRequest.travel_request_id == TravelRequest.travel_request_id', backref='cab_requests')
    travel_request1 = db.relationship('TravelDetail', primaryjoin='CabRequest.travel_request_id == TravelDetail.travel_request_id', backref='cab_requests')



class CertificationDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'certification_details'

    ID = db.Column(db.BigInteger, primary_key=True)
    CERTIFICATION_DATE = db.Column(db.String(500))
    CERTFICATION_VERSION = db.Column(db.String(500))
    PERCENTAGE = db.Column(db.String(500))
    TRAINED_COURSE_NAME = db.Column(db.String(500))
    INSTITUTION_NAME = db.Column(db.String(500))
    INSTITUTION_LOCATION = db.Column(db.String(500))
    COURSE_DURATION = db.Column(db.String(500))
    CERTIFICATION_NO = db.Column(db.String(500))
    CERTIFICATION_NAME = db.Column(db.String(500))
    CERT_NAME_TYPE = db.Column(db.ForeignKey('certification_name_type.ID'), index=True)
    CERT_TYPE = db.Column(db.ForeignKey('certification_type.ID'), index=True)
    employeeId = db.Column(db.ForeignKey('employee.SID'), index=True)
    IS_ENABLE = db.Column(BIT(1))
    IS_SUCCESS = db.Column(BIT(1))

    certification_name_type = db.relationship('CertificationNameType', primaryjoin='CertificationDetail.CERT_NAME_TYPE == CertificationNameType.ID', backref='certification_details')
    certification_type = db.relationship('CertificationType', primaryjoin='CertificationDetail.CERT_TYPE == CertificationType.ID', backref='certification_details')
    employee = db.relationship('Employee', primaryjoin='CertificationDetail.employeeId == Employee.SID', backref='certification_details')



class CertificationNameType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'certification_name_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    CERTIFICATION_TYPE_ID = db.Column(db.ForeignKey('certification_type.ID'), index=True)

    certification_type = db.relationship('CertificationType', primaryjoin='CertificationNameType.CERTIFICATION_TYPE_ID == CertificationType.ID', backref='certification_name_types')



class CertificationType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'certification_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class City(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    state_id = db.Column(db.Integer, nullable=False, index=True)



class ClaimApprover(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'claim_approver'

    approver_name = db.Column(db.String(255), primary_key=True)
    employee_id = db.Column(db.String(255))
    Team = db.Column(db.String(255), nullable=False)



class Contact(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'contacts'

    ID = db.Column(db.Integer, primary_key=True)
    EMAIL = db.Column(db.String(255))
    FIRSTNAME = db.Column(db.String(255))
    LASTNAME = db.Column(db.String(255))
    TELEPHONE = db.Column(db.String(255))



class Country(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'country'

    ID = db.Column(db.BigInteger, primary_key=True)
    COUNTRY_NAME = db.Column(db.String(255))
    CURRENCY = db.Column(db.String(255))
    COUNTRY_DETAILS = db.Column(db.String(5000))



class Currency(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'currency'

    currency_code = db.Column(db.String(255), primary_key=True)
    currency_name = db.Column(db.String(255))



class DegreeType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'degree_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    NAME = db.Column(db.String(500))
    QUALIFICATION_TYPE_ID = db.Column(db.ForeignKey('qualification_type.ID'), index=True)

    qualification_type = db.relationship('QualificationType', primaryjoin='DegreeType.QUALIFICATION_TYPE_ID == QualificationType.ID', backref='degree_types')



class Demandasset(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'demandasset'

    id_No = db.Column(db.BigInteger, primary_key=True)
    request_Id = db.Column(db.String(255))
    request_Type = db.Column(db.String(255))
    emp_id = db.Column(db.String(255))
    request_date = db.Column(db.Date)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    comments = db.Column(db.String(255))
    demandCategory = db.Column(db.ForeignKey('assetcategory.id'), index=True)
    status = db.Column(db.ForeignKey('demandstatus.id'), index=True)
    demandSubcategory = db.Column(db.ForeignKey('assetsubcategory.id'), index=True)

    assetcategory = db.relationship('Assetcategory', primaryjoin='Demandasset.demandCategory == Assetcategory.id', backref='demandassets')
    assetsubcategory = db.relationship('Assetsubcategory', primaryjoin='Demandasset.demandSubcategory == Assetsubcategory.id', backref='demandassets')
    demandstatu = db.relationship('Demandstatu', primaryjoin='Demandasset.status == Demandstatu.id', backref='demandassets')



class Demandstatu(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'demandstatus'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)



class Departmant(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'departmant'

    ID = db.Column(db.BigInteger, primary_key=True)
    DEPARTMENT_NAME = db.Column(db.String(255))
    DC_LEAD = db.Column(db.String(50))



class Department(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'department'

    id = db.Column(db.String(255), primary_key=True)
    department_name = db.Column(db.String(255), nullable=False)



class Designation(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'designation'

    ID = db.Column(db.BigInteger, primary_key=True)
    DESIGNATION_NAME = db.Column(db.String(255))



class DocumentDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'document_details'

    ID = db.Column(db.BigInteger, primary_key=True)
    UAN_FILE_NAME = db.Column(db.String(500))
    UAN_URL = db.Column(db.String(500))
    UAN_NO_DOC = db.Column(LONGBLOB)
    UAN_NO = db.Column(db.String(80))
    PF_FILE_NAME = db.Column(db.String(500))
    PF_URL = db.Column(db.String(500))
    PF_NO_DOC = db.Column(LONGBLOB)
    PF_NO = db.Column(db.String(80))
    ADHAAR_FILE_NAME = db.Column(db.String(500))
    AADHAAR_URL = db.Column(db.String(500))
    AADHAAR_NO_DOC = db.Column(LONGBLOB)
    AADHAR_NO = db.Column(db.String(80))
    DRIVING_LICENCE_FILE_NAME = db.Column(db.String(500))
    DRIVING_LICENCE_URL = db.Column(db.String(500))
    DRIVING_LICENCE_NO_DOC = db.Column(LONGBLOB)
    DRIVING_NO = db.Column(db.String(80))
    PAN_NO_FILE_NAME = db.Column(db.String(500))
    PAN_NO_URL = db.Column(db.String(500))
    PAN_NO_DOC = db.Column(LONGBLOB)
    PAN_NO = db.Column(db.String(80))
    EDUCATION_DETAILS_FILE_NAME = db.Column(db.String(500))
    EDUCATION_DETAILS_URL = db.Column(db.String(500))
    EDUCATION_DETAILS_DOC = db.Column(LONGBLOB)
    EDUCATION_NO = db.Column(db.String(80))
    CERTIFICATE_FILE_NAME = db.Column(db.String(500))
    CERTIFICATE_URL = db.Column(db.String(500))
    CERTIFICATE_DOC = db.Column(LONGBLOB)
    CERTIFICATE_NO = db.Column(db.String(80))
    VOTER_ID_FILE_NAME = db.Column(db.String(500))
    VOTER_ID_URL = db.Column(db.String(500))
    VOTER_ID_DOC = db.Column(LONGBLOB)
    VOTER_ID_NO = db.Column(db.String(80))
    PASSPORT_FILE_NAME = db.Column(db.String(500))
    PASSPORT_URL = db.Column(db.String(500))
    PASSPORT_DOC = db.Column(LONGBLOB)
    PASSPORT_NO = db.Column(db.String(80))

#New Fields Added
    PASSPORT_EXPIRY_DATE = db.Column(db.String(80))
    PASSPORT_ISSUE_PLACE = db.Column(db.String(250))
    PASSPORT_ISSUE_DATE = db.Column(db.String(80))
    NAME_AS_PER_THE_PASSPORT = db.Column(db.String(500))

    employeeId = db.Column(db.ForeignKey('employee.SID'), index=True)

    employee = db.relationship('Employee', primaryjoin='DocumentDetail.employeeId == Employee.SID', backref=backref('document_details', uselist=False))



class Documentname(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'documentname'

    documentname = db.Column(db.String(255), primary_key=True)



class EducationDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'education_details'

    ID = db.Column(db.BigInteger, primary_key=True)
    QUALIFICATION_ID = db.Column(db.ForeignKey('qualification_type.ID'), nullable=False, index=True)
    DEGREE_ID = db.Column(db.ForeignKey('degree_type.ID'), index=True)
    COLLEGE_NAME = db.Column(db.String(500))
    JOINING_DATE = db.Column(db.String(255))
    END_DATE = db.Column(db.String(255))
    PERCENTAGE = db.Column(db.String(50))
    IS_ENABLE = db.Column(BIT(1))
    GRADE = db.Column(db.String(50))
    employeeId = db.Column(db.ForeignKey('employee.SID'), index=True)
    SPECILIZATION = db.Column(db.String(500))
    UNIVERSITY_NAME = db.Column(db.String(500))
    UNIVERSITY_ID = db.Column(db.ForeignKey('university_type.ID'), index=True)
    DegreeType = db.Column(db.String(500))

    degree_type = db.relationship('DegreeType', primaryjoin='EducationDetail.DEGREE_ID == DegreeType.ID', backref='education_details')
    qualification_type = db.relationship('QualificationType', primaryjoin='EducationDetail.QUALIFICATION_ID == QualificationType.ID', backref='education_details')
    university_type = db.relationship('UniversityType', primaryjoin='EducationDetail.UNIVERSITY_ID == UniversityType.ID', backref='education_details')
    employee = db.relationship('Employee', primaryjoin='EducationDetail.employeeId == Employee.SID', backref='education_details')



class Empassetfile(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'empassetfiles'

    id = db.Column(db.BigInteger, primary_key=True)
    empAssetList = db.Column(db.String(255))
    agreementFileName = db.Column(db.String(255))
    agreementCopy = db.Column(LONGBLOB)



class Empassetmapping(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'empassetmapping'

    id = db.Column(db.BigInteger, primary_key=True)
    empId = db.Column(db.String(255))
    bayNo = db.Column(db.String(255))
    windowsVersion = db.Column(db.String(255))
    osProKey = db.Column(db.String(255))
    msOfficeVersion = db.Column(db.String(255))
    officeProKey = db.Column(db.String(255))
    assignedOn = db.Column(db.Date)
    returnedOn = db.Column(db.Date)
    notes = db.Column(db.String(255))
    assetId = db.Column(db.ForeignKey('asset.assetId'), index=True)
    requestId = db.Column(db.ForeignKey('demandasset.id_No'), index=True)

    asset = db.relationship('Asset', primaryjoin='Empassetmapping.assetId == Asset.assetId', backref='empassetmappings')
    demandasset = db.relationship('Demandasset', primaryjoin='Empassetmapping.requestId == Demandasset.id_No', backref='empassetmappings')




class EmployeeFamilyDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'employee_family_details'

    EMP_FAMILY_ID = db.Column(db.BigInteger, primary_key=True)
    FIRST_NAME = db.Column(db.String(255))
    MIDDLE_NAME = db.Column(db.String(255))
    LAST_NAME = db.Column(db.String(255))
    RELATIONSHIP_ID = db.Column(db.ForeignKey('relationship.ID'), index=True)
    GENDER_ID = db.Column(db.ForeignKey('gender.ID'), index=True)
    DATE_OF_BIRTH = db.Column(db.String(255))
    EMAIL_ID = db.Column(db.String(255))
    MOBILE_NO = db.Column(db.String(255))
    OCCUPATION = db.Column(db.String(255))
    PASSPORTID = db.Column(db.String(255))
    IS_ENABLE = db.Column(BIT(1))
    EMP_ID = db.Column(db.ForeignKey('employee.SID'), nullable=False, index=True)
    ADHAR_DOCUMENT = db.Column(LONGBLOB)
    ADHAR_FILENAME = db.Column(db.String(255))
    AADHAR_NO = db.Column(db.String(80))

    employee = db.relationship('Employee', primaryjoin='EmployeeFamilyDetail.EMP_ID == Employee.SID', backref='employee_family_details')
    gender = db.relationship('Gender', primaryjoin='EmployeeFamilyDetail.GENDER_ID == Gender.ID', backref='employee_family_details')
    relationship = db.relationship('Relationship', primaryjoin='EmployeeFamilyDetail.RELATIONSHIP_ID == Relationship.ID', backref='employee_family_details')



class EmployeeProject(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'employee_project'

    project_name = db.Column(db.String(255), primary_key=True)
    approver_emp_id = db.Column(db.ForeignKey('travel_approver.employee_id'), nullable=False, index=True)
    customer_name = db.Column(db.ForeignKey('project_customer.customer_name'), nullable=False, index=True)

    approver_emp = db.relationship('TravelApprover', primaryjoin='EmployeeProject.approver_emp_id == TravelApprover.employee_id', backref='employee_projects')
    project_customer = db.relationship('ProjectCustomer', primaryjoin='EmployeeProject.customer_name == ProjectCustomer.customer_name', backref='employee_projects')



class EmployeeProjectDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'employee_project_details'

    ID = db.Column(db.BigInteger, primary_key=True)
    PROJECT_NAME = db.Column(db.String(500))
    PROJECT_DESCRIPTION = db.Column(db.String(500))
    KEY_CONTRIBUTION = db.Column(db.String(500))
    START_DATE = db.Column(db.String(50))
    END_DATE = db.Column(db.String(50))
    ROLE_ID = db.Column(db.ForeignKey('role.ID'), index=True)
    employment_id = db.Column(db.ForeignKey('employment_history.ID'), index=True)
    idx = db.Column(db.Integer)
    CLIENT_NAME = db.Column(db.String(100))
    EMPLOYEE_ID = db.Column(db.ForeignKey('employee.SID'), index=True)
    EMPLOYMENT_HISTORY_ID = db.Column(db.ForeignKey('employment_history.ID'), index=True)
    IS_ENABLE = db.Column(BIT(1))
    IS_SUCCESS = db.Column(BIT(1))

    employee = db.relationship('Employee', primaryjoin='EmployeeProjectDetail.EMPLOYEE_ID == Employee.SID', backref='employee_project_details')
    employment_history = db.relationship('EmploymentHistory', primaryjoin='EmployeeProjectDetail.EMPLOYMENT_HISTORY_ID == EmploymentHistory.ID', backref='employmenthistory_employee_project_details')
    role = db.relationship('Role', primaryjoin='EmployeeProjectDetail.ROLE_ID == Role.ID', backref='employee_project_details')
    employment = db.relationship('EmploymentHistory', primaryjoin='EmployeeProjectDetail.employment_id == EmploymentHistory.ID', backref='employmenthistory_employee_project_details_0')



class EmploymentHistory(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'employment_history'

    ID = db.Column(db.BigInteger, primary_key=True)
    COMPANY_NAME = db.Column(db.String(500))
    DESIGNATION = db.Column(db.String(500))
    #IS_ENABLE = db.Column(BIT(1))
    EMPLOYEE_ID = db.Column(db.ForeignKey('employee.SID'), index=True)
    START_DATE = db.Column(db.String(50))
    END_DATE = db.Column(db.String(50))
    ROLE_ID = db.Column(db.ForeignKey('role.ID'), index=True)
    DESIGNATION_ID = db.Column(db.ForeignKey('designation.ID'), index=True)

    designation = db.relationship('Designation', primaryjoin='EmploymentHistory.DESIGNATION_ID == Designation.ID', backref='employment_histories')
    employee = db.relationship('Employee', primaryjoin='EmploymentHistory.EMPLOYEE_ID == Employee.SID', backref='employment_histories')
    role = db.relationship('Role', primaryjoin='EmploymentHistory.ROLE_ID == Role.ID', backref='employment_histories')



class Emprolemapping(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'emprolemapping'

    id = db.Column(db.BigInteger, primary_key=True)
    roleId = db.Column(db.Integer)
    empId = db.Column(db.BigInteger)
    emailId = db.Column(db.String(255))



class EpenseClaimDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'epense_claim_details'

    ID = db.Column(db.Integer, primary_key=True)
    CLAIM_ID = db.Column(db.Integer, index=True)
    TRAVEL_ID = db.Column(db.String(50))
    BILL_AMOUNT = db.Column(db.String(50))
    BILL_CURRENCY = db.Column(db.String(50))
    EX_RATE_TO_BS_CURRENCY = db.Column(db.String(50))
    EX_TO_BS_CURRENCY = db.Column(db.String(50))
    EXPENSE_TYPE = db.Column(db.String(80))
    TASK_CODE = db.Column(db.String(80))
    MISSING_RECP = db.Column(db.String(50))
    EXPENSE_GROUP = db.Column(db.String(50))
    JUSTIFICATION = db.Column(db.String(50))
    ADDITIONAL_INFO = db.Column(db.String(50))
    UPLOADED_DOC = db.Column(LONGBLOB)
    SEQ_NO = db.Column(db.Integer)
    FLAG = db.Column(db.String(45), server_default=db.FetchedValue())
    FILE_NAME = db.Column(db.String(45))



class ExpenseApprover(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'expense_approver'

    Id = db.Column(db.Integer, primary_key=True)
    APPROVER_TEAM = db.Column(db.String(45))
    APPROVER_NAME = db.Column(db.String(45))
    EMPLOYEE_ID = db.Column(db.String(45))



t_expense_city = db.Table(
    'expense_city',
    db.Column('Id', db.Integer),
    db.Column('City', db.String(100)),
    db.Column('Country_id', db.String(100))
)



class ExpenseClaim(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'expense_claim'

    CLAIM_ID = db.Column(db.Integer, primary_key=True)
    NATURE_OF_CLAIM = db.Column(db.String(30))
    TRAVEL_ID = db.Column(db.String(50))
    EMP_ID = db.Column(db.String(50))
    EMP_NAME = db.Column(db.String(50))
    APPROVER = db.Column(db.String(50))
    FROM_DATE = db.Column(db.Date)
    TO_DATE = db.Column(db.Date)
    COUNTRY_TRAVELED = db.Column(db.String(80))
    PROJECT_CODE = db.Column(db.String(80))
    BASE_CURRENCY = db.Column(db.String(50))
    STATUS = db.Column(db.Integer, server_default=db.FetchedValue())
    AMOUNT_LOADED_CARD = db.Column(db.String(45))
    AMOUNT_IN_CASH = db.Column(db.String(45))
    REMAINING_AMOUNT_CARD = db.Column(db.String(45))
    REMAINING_AMOUNT_CASH = db.Column(db.String(45))
    USED_IN_CARD = db.Column(db.String(45))
    USED_IN_CASH = db.Column(db.String(45))
    TOTAL_EXPENSE = db.Column(db.String(45))
    CLAIMED_AMOUNT = db.Column(db.String(45))
    TOTAL_AMOUNT_USED = db.Column(db.String(45))
    FINANCE_STATUS = db.Column(db.String(45), server_default=db.FetchedValue())
    TRAVEL_CLAIM_ID = db.Column(db.String(45))



t_expense_country = db.Table(
    'expense_country',
    db.Column('Id', db.Integer),
    db.Column('Country', db.String(100))
)



t_expense_currency = db.Table(
    'expense_currency',
    db.Column('Id', db.Integer),
    db.Column('currency', db.String(45))
)



class ExpenseGroup(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'expense_group'

    id = db.Column(db.Integer, primary_key=True)
    expense_group = db.Column(db.String(100))



class ExpenseType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'expense_type'

    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(100))
    expense_group_id = db.Column(db.ForeignKey('expense_group.id', ondelete='CASCADE'), index=True)

    expense_group = db.relationship('ExpenseGroup', primaryjoin='ExpenseType.expense_group_id == ExpenseGroup.id', backref='expense_types')



class FamilyRelation(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'family_relation'

    id = db.Column(db.Integer, primary_key=True)
    relationship = db.Column(db.String(255))
    immigration_request_id = db.Column(db.ForeignKey('immigration_request.immigration_request_id'), nullable=False, index=True)

    immigration_request = db.relationship('ImmigrationRequest', primaryjoin='FamilyRelation.immigration_request_id == ImmigrationRequest.immigration_request_id', backref='family_relations')



class FilesUpload(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'files_upload'

    FILE_ID = db.Column(db.BigInteger, primary_key=True)
    FILE_DATA = db.Column(TINYBLOB)
    FILE_NAME = db.Column(db.String(255))



t_finance_approver = db.Table(
    'finance_approver',
    db.Column('employeeId', db.String(100), server_default=db.FetchedValue()),
    db.Column('finance_approver', db.String(45), server_default=db.FetchedValue())
)



class ForeignExchangeRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'foreign_exchange_request'

    forex_request_id = db.Column(db.String(255), primary_key=True)
    currency = db.Column(db.String(255), nullable=False)
    currency_in_cash = db.Column(db.String(255))
    pre_outstanding_balance_in_card = db.Column(db.String(255))
    pre_outstanding_balance_in_card_currecy = db.Column(db.String(255))
    total_currency_required = db.Column(db.String(255))
    travel_card_amount = db.Column(db.String(255), nullable=False)
    travellers_check_amount = db.Column(db.String(255), nullable=False)
    travel_request_id = db.Column(db.ForeignKey('travel_request.travel_request_id'), db.ForeignKey('travel_details.travel_request_id'), index=True)

    travel_request = db.relationship('TravelDetail', primaryjoin='ForeignExchangeRequest.travel_request_id == TravelDetail.travel_request_id', backref='foreign_exchange_requests')
    travel_request1 = db.relationship('TravelRequest', primaryjoin='ForeignExchangeRequest.travel_request_id == TravelRequest.travel_request_id', backref='foreign_exchange_requests')



class Gender(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'gender'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class HotelList(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'hotel_list'

    id = db.Column(db.String(255), primary_key=True)
    hotel_name = db.Column(db.String(255))
    star_rating = db.Column(db.String(255))
    cityId = db.Column(db.ForeignKey('cities.id'), nullable=False, index=True)

    city = db.relationship('City', primaryjoin='HotelList.cityId == City.id', backref='hotel_lists')



class HotelRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'hotel_request'

    hotel_request_id = db.Column(db.String(255), primary_key=True)
    check_in_date = db.Column(db.String(255))
    check_out_date = db.Column(db.String(255))
    employee_id = db.Column(db.String(255), nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    place_of_visit = db.Column(db.String(255), nullable=False)
    preferred_hotel = db.Column(db.String(255))
    preferred_hotel_type = db.Column(db.String(255))
    preferred_room_type = db.Column(db.String(255))
    travel_request_id = db.Column(db.ForeignKey('travel_details.travel_request_id'), db.ForeignKey('travel_request.travel_request_id'), index=True)

    travel_request = db.relationship('TravelRequest', primaryjoin='HotelRequest.travel_request_id == TravelRequest.travel_request_id', backref='hotel_requests')
    travel_request1 = db.relationship('TravelDetail', primaryjoin='HotelRequest.travel_request_id == TravelDetail.travel_request_id', backref='hotel_requests')



class Hotelexpense(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'hotelexpense'

    HOTEL_ID = db.Column(db.Integer, primary_key=True)
    CLAIM_ID = db.Column(db.ForeignKey('expense_claim.CLAIM_ID'), index=True)
    HOTEL_TYPE = db.Column(db.String(100))
    COUNTRY = db.Column(db.String(100))
    CITY = db.Column(db.String(100))
    HOTEL_NAME = db.Column(db.String(100))
    BOOKED_ON_NAME = db.Column(db.String(100))
    CHECK_IN_DATE = db.Column(db.String(100))
    CHECK_OUT_DATE = db.Column(db.String(100))
    NUMBER_OF_DAYS_STAYED = db.Column(db.String(100))
    PER_DAY_CHARGE = db.Column(db.String(100))
    TOTAL_ROOM_CHARGE = db.Column(db.String(100))
    LAUNDRY_EXPENSE = db.Column(db.String(100))
    TELEPHONE_EXPENSE = db.Column(db.String(100))
    INTERNET_EXPENSE = db.Column(db.String(100))
    FOOD_EXPENSE = db.Column(db.String(100))
    PARKING_EXPENSE = db.Column(db.String(100))
    SERVICE_TAX = db.Column(db.String(100))
    TOTAL_EXPENSE = db.Column(db.String(100))
    PAID_BY = db.Column(db.String(100))
    UPLOAD_DOCUMENT = db.Column(db.String(100))
    CLAIM_DETAILS_ID = db.Column(db.Integer)
    hotelexpensecol = db.Column(db.String(45))

    expense_claim = db.relationship('ExpenseClaim', primaryjoin='Hotelexpense.CLAIM_ID == ExpenseClaim.CLAIM_ID', backref='hotelexpenses')



t_hoteltype = db.Table(
    'hoteltype',
    db.Column('Id', db.Integer),
    db.Column('Hoteltype', db.String(100))
)



class ImmigrationRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'immigration_request'

    immigration_request_id = db.Column(db.String(255), primary_key=True)
    approver = db.Column(db.String(255), nullable=False)
    country_name = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.String(255), nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    end_date = db.Column(db.String(255), nullable=False)
    have_valid_visa = db.Column(db.String(255), nullable=False)
    project_of_visit = db.Column(db.String(255), nullable=False)
    purpose_of_visit = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    travelling_with = db.Column(db.String(255), nullable=False)
    visa_type = db.Column(db.String(255), nullable=False)
    approver_emp_Id = db.Column(db.String(255))



class ManagerInfo(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'manager_info'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    departMent_Id = db.Column(db.ForeignKey('departmant.ID'), nullable=False, index=True)
    emp_id = db.Column(db.String(50), unique=True)

    departmant = db.relationship('Departmant', primaryjoin='ManagerInfo.departMent_Id == Departmant.ID', backref='manager_infos')



class Mgraction(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'mgractions'

    mgr_action = db.Column(db.String(255), primary_key=True)



t_nontravelclaim_type = db.Table(
    'nontravelclaim_type',
    db.Column('ID', db.Integer, nullable=False),
    db.Column('Claim_Type', db.String(100), nullable=False)
)



class Nontravelexpense(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'nontravelexpense'

    NON_TRAVEL_ID = db.Column(db.Integer, primary_key=True)
    EMPLOYEE_ID = db.Column(db.String(100))
    TYPE_OF_CLAIM = db.Column(db.String(100))
    DATE_OF_CLAIM = db.Column(db.String(45))
    AMOUNT_OF_CLAIM = db.Column(db.String(100))
    DESCRIPTION_OF_CLAIM = db.Column(db.String(100))
    STATUS = db.Column(db.Integer, server_default=db.FetchedValue())
    FINANCE_STATUS = db.Column(db.String(45), server_default=db.FetchedValue())
    NON_TRAVEL_CLAIM_ID = db.Column(db.String(45))
    NONTRAVEL_DOCUMENT = db.Column(LONGBLOB)
    CURRENCY = db.Column(db.String(45))
    FILE_NAME = db.Column(db.String(45))
    APPROVER = db.Column(db.String(50))



class Pofile(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'pofiles'

    id = db.Column(db.BigInteger, primary_key=True)
    poNumber = db.Column(db.String)
    poLetter = db.Column(LONGBLOB)
    createdDate = db.Column(db.Date)



class Postatu(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'postatus'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)



class ProjectCustomer(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'project_customer'

    customer_name = db.Column(db.String(255), primary_key=True)



class Purchaseorder(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'purchaseorder'

    id = db.Column(db.BigInteger, primary_key=True)
    poNumber = db.Column(db.String(255))
    itemNo = db.Column(db.BigInteger)
    poDate = db.Column(db.Date)
    createdDate = db.Column(db.Date)
    createdBy = db.Column(db.String(255))
    lastUpdatedDate = db.Column(db.Date)
    updatedBy = db.Column(db.String(255))
    status = db.Column(db.ForeignKey('postatus.id'), index=True)
    rejectionReason = db.Column(db.String(255))

    postatu = db.relationship('Postatu', primaryjoin='Purchaseorder.status == Postatu.id', backref='purchaseorders')



class QualificationNameType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'qualification_name_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    QUALIFICATION_TYPE_ID = db.Column(db.ForeignKey('qualification_type.ID'), index=True)

    qualification_type = db.relationship('QualificationType', primaryjoin='QualificationNameType.QUALIFICATION_TYPE_ID == QualificationType.ID', backref='qualification_name_types')



class QualificationType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'qualification_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class Quotation(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'quotation'

    id = db.Column(db.BigInteger, primary_key=True)
    quoteId = db.Column(db.BigInteger)
    vendorName = db.Column(db.String(255))
    makeModel = db.Column(db.String(255))
    description = db.Column(db.String(255))
    unitprice = db.Column(db.Float(asdecimal=True))
    quantity = db.Column(db.Integer)
    totalAmt = db.Column(db.Float(asdecimal=True))
    tax = db.Column(db.String(255))
    nettAmout = db.Column(db.Float(asdecimal=True))
    assignedTo = db.Column(db.Integer)
    status = db.Column(db.ForeignKey('quotestatus.id'), index=True)
    comments = db.Column(db.String(255))

    quotestatu = db.relationship('Quotestatu', primaryjoin='Quotation.status == Quotestatu.id', backref='quotations')



class Quotefile(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'quotefiles'

    id = db.Column(db.BigInteger, primary_key=True)
    quoteFileName = db.Column(db.String(255))
    fileData = db.Column(LONGBLOB)



class Quotestatu(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'quotestatus'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)



class Reason(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'reasons'

    reason = db.Column(db.String(255), primary_key=True)



class Relation(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'relation'

    relationship = db.Column(db.String(255), primary_key=True)



class Relationship(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'relationship'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class Role(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'role'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class SeparationAction(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'separation_action'

    action_id = db.Column(db.BigInteger, primary_key=True)
    checklist = db.Column(db.String(255))
    #complete = db.Column(BIT(1))
    datecomplete = db.Column(db.String(255))
    description = db.Column(db.String(255))
    emp_id = db.Column(db.String(255))
    #mandatory = db.Column(BIT(1))
    remarks = db.Column(db.String(255))
    requestid = db.Column(db.BigInteger)
    status = db.Column(db.String(255))
    task_type = db.Column(db.String(255))



class SeparationEmployee(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'separation_employee'

    request_id = db.Column(db.BigInteger, primary_key=True)
    emp_id = db.Column(db.String(255))
    emp_name = db.Column(db.String(255))
    feedback = db.Column(db.String(255))
    initiatedby = db.Column(db.String(255))
    initiationdate = db.Column(db.DateTime)
    lastworkingday = db.Column(db.String(255))
    mgraction = db.Column(db.String(255))
    reason = db.Column(db.String(255))
    recommenddate = db.Column(db.String(255))
    requestdate = db.Column(db.String(255))



class SeparationTask(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'separation_task'

    task_id = db.Column(db.BigInteger, primary_key=True)
    checklist = db.Column(db.String(255))
    description = db.Column(db.String(255))
    #mandatory = db.Column(BIT(1))
    task_type = db.Column(db.String(255))



class SkillCategory(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'skill_category'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class SkillDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'skill_details'

    ID = db.Column(db.BigInteger, primary_key=True)
    employeeId = db.Column(db.ForeignKey('employee.SID'), nullable=False, index=True)
    SKILL_CATEGORY_ID = db.Column(db.ForeignKey('skill_category.ID'), index=True)
    SKILL_TYPE_ID = db.Column(db.ForeignKey('skill_type.ID'), index=True)
    SKILL_ID = db.Column(db.ForeignKey('skills.ID'), index=True)
    ROLE_ID = db.Column(db.ForeignKey('role.ID'), index=True)
    VERSION = db.Column(db.String(10))
    PROFICIENCY = db.Column(db.String(100))
    LASTUSED = db.Column(db.String(10))
    RELEVENT_EXP_IN_MONTHS = db.Column(db.String(80))
    RELEVENT_EXP_IN_YEARS = db.Column(db.String(80))
    #IS_ENABLE = db.Column(BIT(1))

    role = db.relationship('Role', primaryjoin='SkillDetail.ROLE_ID == Role.ID', backref='skill_details')
    skill_category = db.relationship('SkillCategory', primaryjoin='SkillDetail.SKILL_CATEGORY_ID == SkillCategory.ID', backref='skill_details')
    skill = db.relationship('Skill', primaryjoin='SkillDetail.SKILL_ID == Skill.ID', backref='skill_details')
    skill_type = db.relationship('SkillType', primaryjoin='SkillDetail.SKILL_TYPE_ID == SkillType.ID', backref='skill_details')
    employee = db.relationship('Employee', primaryjoin='SkillDetail.employeeId == Employee.SID', backref='skill_details')



class SkillType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'skill_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    SKILL_CATEGORY_ID = db.Column(db.ForeignKey('skill_category.ID'), index=True)

    skill_category = db.relationship('SkillCategory', primaryjoin='SkillType.SKILL_CATEGORY_ID == SkillCategory.ID', backref='skill_types')



class Skill(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'skills'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    SKILL_TYPE_ID = db.Column(db.ForeignKey('skill_type.ID'), index=True)

    skill_type = db.relationship('SkillType', primaryjoin='Skill.SKILL_TYPE_ID == SkillType.ID', backref='skills')



class State(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'state'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    COUNTRY_ID = db.Column(db.ForeignKey('country.ID'), index=True)

    country = db.relationship('Country', primaryjoin='State.COUNTRY_ID == Country.ID', backref='states')



t_taskcode = db.Table(
    'taskcode',
    db.Column('Id', db.Integer),
    db.Column('taskcode', db.String(100))
)



class TechnologyType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'technology_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class TravelAdmin(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'travel_admin'

    admin_name = db.Column(db.String(255), primary_key=True)
    employee_id = db.Column(db.String(255))



class TravelApprover(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'travel_approver'

    employee_id = db.Column(db.String(255), primary_key=True)
    approver_name = db.Column(db.String(255))



class TravelDetail(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'travel_details'

    travel_request_id = db.Column(db.String(255), primary_key=True)
    employee_id = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255))
    approver_emp_id = db.Column(db.String(255))



class TravelRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'travel_request'

    travel_request_id = db.Column(db.String(255), primary_key=True)
    approver_name = db.Column(db.String(255))
    city_name = db.Column(db.String(255))
    country_name = db.Column(db.String(255))
    customer_name = db.Column(db.String(255))
    emp_department = db.Column(db.String(255))
    employee_id = db.Column(db.String(255), nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    expected_date_of_departure = db.Column(db.String(255))
    expected_duration_in_days = db.Column(db.String(255))
    expected_date_of_arrival = db.Column(db.String(255))
    immigration_id = db.Column(db.String(255), nullable=False)
    isBillable = db.Column(db.String(255))
    project_id = db.Column(db.String(255))
    purpose_of_visit = db.Column(db.String(255))
    travelling_with = db.Column(db.String(255))
    type_of_travel = db.Column(db.String(255))



class UniversityType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'university_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))



class Visa(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'visa'

    visa_type = db.Column(db.String(255), primary_key=True)



class VisaDocument(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'visa_documents'

    visa_request_document_id = db.Column(db.Integer, primary_key=True)
    date_of_birth = db.Column(db.String(255))
    document_name = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255), nullable=False)
    relationship = db.Column(db.String(255), nullable=False)
    visa_document = db.Column(LONGBLOB, nullable=False)
    visa_request_id = db.Column(db.ForeignKey('visa_request.visa_request_id'), nullable=False, index=True)

    visa_request = db.relationship('VisaRequest', primaryjoin='VisaDocument.visa_request_id == VisaRequest.visa_request_id', backref='visa_documents')



class VisaRequest(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'visa_request'

    visa_request_id = db.Column(db.String(255), primary_key=True)
    end_date = db.Column(db.String(255))
    immigration_request_id = db.Column(db.String(255), nullable=False, unique=True)
    start_date = db.Column(db.String(255))
    visa_form = db.Column(LONGBLOB, nullable=False)
    visa_form_file_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))



class VisaType(db.Model):
    __bind_key__ = 'hrms'
    __tablename__ = 'visa_type'

    ID = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(500))
    COUNTRY_ID = db.Column(db.ForeignKey('country.ID'), nullable=False, index=True)

    country = db.relationship('Country', primaryjoin='VisaType.COUNTRY_ID == Country.ID', backref='visa_types')