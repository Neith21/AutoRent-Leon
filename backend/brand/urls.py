from django.urls import path
from .views import *

urlpatterns = [
    path('brand', BrandRC.as_view()),
    path('brand/<int:id>', BrandRU.as_view()),
    path('brand/delete/<int:id>', BrandD.as_view()),
]