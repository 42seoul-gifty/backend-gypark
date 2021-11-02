from django.urls import path
from django.views.generic import TemplateView
from tests.views import trigger_error


app_name = 'tests'

urlpatterns = [
    path('create_payment', TemplateView.as_view(template_name='tests/create_payment.html')),
    path('sentry-debug', trigger_error),
]
