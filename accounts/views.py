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
from .decorators import check_key
from .token import get_jwt_token, decode_jwt_token
from .helpers.utils import (
    create_or_update_user,
    tz,
    authprotocol,
    get_current_date,
    generate_uuid,
    get_user_api_key,
    change_api_key,
    change_password,
)


UserData = get_user_model()

# Create your views here.

# Authentication endpoints
def add_user_view(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Unable to decode data {e}",
                }
            )
        email = data.get("email", None)
        address = data.get("address", None)
        state = data.get("state", None)
        country = data.get("country", None)
        email = data.get("email", None)
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)
        is_vendor = data.get("is_vendor", False)
        is_customer = data.get("is_customer", True)
        is_admin = data.get("is_admin", False)

        if not (
            address and email and password and confirm_password and state and country
        ):
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Incomplete data: username or email or password or confirm_password cannot be null",
                }
            )

        elif password != confirm_password:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f'Passwords don"t match',
                }
            )

        elif len(password) < 8:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Password is too short, should be at least 8 characters",
                }
            )

        elif UserData.objects.filter(email=email):
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Email already in Use",
                }
            )

        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Email is invalid",
                }
            )

        # TODO:Implement confirm email

        else:
            user_data = create_or_update_user(
                email,
                phone_number,
                address,
                state,
                country,
                password,
                is_admin,
                is_vendor,
                is_customer,
            )
            return (
                JsonResponse(
                    {
                        "response_code": 201,
                        "response_status": "success",
                        "message": f"User Created Successfully",
                        "api_key": user_data["key"],
                    }
                )
                if user_data
                else JsonResponse(
                    {
                        "response_code": 400,
                        "response_status": "error",
                        "message": f"Error Creating User",
                    }
                )
            )


def get_api_key_view(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Unable to decode data {e}",
                }
            )
        email = data.get("email", None)
        password = data.get("password", None)

        if not (email and password):
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Incomplete data: email or password cannot be null",
                }
            )
        key = get_user_api_key(email, password)
        return (
            JsonResponse(
                {
                    "response_code": 200,
                    "response_status": "success",
                    "message": {"api_key": key},
                }
            )
            if key
            else JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Incorrect Password",
                }
            )
        )


@check_key()
def change_api_key_view(request):
    user = request.user
    if not user:
        return JsonResponse(
            {
                "response_code": 401,
                "response_status": "error",
                "message": f"The request you have made requires authorization",
            }
        )

    if request.method == "POST":
        body = request.body.decode("utf-8")
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Unable to decode data {e}",
                }
            )
        email = data.get("email", None)

        if not email:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Incomplete data: email or password cannot be null",
                }
            )

        key = change_api_key(email)
        return (
            JsonResponse(
                {
                    "response_code": 200,
                    "response_status": "success",
                    "message": f"Key Updated Successfully",
                    "api_key": key,
                }
            )
            if key
            else JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": "User not found",
                }
            )
        )


@check_key()
def change_password_view(request):
    user = request.user
    if not user:
        return JsonResponse(
            {
                "response_code": 401,
                "response_status": "error",
                "message": f"The request you have made requires authorization",
            }
        )

    if request.method == "POST":
        body = request.body.decode("utf-8")
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Unable to decode data {e}",
                }
            )
        old_password = data.get("old_password", None)
        new_password = data.get("new_password", None)

        key = change_password(user.email, old_password, new_password)
        return (
            JsonResponse(
                {
                    "response_code": 200,
                    "response_status": "success",
                    "message": f"Key Updated Successfully",
                    "api_key": key,
                }
            )
            if key
            else JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": "Error changing Password",
                }
            )
        )


# TODO Implement reset password


def delete_user_view(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Unable to decode data {e}",
                }
            )

        user_id = data.get("user_id", None)

        if not user_id:
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"Incomplete data: user ID cannot be null",
                }
            )

        if not UserData.objects.filter(user_id=user_id):
            return JsonResponse(
                {
                    "response_code": 400,
                    "response_status": "error",
                    "message": f"User not found",
                }
            )
        delete_user(user_id)
        return JsonResponse(
            {
                "response_code": 201,
                "response_status": "success",
                "message": f"User Deleted Sucessfully",
            }
        )


def edit_user_view(request):
    if request.method == "POST":
        pass
