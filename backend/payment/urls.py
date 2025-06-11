from django.urls import path
from .views import PaymentRC, PaymentRetrieveUpdateDestroy

urlpatterns = [
    #path('payment', PaymentRC.as_view()),
    #path('payment/<int:id>', PaymentRU.as_view()),
    #path('payment/delete/<int:id>', PaymentD.as_view()),


    # Endpoint para listar todos los pagos o filtrar por rental_id
    path('payment/', PaymentRC.as_view(), name='payment-list-create'), 
    
    # Endpoint para operaciones CRUD en un pago específico por su ID
    path('payment/<int:pk>/', PaymentRetrieveUpdateDestroy.as_view(), name='payment-retrieve-update-delete'),
]