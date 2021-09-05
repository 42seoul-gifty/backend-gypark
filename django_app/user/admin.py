from django.contrib import admin
from django.db.models import (
    Count,
    Sum,
    Q,
    Subquery,
    OuterRef,
    Value
)
from django.db.models.functions import Coalesce

from allauth.socialaccount.models import SocialAccount

from .models import User
from gifty.admin import BaseModelAdmin


class UserAdmin(BaseModelAdmin):
    model = User
    list_display = (
        'id',
        'user_type',
        'email',
        'nickname',
        'date_joined',
        'order_count',
        'total_price',
        'is_active',
    )
    list_editable = (
        'is_active',
    )

    def get_queryset(self, request):
        account = SocialAccount.objects.filter(user=OuterRef('pk'))
        return self.model.objects.annotate(
            order_count=Count('orders', filter=Q(orders__payment__status='결제완료')),
            total_price=Coalesce(Sum('orders__payment__amount'), 0),
            user_type=Coalesce(Subquery(account.values('provider')[:1]), Value('gifty'))
        )

    @admin.display(description='구매횟수', ordering='order_count')
    def order_count(self, user):
        return user.order_count

    @admin.display(description='구매금액', ordering='total_price')
    def total_price(self, user):
        return user.total_price

    @admin.display(description='유저타입', ordering='user_type')
    def user_type(self, user):
        return user.user_type


admin.site.register(User, UserAdmin)
