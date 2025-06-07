from django.urls import path
from .views import *

urlpatterns = [
    path('customer', CustomerRC.as_view()),
    #path('customer/<int:id>', CustomerRU.as_view()),
    #path('customer/delete/<int:id>', CustomerD.as_view()),
]