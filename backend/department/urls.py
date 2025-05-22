from django.urls import path
from .views import *

urlpatterns = [
    path('department', DepartmentRC.as_view()),
    #path('department/<int:id>', DepartmentRU.as_view()),
    #path('department/delete/<int:id>', DepartmentD.as_view()),
]