from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.versioning import URLPathVersioning

from .models import (
    GenderCategory,
    Product,
    AgeCategory,
    PriceCategory,
)
from .serializers import (
    PriceSerializerVersion1_1,
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
    queryset = PriceCategory.objects.actived()

    class versioning_class(URLPathVersioning):
        allowed_versions = ('v1.0', 'v1.1')

    def get_serializer_class(self):
        serializers = {
            'v1.0': PriceSerializer,
            'v1.1': PriceSerializerVersion1_1,
        }
        return serializers[self.request.version]
