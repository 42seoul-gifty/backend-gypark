from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    GenericAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)

from .sms import send_sms
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
        data = {
            'merchant_uid': order.id,
            'receiver_id': order.receivers.values_list('uuid', flat=True),
        }

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
    permission_classes = (IsAuthenticated, OwnerPermission)
    serializer_class = PaymentValidationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.check_object_permissions(request, serializer.order)
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


class ReceiverSendSMSView(GenericAPIView):
    permission_classes = (IsAuthenticated, OwnerPermission)

    def post(self, request, *args, **kwargs):
        receiver = Receiver.get_available_or_404(kwargs['uuid'])
        self.check_object_permissions(request, receiver)

        res = send_sms(
            receiver.order.giver_phone,
            content=receiver.sms_message,
            messages=[
                {'to': receiver.phone}
            ]
        )

        receiver.sms_response = res.text
        receiver.save()

        if res.status_code != 202:
            raise HttpResponseServerError('메세지 전송 실패')
        return Response(status=res.status_code)
