from django.urls import path
from django.views.generic import TemplateView


app_name = 'tests'

urlpatterns = [
    path('create_payment', TemplateView.as_view(template_name='tests/create_payment.html')),
]
