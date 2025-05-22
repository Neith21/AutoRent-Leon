from django.urls import path
from .views import *

urlpatterns = [
    path('vehicle', VehicleRC.as_view()),
    path('vehicle/<int:id>', VehicleRU.as_view()),
    path('vehicle/delete/<int:id>', VehicleD.as_view()),
    path('vehicle/models/<int:id>', ModelsByBrandR.as_view()),
]