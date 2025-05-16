from django.urls import path
from .views import *

urlpatterns = [
    path('user', UserR.as_view()),
    path('user/<int:id>', UserRU.as_view()),
    path('user/edit/image', EditImage.as_view()),
    path('user/delete/<int:id>', UserD.as_view()),
    path('user/edit/password', EditPassword.as_view()),
    path('user/permission/<int:id>', UserPermissionsView.as_view()),
]