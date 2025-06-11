from django.urls import path
from .views import *

urlpatterns = [
    path('company', CompanyRU.as_view()),
]