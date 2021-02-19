import json
import re
import datetime
import requests
import uuid
import random
import string
from pytz import timezone
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.decorators import decorator_from_middleware
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer
from wallet.models import *
import wallet.utils as utils
from accounts.views import check_key


def get_current_date():
    africa = timezone('Africa/Lagos')
    return datetime.datetime.now(africa)

def generate_uuid(user_id):
    user_id = user_id
    us1 = user_id[:8]
    us2 = user_id[8:]
    rand = ''.join(
    [random.choice(
        string.ascii_letters + string.digits) for n in range(16)])
    return f'{us1}{rand}{us2}'


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

UserData = get_user_model()



#Payment Endpoints

def verify_transaction_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        trans_ref = data.get('trans_ref', None)

        if not ( trans_ref):
            # main_log.error(f'[paystack.views.py; add_user_view(ln-29)] Error: Transaction Ref cannot be blank')
            return JSONResponse(status=400, data={'Error': 'Transaction Ref cannot be blank'})

        paystack_data = utils.verify_transactions(trans_ref)
        if not paystack_data:
            # main_log.error(f'[paystack.views.py; add_user_view(ln-36)] Error: Unable to Generate Authorization Reference')
            return JSONResponse(status=400, data={'Error': 'Unable to Generate Authorization Reference'})
        else:
            return JSONResponse(status=200, data=paystack_data)

def charge_user_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        email = data.get('email', None)
        amount = data.get('amount', None)
        auth_ref = data.get('auth_ref', None)
        reference = data.get('reference', None)

        if not (email and amount and reference and auth_ref):
            # main_log.error(f'[paystack.views.py; charge_user_view(ln-95)] Error: Email or Transaction Ref cannot be blank')
            return JSONResponse(status=400, data={'Error': 'Email or Transaction Ref cannot be blank'})
        else:
            try:
                amount = int(amount)
                charge = utils.charge_authorizaton(auth_ref, email, amount, reference)
                # main_log.info(f'[paystack.views.py; charge_user_view(ln-115)] Charge {charge}')
                if not charge:
                    return JSONResponse(status=200, data={'status': 'error', 'data': {'reference': reference}})
                else:
                    return JSONResponse(status=200, data={'status': 'success', 'data': charge})
            except Exception as e:
                # main_log.error(f'[paystack.views.py; charge_user_view(ln-97)] Error: Error Charging User {e}')
                return JSONResponse(status=400, data={'Error': 'Error Charging User'})


# wallet Endpoints

def get_wallet_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'GET':
        # data = request.POST.copy()
        # user_id = data.get('user_id', None)

        # if not user_id:
        #     return JSONResponse(status=401, data="Userid cannot be null")
        try:
            # user = User.objects.get(user_id=user_id)
            bal = user.wallet.balance
            return JSONResponse(status=200, data=bal)

        except Exception as e:
            print(f'Error {e}')
            return JSONResponse(status=401, data=e)

def fund_wallet_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        data = request.POST.copy()
        amount = data.get('amount', None)
        card_id = data.get('card_id', None)

        if not (amount and card_id):
            return JSONResponse(status=401, data="card_id or amount cannot be null")
        try:
            card = Card.objects.get(card_id=card_id)
            # user = card.user
            reference = generate_uuid(user.user_id)
        except Exception as e:
            
            return JSONResponse(status=401, data='Card not found')
        try:
            if card.origin.lower() == 'paystack':
                data = {'reference': reference, 'amount': amount, 'email': user.email, 'auth_ref': card.auth_ref}
                charge = utils.charge_authorizaton(card.auth_ref, user.email, amount, reference)
                if charge:
                    if charge['data']['status'] == 'success':
                        user.wallet.balance += float(amount)
                        user.wallet.save()
                        transacton_status = charge['data']['status']
                        transacton_ref = charge['data']['reference']
                        return_data ={'status': transacton_status, 'trans_ref': transacton_ref}
                        Transaction.objects.create(wallet=user.wallet, status=transacton_status, reference=transacton_ref, amount=float(amount), trans_type='credit', created_at=get_current_date())
                        return JSONResponse(status=200, data=return_data)
                    else:
                        Transaction.objects.create(wallet=user.wallet, status='failed', reference=reference, amount=float(amount), trans_type='credit', created_at=get_current_date())
                        return JSONResponse(status=400, data={'status': 'error'})
                else:
                    Transaction.objects.create(wallet=user.wallet, status='failed', reference=reference, amount=float(amount), trans_type='credit', created_at=get_current_date())
                    return JSONResponse(status=400, data={'status': 'error'})
            else:
                return JSONResponse(status=400, data={'Error': 'Unknown Gateway'})
        except Exception as e:
            return JSONResponse(status=401, data=e)

def update_wallet_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        data = request.POST.copy()
        # user_id = data.get('user_id', None)
        amount = data.get('amount', None)

        if not (amount):
            return JSONResponse(status=401, data="Userid or amount cannot be null") 
        transacton_ref = str(uuid.uuid4())
        try:
            # user = User.objects.get(user_id=user_id)
            user.wallet.balance += float(amount)
            Transaction.objects.create(wallet=user.wallet, status='success', reference=transacton_ref, amount=float(amount), trans_type='credit', created_at=get_current_date())
            bal = user.wallet.balance
            return JSONResponse(status=200, data=bal)

        except Exception as e:
            Transaction.objects.create(wallet=user.wallet, status='failed', reference=transacton_ref, amount=float(amount), trans_type='credit', created_at=get_current_date())
            # main_log.error(f'[users.views.py; update_wallet(ln-150)] Error: Unable to fund wallet')
            return JSONResponse(status=401, data=e)

def charge_wallet_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        data = request.POST.copy()
        # user_id = data.get('user_id', None)
        amount = data.get('amount', None)
        reference = data.get('reference', None)

        if not (amount):
            return JSONResponse(status=400, data={'Error': 'Email or cannot be blank'})
        else:
            # try:
            #     user = User.objects.get(user_id=user_id)
            # except Exception as e:
            #     return JSONResponse(status=400, data={'Error': 'User Not Found'})
            # else:
            transacton_ref = reference if reference else str(uuid.uuid4())
            if user.wallet.balance < float(amount):
                print('creating transaction...')
                t = Transaction.objects.create(wallet=user.wallet, status="failed", reference=transacton_ref, amount=float(amount), trans_type="debit", created_at=get_current_date())
                return JSONResponse(status=400, data={'status': 'error', 'message': 'Insuffecient Funds'})
            else:
                user.wallet.balance -= float(amount)
                user.wallet.save()
                Transaction.objects.create(wallet=user.wallet, status='success', reference=transacton_ref, amount=float(amount), trans_type='debit', created_at=get_current_date())
                # main_log.info(f'[users.views.py; charge_wallet_view(ln-115)] Success: Charge Successful', user_log=logger)
                return JSONResponse(status=200, data={'status': 'success', 'trans_ref': transacton_ref})

def get_cards_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'GET':
        # data = request.POST.copy()
        # user_id = data.get('user_id', None)

        # if not (user_id):
        #     return JSONResponse(status=400, data={'Error': 'User_ID cannot be blank'})
        # else:
            # try:
            #     user = User.objects.get(user_id=user_id)
            # except Exception as e:
            #     return JSONResponse(status=400, data={'Error': 'User Not Found'})
            # else:
        try:
            cards = [{'id': card.card_id, 'last4': card.last4, 'first6': card.first6, 'origin': card.origin} for card in Card.objects.filter(user=user)]
        except Exception as e:
            return JSONResponse(status=400, data={'Error': 'Error Retrieving Cards'})
        else:
            print(cards)
            return JSONResponse(status=200, data={'Success!': 'User Updated Successfully', 'cards': cards})

def add_card_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
    
        data = request.POST.copy()
        user_id = data.get('user_id', None)
        trans_ref = data.get('trans_ref', None)
        origin = data.get('origin', None)

        if not (trans_ref and origin):
            return JSONResponse(status=400, data={'Error': 'user_id, origin or Transaction Ref cannot be blank'})
        else:
            if origin.lower() == 'paystack':
                data = {'trans_ref': trans_ref}
                paystack_data = utils.verify_transactions(trans_ref)
                
                if not paystack_data:
                    return JSONResponse(status=400, data={'Error': 'Unable to Generate Authorization Reference'})
                else:
                    try:
                        amount = float(paystack_data['data']['amount']) / 100
                        auth_data = paystack_data['data']['authorization']
                        User_id = paystack_data['data']['User']['id']
                        auth_ref = auth_data['authorization_code']
                        reusable = auth_data['reusable']
                        card_type = auth_data['card_type']
                        last4 = auth_data['last4']
                        exp_month = auth_data['exp_month']
                        exp_year = auth_data['exp_year']
                        first6 = auth_data['bin']
                        bank = auth_data['bank']
                        signature = auth_data['signature']
                        country_code = auth_data['country_code']
                        # user = User.objects.get(user_id=user_id)
                        Card.objects.create(user=user, card_type=card_type, last4=last4, first6=first6, exp_month=exp_month, exp_year=exp_year, bank=bank, 
                        signature=signature,country_code=country_code, User_id=User_id, auth_ref=auth_ref, ref_code=trans_ref, verified=True, reusable=reusable, origin=origin)
                        user.wallet.balance += amount
                        user.wallet.save()
                        
                    except Exception as e:
                        return JSONResponse(status=400, data={'Error': '{e}'})
                    else:
                        return JSONResponse(status=201, data={'Success': 'Card Added Successfully'})
        
            else:
                return JSONResponse(status=400, data={'Error': 'Unknown Gateway'})

def get_transactions_view(request):
    user = check_key(request)
    # if not user:
    #     return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'GET':
        # data = request.POST.copy()
        # user_id = data.get('user_id', None)

        if not user:
            try:
                transactions = [{'transaction_id':trans.reference, 'amount':trans.amount, 'status':trans.status, 'id': trans.id, 'type':trans.trans_type, 'created_at': trans.created_at.strftime("%m/%d/%Y-%H:%M:%S")} for trans in Transaction.objects.all()]
            except Exception as e:
                # main_log.error(f'[] Error: Unable to retrieve Transactions {e}')
                return JSONResponse(status=400, data='Error Unable to retrieve Transactions')
            else:
                return JSONResponse(status=200, data={'transactions':transactions})

        try:
            transactions = [{'transaction_id':trans.reference, 'amount':trans.amount, 'status':trans.status, 'id': trans.id, 'type':trans.trans_type, 'created_at': trans.created_at.strftime("%m/%d/%Y-%H:%M:%S")} for trans in Transaction.objects.filter(wallet=user.wallet)]
        except Exception as e:
            # main_log.error(f'[] Error: Unable to retrieve Transactions {e}')
            return JSONResponse(status=400, data='Error Unable to retrieve Transactions')
        else:
            return JSONResponse(status=200, data={'transactions':transactions})

    else:
        return JSONResponse(status=400, data='Error GET request not available for this endpoint')
