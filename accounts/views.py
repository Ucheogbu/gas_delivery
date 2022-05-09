import json
import re
import datetime
import requests
import random
import string
from pytz import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings as st
from accounts.models import *
from .util import get_api_key
from .decorators import check_key
from .token import get_jwt_token, decode_jwt_token

tz = st.TZN
authprotocol = 'jwt' if st.AUTH_PROTOCOL == 'jwt' else 'custom'

def get_current_date():
    africa = timezone(tz)
    return datetime.datetime.now(africa)

def generate_uuid(user_id):
    user_id = user_id
    us1 = user_id[:8]
    us2 = user_id[8:]
    rand = ''.join(
    [random.choice(
        string.ascii_letters + string.digits) for n in range(16)])
    return f'{us1}{rand}{us2}'



UserData = get_user_model()

# Create your views here.

# Authentication endpoints
def add_user_view(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if not (username and email and password and confirm_password):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: username or email or password or confirm_password cannot be null'})

        elif password != confirm_password:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Passwords don"t match'})

        elif len(password) < 8:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Password is too short, should be at least 8 characters'})

        elif UserData.objects.filter(email=email):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Email already in Use'})
        
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Email is invalid'})

        #TODO:Implement confirm email

        else:
            user = UserData.objects.create(username=username, email=email)
            user.set_password(password)
            user.is_User = True
            user.save()
            key = get_api_key()
            APIKey.objects.create(user=user, api_key=key)
            return JsonResponse({'response_code': 201, 'response_status': 'success', 'message': f'User Created Successfully', 'api_key': key})

def add_vendor_view(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if not (username and email and password and confirm_password):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: username or email or password or confirm_password cannot be null'})

        elif password != confirm_password:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Passwords don"t match'})

        elif len(password) < 8:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Password is too short, should be at least 8 characters'})

        elif UserData.objects.filter(email=email):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Email already in Use'})
        
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Email is invalid'})

        #TODO:Implement confirm email

        else:
            user = UserData.objects.create(username=username, email=email)
            user.set_password(password)
            user.is_vendor = True
            user.save()
            key = get_api_key()
            APIKey.objects.create(user=user, api_key=key)
            return JsonResponse({'response_code': 201, 'response_status': 'success', 'message': f'User Created Successfully', 'api_key': key})

def get_api_key_view(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        email = data.get('email', None)
        password = data.get('password', None)

        if not (email and password):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: email or password cannot be null'})

        if UserData.objects.filter(email=email):
            user = UserData.objects.get(email=email)
            if authprotocol != 'jwt':
                if user.check_password(password):
                    return JsonResponse({'response_code': 200, 'response_status': 'success', 'message': {"api_key": user.user_data.api_key}})
                else:
                    return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incorrect Password'})
            else:
                return JsonResponse({'response_code': 200, 'response_status': 'success', 'message': {"api_key": get_jwt_token(user)}})
        else:
            return JsonResponse({'response_code': 404, 'response_status': 'error', 'message': f'User not Found'})

@check_key()
def change_api_key_view(request):
    user = request.user
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        email = data.get('email', None)
        password = data.get('password', None)

        if not (email and password ):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: email or password cannot be null'})

        if UserData.objects.filter(email=email):
            user = UserData.objects.get(email=email)
            key = get_api_key()
            APIKey.objects.filter(user=user).update(api_key=key)
            return JsonResponse({'response_code': 200, 'response_status': 'success', 'message': f'Key Updated Successfully', 'api_key': key})

@check_key()
def change_password_view(request):
    user = request.user
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        old_password = data.get('old_password', None)
        new_password = data.get('new_password', None)

        if not (old_password and new_password ):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: email or password cannot be null'})

        # if UserData.objects.filter(email=email):
        # user = UserData.objects.get(email=email)
        # key = get_api_key()
        # APIKey.objects.filter(user=user).update(api_key=key)
        key = user.api_key
        if user.check_password(old_password):
            user.set_password(new_password)
        return JsonResponse({'response_code': 200, 'response_status': 'success', 'message': f'Key Updated Successfully', 'api_key': key})

#TODO Implement reset password

def delete_user(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        
        user_id = data.get('user_id', None)

        if not user_id:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: user ID cannot be null'}) 

        if not UserData.objects.filter(user_id=user_id):
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'User not found'}) 
        try:
            UserData.objects.filter(user_id=user_id).delete()
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to delete user {str(e)}'}) 
        else:
            return JsonResponse({'response_code': 201, 'response_status': 'success', 'message': f'User Deleted Sucessfully'}) 

def edit_user(request):
    if request.method == 'POST':
        pass
