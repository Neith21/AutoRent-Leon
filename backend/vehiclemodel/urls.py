from django.urls import path
from .views import *

urlpatterns = [
    path('vehiclemodel', VehicleModelRC.as_view()),
    path('vehiclemodel/<int:id>', VehicleModelRU.as_view()),
    path('vehiclemodel/delete/<int:id>', VehicleModelD.as_view()),
]