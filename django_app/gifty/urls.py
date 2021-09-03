from django.urls import path
from .views import (
    ProductDetailView,
    ProductListView,
    AgeListView,
    GenderListView,
    PriceListView,
    ProductDislikeView,
    ProductLikeView,
)

app_name = 'gifty'

urlpatterns = [
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('products', ProductListView.as_view(), name='product_list'),

    path('ages', AgeListView.as_view(), name='age_list'),
    path('genders', GenderListView.as_view(), name='gender_list'),
    path('prices', PriceListView.as_view(), name='price_list'),

    path('products/<int:pk>/dislike', ProductDislikeView.as_view(), name='product_dislike'),
    path('products/<int:pk>/like', ProductLikeView.as_view(), name='product_like'),
]
