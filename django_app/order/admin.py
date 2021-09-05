from django.contrib import admin
from django.db.models import Count

from .models import Order
from .forms import OrderListChangeForm


class EditableCheckIgnore(admin.checks.ModelAdminChecks):
    # https://stackoverflow.com/questions/19233551/custom-list-editable-field-in-django-admin-change-list-which-doesnt-correspond
    def _check_list_editable_item(self, obj, field_name, label):
        return []


class OrderAdmin(admin.ModelAdmin):
    model = Order
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
        return order.receiver.address.detail

    @admin.display(description='선택상품')
    def selected_product(self, order):
        return order.receiver.product

    @admin.display(description='배송상태')
    def shipment_status(self, order):
        return order.receiver.shipment_status


admin.site.register(Order, OrderAdmin)
