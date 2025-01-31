from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic.base import TemplateView
from orders.models import Order
from payment.stripe_session import StripeSession


class PaymentProcessView(View):
    """
    Создание сеанса оформления платежа и перенаправление к платежной форме
    """

    def post(self, request, pk=None):
        order = get_object_or_404(
            Order.objects.select_related("coupon").prefetch_related(
                "items", "items__product"
            ),
            pk=pk,
        )
        # создать сеанс оформления платежа Strip
        stripe = StripeSession(request)
        session = stripe.create_session(order)
        # перенаправить к форме для платежа Stripe
        return redirect(session.url, code=303)


class PaymentCompletedView(TemplateView):
    """Отображение сообщения об успешных платежах"""

    template_name = "payment/completed.html"


class PaymentCanceledView(TemplateView):
    """Отображение сообщения об отмененных платежах"""

    template_name = "payment/canceled.html"
