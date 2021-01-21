"""
K.Srinivas, 7-Apr-2018

Project: Generic
Description: This module provide interface to authorization mechanism (yet to be implemented). Approach is very simple. 
check_auth method is to be called with a string = Auth_TYPE, that will be checked. 
True = user is authorized, False=Not authorized. Default is "Not authorized"


TODO:
a) Once RBAC is implemented, enable the functionality. For now, is_admin is used
b) List all Authorizations available.

KNOWN BUGs: Need to check its usage everywhere
"""
from flask_login import current_user
import logging
from realapp import app

def check_auth(auth_type) :
    app.logger.info("Authorization for %s Requested by user:%s" % (auth_type, current_user.username))
    if current_user and current_user.is_admin : 
        return True
    return False

