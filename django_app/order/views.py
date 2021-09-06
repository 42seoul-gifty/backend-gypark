from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    GenericAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)

from .models import (
    Order,
    Receiver
)
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    PaymentValidationSerializer,
    ReceiverSerializer,
    ReceiverPatchSerializer,
    ReceiverDataSetSerializer
)
from gifty.serializers import ProductSerializer
from user.permissions import (
    OwnerUrlPermission,
    OwnerPermission,
)


class OrderListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, OwnerUrlPermission)
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = {'merchant_uid': order.id}

        return Response(data, HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer


class OrderDetailDeleteView(RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, OwnerUrlPermission, OwnerPermission)
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class PaymentValidationView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentValidationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_200_OK)


class ReceiverDetailUpdateView(RetrieveAPIView):
    permission_classes = tuple()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ReceiverPatchSerializer
        return ReceiverSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_200_OK)

    def get_object(self):
        queryset = Receiver.objects.exclude(shipment_status='배송완료')
        obj = get_object_or_404(queryset, uuid=self.kwargs['uuid'])
        return obj


class ReceiverDataSetView(RetrieveAPIView):
    permission_classes = tuple()
    serializer_class = ReceiverDataSetSerializer

    def get_object(self):
        queryset = Receiver.objects.exclude(shipment_status='배송완료')
        obj = get_object_or_404(queryset, uuid=self.kwargs['uuid'])
        return obj


class ReceiverLikeProductsView(ListAPIView):
    permission_classes = tuple()
    serializer_class = ProductSerializer

    def get_queryset(self):
        receiver = Receiver.get_available_or_404(self.kwargs['uuid'])
        return receiver.likes.all()
