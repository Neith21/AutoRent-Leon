from django.urls import path
from .views import * 
#from .views import RentalRC, RentalRetrieveUpdateDestroy, RentalCreateWithInitialPaymentAPIView, RentalFinalizeAPIView, RentalAddPaymentAPIView, RentalCalculatePriceAPIView

urlpatterns = [
    # URLs para Alquileres base (CRUD)
    path('rental/', RentalRC.as_view(), name='rental-list-create'),
    path('rental/<int:pk>/', RentalRetrieveUpdateDestroy.as_view(), name='rental-retrieve-update-destroy'),
    
    # --- ¡NUEVA URL para crear renta con pago inicial! ---
    path('rental/create-with-initial-payment/', RentalCreateWithInitialPaymentAPIView.as_view(), name='rental-create-with-initial-payment'),
    
    # Acciones personalizadas
    path('rental/calculate-price/', RentalCalculatePriceAPIView.as_view(), name='rental-calculate-price'),
    path('rental/<int:pk>/finalize/', RentalFinalizeAPIView.as_view(), name='rental-finalize'),
    path('rental/<int:pk>/add-payment/', RentalAddPaymentAPIView.as_view(), name='rental-add-payment'),
]