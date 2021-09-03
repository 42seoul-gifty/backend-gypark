from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailDeleteView,
    PaymentValidationView
)


app_name = 'order'

urlpatterns = [
    path('users/<int:upk>/orders', OrderListCreateView.as_view(), name='list_create'),
    path('users/<int:upk>/orders/<int:pk>', OrderDetailDeleteView.as_view(), name='detail_delete'),

    path('payment/validation', PaymentValidationView.as_view(), name='validation'),
]
