"""
K.Srinivas, 10-Sep-2018

Project: Common Notification Server using SMS to employees

Description: Common methods for TEXTLOCAL.in SMS gateway

"""
import urllib.request
import urllib.parse
import phonenumbers

#Send SMS to a numbers-List given as python list
def sendSMStoList(numberList, message):
    #Convert Numbers into list
    numbers = ""
    for a in numberList :
        numbers += a + ','
    numbers = numbers[:-1] # Get rid of the last ','
#    print ("Numbers=" + numbers)
    resp = "All OK"
    resp, code = sendSMSgeneric('VQPdZt7Hl5g-R9keGDhwRkkAQCx2pvj0YRUBTVddJI', numbers,'MSGIND' , message)
    return resp

#Send SMS to one number
def sendSMStoOne(number, message):
    #Convert Numbers into list, clean-up
    resp, code = sendSMSgeneric('VQPdZt7Hl5g-R9keGDhwRkkAQCx2pvj0YRUBTVddJI', number,'MSGIND' , message)
    return resp

def sendSMSgeneric(apikey, numbers, sender, message):
    params = {'apikey': apikey, 'numbers': numbers, 'message' : message, 'sender': sender, 'test' : '0'}
    f = urllib.request.urlopen('https://api.textlocal.in/send/?'
        + urllib.parse.urlencode(params))
    return (f.read(), f.code)

