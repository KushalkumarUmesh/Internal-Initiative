"""
Project: OnlineExam
Domain: CandidateInteface
Description: This is an Interface to provide the the following:
a) Candidate ID - Unique-key
b) Candidate eMail - Unique 
c) Candidate Name
d) Candidate Designation (optional)
=> It should be possible to retrieve the data if either the ID or e-mail is given.
It is assumed that this data comes from "somewhere", may be HRMS or where-ever. 
The currently implementation is only a dummy to support completion of the rest of the implementation.
The following Users are statically created :
srinivas.kambhampati@msg-global.com, 274
tulsi
mohit


Author: K.Srinivas
16-Mar-2018
"""

from realapp import db
import datetime as dt
import sys
sys.path.insert(0,'../../shared/readconfig')

# User Object from DB
class User(db.Model):
    __tablename__  = 'user'
    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('email_Id', db.String(255), nullable=False )

#This property should return True if this is an active user - in addition to being authenticated, they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accounts may not log in (without being forced of course).
    is_active = db.Column(db.Integer,  nullable=False  )
#This property should return True if the user is authenticated, i.e. they have provided valid credentials. (Only authenticated users will fulfill the criteria of login_required.)
#    is_authenticated = db.Column(db.Integer,  nullable=False  )
#This property should return True if this is an anonymous user. (Actual users should return False instead.)
    is_anonymous = db.Column(db.Integer,  nullable=False  )
    is_admin = db.Column(db.Integer,  nullable=False  )

    def get_id(self) :
        return( str(self.id).encode("utf-8").decode("utf-8") )

    def __init__(self,id,username,is_active,is_anonymous, is_admin  ):
        self.username = username
        self.id = id
        self.is_active = is_active
        self.is_anonymous = is_anonymous
        self.is_admin = is_admin
    
    def save(self) :
        #print("Saving: %s as %d" % (self.username, self.is_authenticated))
        db.session.commit()
        
