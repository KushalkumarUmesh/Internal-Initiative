"""
K.Srinivas
22-Aug-2018: Interface for BCS authorization. For now, its hard-coded to few people.
Once RBAC is ready, these methods will need to be re-written    
"""

#TODO: Integrate with RBAC and return True for authorized, False for unauthorized
def bcscheckauth(email) :
    if "srinivas.kambhampati"  in email or \
        "mukundan" in email or "pradeep.bala" or \
		nandhini.arumugam in email :
        return True
    return False