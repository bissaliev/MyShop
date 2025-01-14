from django.urls import path

from . import views
from .application import webhooks

app_name = "payment"

urlpatterns = [
    path("process/", views.PaymentProcessView.as_view(), name="process"),
    path("completed/", views.PaymentCompletedView.as_view(), name="completed"),
    path("canceled/", views.PaymentCanceledView.as_view(), name="canceled"),
    path("webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]
