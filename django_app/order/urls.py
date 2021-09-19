from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailDeleteView,
    PaymentValidationView,
    ReceiverDetailUpdateView,
    ReceiverDataSetView,
    ReceiverSendSMSView,
)


app_name = 'order'

urlpatterns = [
    path('users/<int:upk>/orders', OrderListCreateView.as_view(), name='list_create'),
    path('users/<int:upk>/orders/<int:pk>', OrderDetailDeleteView.as_view(), name='detail_delete'),

    path('payment/validation', PaymentValidationView.as_view(), name='validation'),

    path('receiver/<str:uuid>', ReceiverDetailUpdateView.as_view(), name='receiver_detail'),
    path('receiver/<str:uuid>/choice', ReceiverDataSetView.as_view(), name='choice_dataset'),
    path('receiver/<str:uuid>/send', ReceiverSendSMSView.as_view(), name='send_sms'),
]
