from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
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
    queryset = Product.objects.actived_for_giver()


class ProductListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.actived_for_giver()


class AgeListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AgeSerializer
    queryset = AgeCategory.objects.actived()


class GenderListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = GenderSerializer
    queryset = GenderCategory.objects.actived()


class PriceListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PriceSerializer
    queryset = PriceCategory.objects.actived()
