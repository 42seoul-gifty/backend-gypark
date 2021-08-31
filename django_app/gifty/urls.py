from django.urls import path
from .views import *

app_name = 'gifty'

urlpatterns = [
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('products', ProductListView.as_view(), name='product_list'),
]
