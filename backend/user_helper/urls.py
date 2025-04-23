from django.urls import path
from .views import *

urlpatterns = [
    path('user', UserRC.as_view()),
    path('user/<int:id>', UserRUD.as_view()),
    path('user/edit/image', EditImage.as_view()),
]