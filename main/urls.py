"""authapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('get_orders/', csrf_exempt(get_orders_view), name='get_orders'),
    path('get_available_orders/', csrf_exempt(get_available_orders_view), name='get_available_orders'),
    path('add_order/', csrf_exempt(add_order_view), name='add_order'),
    path('cancel_order/', csrf_exempt(cancel_order_view), name='cancel_order'),
    path('modify_order/', csrf_exempt(modify_order_view), name='modify_order'),
    path('get_order_history/', csrf_exempt(get_order_history_view), name='get_order_history'),
    path('accept_order/', csrf_exempt(accept_order_view), name='accept_order'),
    path('get_average_ratings/', csrf_exempt(get_average_ratings_view), name='get_average_ratings'),
    path('add_review/', csrf_exempt(add_review_view), name='add_review'),
    path('change_review/', csrf_exempt(change_review_view), name='change_review'),
    path('delete_review/', csrf_exempt(delete_review_view), name='delete_review'),
    path('add_comment/', csrf_exempt(add_comment_view), name='add_comment'),
    path('delete_comment/', csrf_exempt(delete_comment_view), name='delete_comment'),
    path('get_comments/', csrf_exempt(get_comments_view), name='get_comments'),
]
