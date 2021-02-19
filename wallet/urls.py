
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
    path('get_wallet/', csrf_exempt(get_wallet_view)),
    path('update_wallet/', csrf_exempt(update_wallet_view)),
    path('fund_wallet/', csrf_exempt(fund_wallet_view)),
    path('add_card/', csrf_exempt(add_card_view)),
    path('get_cards/', csrf_exempt(get_cards_view)),
    path('get_transactions/', csrf_exempt(get_transactions_view)),
    path('charge_wallet/', csrf_exempt(charge_wallet_view), name='charge_wallet')
]