from decimal import Decimal
from typing import Any

import stripe
from django.conf import settings
from django.http.request import HttpRequest
from django.urls import reverse
from orders.models import Order


class StripeSession:
    """Управление и создание сессий платежного шлюза stripe"""

    def __init__(self, request: HttpRequest):
        self.request = request
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe.api_version = settings.STRIPE_API_VERSION

    def create_session(self, order: Order):
        session = self.stripe.checkout.Session.create(
            **self.get_session_data(order)
        )
        return session

    def get_session_data(self, order: Order) -> dict[str, Any]:
        """Создание данных для Stripe сеанса"""
        success_url = self.get_success_url(self.request)
        cancel_url = self.get_cancel_url(self.request)
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

    def get_line_items(self, order: Order) -> list[dict[str, Any]]:
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

    def get_success_url(self, request: HttpRequest) -> str:
        """Получение маршрута для перенаправления при удачной оплаты"""
        url = self.get_full_url(request, "payment:completed")
        return url

    def get_cancel_url(self, request: HttpRequest) -> str:
        """Получение маршрута для перенаправления при неудачной оплаты"""
        url = self.get_full_url(request, "payment:canceled")
        return url

    @staticmethod
    def get_full_url(request: HttpRequest, view_name: str, *args, **kwargs):
        """
        Метод принимает request, название маршрута и параметры маршрута
        и возвращает полный url-адрес
        """
        relative_url = reverse(view_name, args=args, kwargs=kwargs)
        full_url = request.build_absolute_uri(relative_url)
        return full_url
