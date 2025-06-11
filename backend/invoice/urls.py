from django.urls import path
from .views import *

urlpatterns = [
    path('invoice', InvoiceRC.as_view()),
    path('invoice/<int:id>', InvoiceRU.as_view()),
    path('invoice/suggested-invoice-payments/<int:id>', AutomaticInvoice.as_view()),
    path('invoice/rental-payments/<int:id>', PaymentsRental.as_view()),
    path('invoice/issue-invoice/<int:id>', IssueInvoice.as_view()),
]