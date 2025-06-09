from django.urls import path
from .views import *

urlpatterns = [
    #path('rental', RentalRC.as_view()),
    #path('rental/<int:id>', RentalRU.as_view()),
    #path('rental/delete/<int:id>', RentalD.as_view()),

    # URLs para Alquileres
    path('rental/', RentalRC.as_view(), name='rental-list-create'),
    path('rental/<int:pk>/', RentalRetrieveUpdateDestroy.as_view(), name='rental-retrieve-update-destroy'),
    
    # Acciones personalizadas
    path('rental/calculate-price/', RentalCalculatePriceAPIView.as_view(), name='rental-calculate-price'),
    path('rental/<int:pk>/finalize/', RentalFinalizeAPIView.as_view(), name='rental-finalize'),
    path('rental/<int:pk>/add-payment/', RentalAddPaymentAPIView.as_view(), name='rental-add-payment'),
]