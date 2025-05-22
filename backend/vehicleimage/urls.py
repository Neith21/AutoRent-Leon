from django.urls import path
from .views import *

urlpatterns = [
    path('vehicleimage/<int:id>', VehicleImageCD.as_view()),
]