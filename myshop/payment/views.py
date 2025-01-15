from decimal import Decimal
from typing import Any

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from orders.models import Order

# создать экземпляр Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class PaymentProcessView(View):
    """
    Создание сеанса оформления платежа и перенаправление к платежной форме
    """

    def get(self, request):
        order = self.get_order()
        return render(request, "payment/process.html", {"order": order})

    def post(self, request):
        order = self.get_order()
        # создать сеанс оформления платежа Stripe
        session = stripe.checkout.Session.create(
            **self.get_session_data(order)
        )
        # перенаправить к форме для платежа Stripe
        return redirect(session.url, code=303)

    def get_session_data(self, order: Order) -> dict[str, Any]:
        """Создание данных для Stripe сеанса"""
        success_url = self.request.build_absolute_uri(
            reverse("payment:completed")
        )
        cancel_url = self.request.build_absolute_uri(
            reverse("payment:canceled")
        )
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": self.get_line_items(order),
        }
        if order.coupon:
            session_data["discounts"] = [self.get_stripe_coupon(order)]
        return session_data

    def get_line_items(self, order: Order) -> list:
        """Генерация товарных позиций для Stripe"""
        items = []
        for item in order.items.all():
            items.append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                        },
                    },
                    "quantity": item.quantity,
                }
            )
        return items

    def get_stripe_coupon(self, order: Order) -> dict[str:int]:
        """Создание купона Stripe для заказа"""
        stripe_coupon = stripe.Coupon.create(
            name=order.coupon.code,
            percent_off=order.discount,
            duration="once",
        )
        return {"coupon": stripe_coupon.id}

    def get_order(self):
        order_id = self.request.session.get("order_id", None)
        order = get_object_or_404(
            Order.objects.prefetch_related("items"), id=order_id
        )
        return order


class PaymentCompletedView(TemplateView):
    """Отображение сообщения об успешных платежах"""

    template_name = "payment/completed.html"


class PaymentCanceledView(TemplateView):
    """Отображение сообщения об отмененных платежах"""

    template_name = "payment/completed.html"
