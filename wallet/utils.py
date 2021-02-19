import requests
import json
import random
import string
from django.conf import settings

pk = settings.PAYSTACK_PUBLIC
sk = settings.PAYSTACK_SECRET

def verify_transactions(ref):
    """
    A Helper function used to verify a paystack transaction so as to generate a auth_ref code

    Arguments:
        ref {string} -- A transaction reference as returned by paystack after a successfull billing

    # Sample return Data

    {"status":True, "message":"Verification successful",
        "data":{"amount":27000,"currency":"NGN","transaction_date":"2016-10-01T11:03:09.000Z","status":"success",
        "reference":"DG4uishudoq90LD","domain":"test","metadata":0,"gateway_response":"Successful","message":None,
        "channel":"card","ip_address":"41.1.25.1",
        "log": {"time_spent":9,"attempts":1,"authentication":None,"errors":0,"success":True,"mobile":False,"input":[],
        "channel":None, 
        "history": [
            {"type":"input","message":"Filled these fields: card number, card expiry, card cvv",
                "time":7,}, 
            {"type":"action","message":"Attempted to pay","time":7,}, 
            {"type":"success", "message":"Successfully paid","time":8,}, 
            {"type":"close","message":"Page closed","time":9,}
            ]},
        
        "fees":None,"authorization":
            {"authorization_code":"AUTH_8dfhjjdt","card_type":"visa","last4":"1381","exp_month":"08","exp_year":"2018",
            "bin":"412345","bank":"TEST BANK","channel":"card","signature":"SIG_idyuhgd87dUYSHO92D","reusable":True,
            "country_code":"NG",}, 
        
        "customer":{"id":84312, "customer_code":"CUS_hdhye17yj8qd2tx", "first_name":"BoJack","last_name":"Horseman","email":"bojack@horseman.com",},"plan":"PLN_0as2m9n02cl0kp6","requested_amount":1500000,}
    }
    """    
    verification_url = f'https://api.paystack.co/transaction/verify/{ref}'
    
    req = requests.get(url=verification_url, 
                       headers={
                           'Authorization': 
                                f'Bearer {sk}'
                           })
    if req.status_code:
        data = req.json()
        # print(data)
        if data['status']:
            return data
        else:
            return None
    else:
        return None


def generate_uuid():
    rand = ''.join(
    [random.choice(
        string.ascii_letters + string.digits) for n in range(32)])
    return f'{rand}'


def charge_authorizaton(authorization_code, email, amount, reference=''):
    """
    A Helper function for charging authenticated/verified users when needed

    Arguments:
        authorization_code {[string]} -- [User authorization code from paystack]
        email {[string]} -- [customers email]
        amount {[integer]} -- [amount to be charged]
    
    # Sample return Data

    {"status":true, "message":"Charge attempted", "data":{"amount":500000, "currency":"NGN", "transaction_date":"2016-10-01T14:29:53.000Z", "status":"success", "reference":"0bxco8lyc2aa0fq", "domain":"live", "metadata":None, "gateway_response":"Successful", "message":None, "channel":"card", "ip_address":None, "log":None, "fees":None, "authorization":{ "authorization_code":"AUTH_5z72ux0koz", "bin":"408408", "last4":"4081", "exp_month":"12", "exp_year":"2020", "channel":"card", "card_type":"visa DEBIT", "bank":"Test Bank","country_code":"NG", "brand":"visa", "reusable":true, "signature":"SIG_ZdUx7Z5ujd75rt9OMTN4",}, "customer":{"id":90831, "customer_code":"CUS_fxg9930u8pqeiu", "first_name":"Bojack","last_name":"Horseman", "email":"bojack@horsinaround.com", }, "plan":0}
    
    """    
    amount = int(amount) * 100
    charge_url = 'https://api.paystack.co/transaction/charge_authorization'
    auth_header = {"Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    data = json.dumps({"authorization_code": authorization_code, "email": email, "amount": amount, 'reference':reference})

    req = requests.post(url=charge_url,headers=auth_header, data=data)
    
    if req.status_code:
        data = req.json()
        # print(data)
        if data['status']:
            return data
        else:
            return None
    else:
        return None


def check_pending(reference):
    """
    Helper function for ascertaining the status of pending transactions

    Arguments:
        reference {String} -- reference of the transaction to check

    Returns:
        dict -- A dictionary containing transaction metadata
    """    

    url = f"https://api.paystack.co/charge/{reference}"

    headers = {
        'user-agent': "Paystack-Developers-Hub",
        'authorization': f"Bearer {sk}"
        }

    req = requests.get(url, headers=headers)

    if req.status_code:
        data = req.json()
        # print(data)
        if data['status']:
            return data
        else:
            return None
    else:
        return None
