from django.urls import path
from .views import *

urlpatterns = [
    path('vehiclecategory', VehicleCategoryRC.as_view()),
    path('vehiclecategory/<int:id>', VehicleCategoryRU.as_view()),
    path('vehiclecategory/delete/<int:id>', VehicleCategoryD.as_view()),
]