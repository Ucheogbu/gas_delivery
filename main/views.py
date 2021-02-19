import json
import re
import datetime
import requests
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
from main.models import *
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

# App Endpoints

def get_orders_view(request):
    # Verify that the user has authorization to access this page
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        orders = Order.objects.all()
        if orders:
            # Convert all order objects to dict and return a list of order dict
            try:
                orders = [model_to_dict(x) for x in orders]
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error Retrieving Error {str(e)}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'orders': orders})
        else:
            return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'No Order Yet!'})

def get_available_orders_view(request):
    user = check_key(request)
    if not user:
        return JsonResponse({'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        orders = Order.objects.filter(is_accepted=False)
        if orders:
            # Convert all order objects to dict and return a list of order dict
            try:
                orders = [model_to_dict(x) for x in orders]
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error Retrieving Error {str(e)}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'orders': orders})
        else:
            return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'No Order Yet!'})

def add_order_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=401, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            amount = data.get('amount', None)
            pickup_address = data.get('pickup_address', None)
            dropoff_address = data.get('dropoff_address', None)
            package_size_in_kg = data.get('package_size_in_kg', None)
            description = data.get('description', None)

            if not (pickup_address and package_size_in_kg and description and dropoff_address and amount):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'user_id or vendor_id or pickup_address or package_size_in_kg or description or dropoff_address or amount cannot be null'})

            try:
                new_order = Order.objects.create(user=user, pickup_address=pickup_address, package_size_in_kg=package_size_in_kg, description=description, dropoff_address=dropoff_address, amount=amount)
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error Creating Order {e}'})
            else:
                return JSONResponse(status=201, data={'response_code': 201, 'response_status': 'success', 'message': f'Order Created Successfully', 'data': new_order})            

def cancel_order_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            order_id = data.get('order_id', None)

        if not order_id:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order ID cannot be null'})
        if not Order.objects.filter(order_id=order_id):
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order not found'})
        else:
            Order.objects.filter(order_id=order_id).update(is_active=False)
            return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Order cancelled successfully'})

def modify_order_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            order_id = data.get('order_id', None)
            amount = data.get('amount', None)
            pickup_address = data.get('pickup_address', None)
            dropoff_address = data.get('dropoff_address', None)
            package_size_in_kg = data.get('package_size_in_kg', None)
            description = data.get('description', None)

            if not order_id:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order Id cannot be null'})
            order = Order.objects.get(order_id=order_id)

            order.amount=amount if amount else order.amount
            order.pickup_address = pickup_address if pickup_address else order.pickup_address
            order.dropoff_address = dropoff_address if dropoff_address else order.dropoff_address
            order.package_size_in_kg = package_size_in_kg if package_size_in_kg else order.package_size_in_kg
            order.description = description if description else order.description

            order.save()
            return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Order Updated Successfully', 'data': model_to_dict(order)})
             
def get_order_history_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if not user.is_vendor:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {str(e)}'})
        else:
            orders = Order.objects.filter(vendor=user)
            if orders:
                # Convert all order objects to dict and return a list of order dict
                try:
                    orders = [model_to_dict(x) for x in orders]
                except Exception as e:
                    return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error Retrieving Error {str(e)}'})
                else:
                    return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'orders': orders})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'No Order Yet!'})

def accept_order_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if not user.is_vendor:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            order_id = data.get('order_id', None)

            if not order_id:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order ID cannot be null'})
            elif not Order.objects.filter(order_id=order_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order not found'})
            elif not Order.objects.filter(order_id=order_id, is_accepted=True):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order is already accepted by a vendor'})
            else:
                Order.objects.filter(order_id=order_id).update(is_accepted=True, vendor=user)
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Order cancelled successfully'})
            
def get_average_ratings_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if not user.is_vendor:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            try:
                ratings_list = [x.review.rating for x in Order.objects.filter(vendor=user)]
                r_len = len(ratings_list)
                average_rating = sum(ratings_list) / r_len
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error Retrieving average rating {e}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message':'Average rating retrieved Successfully', 'data': average_rating})

def add_review_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            rating = data.get('rating', None)
            order_id = data.get('order_id', None)

            if not (rating and order_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Rating or Order ID cannot be null'})
            if not Order.objects.filter(order_id=order_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order matching provided id not found'})
            if int(rating) not in range(1,6):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Invalid Rating Provided'})

            try:
                rev = Reviews.objects.create(order=Order.objects.get(order_id=order_id), rating=int(rating))
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error creating review {e}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Review created successfully', 'data': rev})

def change_review_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            rating = data.get('rating', None)
            review_id = data.get('order_id', None)
            if not (rating and review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Rating or Order ID cannot be null'})
            if not Reviews.objects.filter(review_id=review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order matching provided id not found'})
            if int(rating) not in range(1,6):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Invalid Rating Provided'})

            try:
                Reviews.objects.filter(review_id=review_id).update(rating=int(rating))
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error creating review {e}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Review Updated successfully'})

def delete_review_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            review_id = data.get('order_id', None)

            if not (review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Rating or Order ID cannot be null'})
            if not Reviews.objects.filter(review_id=review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Order matching provided id not found'})

            try:
                Reviews.objects.filter(review_id=review_id).delete()
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Error creating review {e}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Review deleted successfully'})

def add_comment_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            review_id = data.get('review_id', None)
            text_data = data.get('text_data', None)

            if not (review_id and text_data):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Review Id and Text_data cannot be null'})
            if not Reviews.objects.filter(review_id=review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Review Id and Text_data cannot be null'})
            
            try:
                comment = Comments.object.create(user=user, review=Reviews.objects.get(review_id=review_id), text=text_data)
            except Exception as e:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to create Comment{e}'})
            else:
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Comment Created Successfully', 'data': model_to_dict(comment)})

def delete_comment_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            comment_id = data.get('id', None)

            if not comment_id:
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'comment_id cannot be none'})
            if not Comments.objects.filter(id=int(comment_id)):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'comment_id not found'})
            comment = Comments.objects.get(id=int(comment_id))
            if comment.user != user:
                return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
            else:
                comment.delete()
                return JSONResponse(status=200, data={'response_code': 200, 'response_status': 'success', 'message': f'Comment deleted successfully'})

def get_comments_view(request):
    user = check_key(request)
    if not user:
        return JSONResponse(status=400, data={'response_code': 401, 'response_status': 'error', 'message': f'The request you have made requires authorization'})
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        try:
            data = json.loads(body)
        except Exception as e:
            return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Unable to decode data {e}'})
        else:
            review_id = data.get('review_id', None)
            if not (review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Review Id and Text_data cannot be null'})
            if not Reviews.objects.filter(review_id=review_id):
                return JSONResponse(status=400, data={'response_code': 400, 'response_status': 'error', 'message': f'Review matching review id not found'})
            
            review = Reviews.objects.get(review_id=review_id)
            if not review.comments.count():
                return JSONResponse(status=400, data={'response_code': 200, 'response_status': 'success', 'message': f'Review matching review id has no comments', 'data':[]})

            comments = [model_to_dict(x) for x in Comments.objects.filter(review=review)]
            return JSONResponse(status=400, data={'response_code': 200, 'response_status': 'success', 'message': f'Comments Retrieved Successfully', 'data': comments})
