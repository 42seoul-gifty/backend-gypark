from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

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
    ProductReactSerializer
)
from .filters import ProductFilter
from order.models import Receiver


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


class ProductDislikeView(GenericAPIView):
    permission_classes = tuple()
    serializer_class = ProductReactSerializer
    queryset = Product.objects.all()

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uuid = serializer.validated_data['receiver_id']
        receiver = Receiver.get_available_or_404(uuid)

        product.dislikes.add(receiver)
        if product.likes.filter(id=receiver.id):
            product.likes.remove(receiver)

        return Response(status=HTTP_200_OK)


class ProductLikeView(GenericAPIView):
    permission_classes = tuple()
    serializer_class = ProductReactSerializer
    queryset = Product.objects.all()

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uuid = serializer.validated_data['receiver_id']
        receiver = Receiver.get_available_or_404(uuid)

        product.likes.add(receiver)
        if product.dislikes.filter(id=receiver.id):
            product.dislikes.remove(receiver)

        return Response(status=HTTP_200_OK)
