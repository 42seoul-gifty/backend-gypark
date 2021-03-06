from django.contrib import admin
from django.db.models import Count

from .models import (
    Order,
    Receiver
)
from .forms import OrderListChangeForm
from gifty.admin import BaseModelAdmin


class EditableCheckIgnore(admin.checks.ModelAdminChecks):
    # https://stackoverflow.com/questions/19233551/custom-list-editable-field-in-django-admin-change-list-which-doesnt-correspond
    def _check_list_editable_item(self, obj, field_name, label):
        return []


class ReceiverInline(admin.StackedInline):
    model = Receiver
    verbose_name = '수신자'
    verbose_name_plural = '수신자'
    fields = (
        'name',
        'phone',
        'product',
        'shipment_status',
        'uuid',
        'sms_response'
    )
    readonly_fields = (
        'uuid',
        'sms_response'
    )
    extra = 1
    max_num = 1


class OrderAdmin(BaseModelAdmin):
    model = Order
    inlines = (ReceiverInline, )
    list_display = (
        'id',
        'display_genders',
        'price',
        'phone',
        'address',
        'address_detail',
        'selected_product',
        'shipment_status',
    )
    list_editable = (
        'shipment_status',
    )
    checks_class = EditableCheckIgnore

    def get_queryset(self, request):
        queryset = self.model.objects.annotate(cnt_receiver=Count('receivers'))
        has_one_receiver = queryset.filter(cnt_receiver=1)
        return has_one_receiver

    def get_changelist_form(self, request, **kwargs):
        return OrderListChangeForm

    @admin.display(description='성별')
    def display_genders(self, order):
        return ', '.join(
            [str(gender) for gender in order.gender.all()]
        )

    @admin.display(description='연락처')
    def phone(self, order):
        return order.receiver.phone

    @admin.display(description='주소')
    def address(self, order):
        return order.receiver.address.address

    @admin.display(description='상세주소')
    def address_detail(self, order):
        return order.receiver.address.address_detail

    @admin.display(description='선택상품')
    def selected_product(self, order):
        return order.receiver.product

    @admin.display(description='배송상태')
    def shipment_status(self, order):
        return order.receiver.shipment_status


admin.site.register(Order, OrderAdmin)
