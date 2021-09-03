from typing import List
from django.db.models.query import QuerySet
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated

from .models import (
    GenderCategory,
    Product,
    AgeCategory,
    PriceCategory,
)
from .serializers import (
    ProductSerializer,
    AgeSerializer,
    GenderSerializer,
    PriceSerializer,
)
from .filters import ProductFilter


class ProductDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.all()


class AgeListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AgeSerializer
    queryset = AgeCategory.objects.all()


class GenderListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = GenderSerializer
    queryset = GenderCategory.objects.all()


class PriceListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PriceSerializer
    queryset = PriceCategory.objects.all()
