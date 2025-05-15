from django.urls import path
from .views import *

urlpatterns = [
    path('branch', BranchRC.as_view()),
    path('branch/<int:id>', BranchRU.as_view()),
    path('branch/delete/<int:id>', BranchD.as_view()),
]