from django.urls import path

from .views import (
    ProductDetailView,
    ProductListView,
    AgeListView,
    GenderListView,
    PriceListView,
)
from .handlers import test_500_view

app_name = 'gifty'

urlpatterns = [
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('products', ProductListView.as_view(), name='product_list'),

    path('ages', AgeListView.as_view(), name='age_list'),
    path('genders', GenderListView.as_view(), name='gender_list'),
    path('prices', PriceListView.as_view(), name='price_list'),

    path('test_500', test_500_view, name='test_500'),
]
