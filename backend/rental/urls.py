from django.urls import path
from .views import *

urlpatterns = [
    path('rental', RentalRC.as_view()),
    #path('rental/<int:id>', RentalRU.as_view()),
    #path('rental/delete/<int:id>', RentalD.as_view()),
]