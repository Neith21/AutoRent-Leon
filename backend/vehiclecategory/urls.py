from django.urls import path
from .views import *

urlpatterns = [
    path('vehiclecategory', VehicleCategoryRC.as_view()),
    #path('vehiclecategory/<int:id>', BrandRU.as_view()),
    #path('vehiclecategory/delete/<int:id>', BrandD.as_view()),
]