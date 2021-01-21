"""
K.Srinivas, 2-Nov-2018

Project: Goal sheet and others
Description: This was originally created for testing file-uploads but never used. This should now provide the
following functionality:
a) Store uploaded files and rrovide methods for retriving a URL that can be presented to the user
b) The following attributes need to be stored along with the file:
    1) File-Name
    2) Owner e-mail ID/identifier
    3) Encrypted - Yes/No
    4) Retention Period - No. of days, 0-forever (default)
    5) File ID

Module will have configurable properties:
    1) Storage location

TODO: define upload and download methods:
a) SaveFile [file-name, stream, owner, Encrypt=false,retention_period=0 ], returns fileID
b) getFile (id) - to be returned in a VIEW - the file will be downloaded to the client system
c) deleteFile(id) - Not implemented
d) GetFileMetadata(id) - returns everything except the file-content itself

KNOWN BUGs: Encryption and archiving is not yet implemented
"""

from flask import request, send_from_directory
from werkzeug import secure_filename
from realapp import app, db
import sys
import os
import datetime

from documentmodel import HrmsDocument


#a) SaveFile [file-name, stream, owner, Encrypt=false,retention_period=0 ], returns fileID
def saveFile(fileStream, ownerEmailId, linkedToType, linkedToId, encrypt=False, retensionPeriod=0) :
    #Generate File Name
#    format = "%Y-%m-%dT%H:%M:%S"
    format = "%Y-%m-%dT%H-%M-%S"
    now = datetime.datetime.now().strftime(format) #for filename  generation
    (baseEmail, domain) = ownerEmailId.split('@')
    fname = baseEmail + '_' + now + '_' + secure_filename(fileStream.filename)
    #Add the path
    fullFileName = os.path.join(app.config['UPLOAD_FOLDER'],fname)
    #Save the File
    fileStream.save(fullFileName)
    #Create the DB Entry for the saved file, along with meta data
    hDoc = HrmsDocument()
    hDoc.fileName =  fileStream.filename
    hDoc.empEmail = ownerEmailId #Employee email, after look-up by name
    hDoc.storedFileName = fname # FileName as stored on disk
    hDoc.dateStored = datetime.datetime.now()
    hDoc.retentionDays = retensionPeriod #  number of days to keep
    hDoc.linkedToType = linkedToType #  type of item its linked to : Task = 1, Comments = 2
    hDoc.linkedToId = linkedToId #  item that this is linked to

    hDoc.encrypted = encrypt
    hDoc.archived = False

    #Delete a previous one if it exists
    deleteFileByTypeAndId(linkedToType, linkedToId)

    return saveHrmsDoc(hDoc) # Save and return the ID

#View methods should call this to allow the file to be downloaded
def getFile(fileId) :
    hDoc = HrmsDocument.query.filter_by(id = int(fileId)).first() 
    if not hDoc:
        return False
    if hDoc.archived :
        return False

    return send_from_directory(app.config['UPLOAD_FOLDER'], hDoc.storedFileName, \
        attachment_filename=hDoc.fileName, as_attachment=True)

def getFileByTypeAndId(itemType, itemId) :
    hDoc = HrmsDocument.query.filter_by(linkedToId = int(itemId)).filter_by(linkedToType = int(itemType)).first() 
    if not hDoc :
        return (False, False, False)
    if hDoc.archived :
        return (False, False, False)

    return (app.config['UPLOAD_FOLDER'], hDoc.storedFileName, hDoc.fileName)
    # return send_from_directory(app.config['UPLOAD_FOLDER'], hDoc.storedFileName, \
    #     attachment_filename=hDoc.fileName, as_attachment=True)

#If a file exists for this type and ID, delete it
#Else silently return, no need for any error
def deleteFileByTypeAndId(itemType, itemId) :
    hDoc = HrmsDocument.query. \
        filter_by(linkedToId = int(itemId)).filter_by(linkedToType = int(itemType)).first() 
    if hDoc : #If found delete it.
        deleteUploadedFile( hDoc.storedFileName)
        item = HrmsDocument.query. \
            filter_by(linkedToId = int(itemId)).filter_by(linkedToType = int(itemType)).delete(synchronize_session='evaluate') # Assuming ID to be an INT!! Watchout
        db.session.commit()
    return

def deleteUploadedFile(storedFileName) :
    filePath =  os.path.join(app.config['UPLOAD_FOLDER'], storedFileName)
    print ("FilePath:" + filePath)
    if os.path.exists(filePath):
        os.remove(filePath)
    return

#For testing and other support functions
def getFileMetadata(fileId) :
    hDoc = HrmsDocument.query.filter_by(id = int(fileId)).first() 

    if not hDoc:
        return None

    return (hDoc.fileName, hDoc.empEmail, hDoc.storedFileName,hDoc.dateStored,hDoc.archived,hDoc.encrypted   )

#Convenience method, placed here
def saveHrmsDoc(doc) :
    db.session.add(doc)
    db.session.commit()
    return doc.id

