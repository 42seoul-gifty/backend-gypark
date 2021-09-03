from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED
)

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    PaymentValidationSerializer
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
