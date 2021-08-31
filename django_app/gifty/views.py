from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductSerializer
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
