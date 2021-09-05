from django import forms

from .models import (
    Order,
    Receiver
)


class OrderListChangeForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('shipment_status', )

    shipment_status = forms.ChoiceField(
        choices=Receiver._meta.get_field('shipment_status').choices
    )

    def __init__(self, *args, **kwargs):
        order = kwargs.get('instance')
        if order:
            initial = kwargs.get('initial', {})
            initial['shipment_status'] = order.receivers.first().shipment_status
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)


    def save(self, commit=True):
        order = super().save(commit=commit)
        receiver = order.receivers.first()
        receiver.shipment_status = self.cleaned_data['shipment_status']
        receiver.save()
        return order
