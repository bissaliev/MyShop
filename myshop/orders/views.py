from cart.cart import Cart
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from orders.services.pdf import generate_invoice_pdf
from shop.models import Product

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


class UserInitialFormMixin:
    """Миксин для добавления учетных данных пользователя в форму"""

    def get_initial(self):
        """
        Устанавливаем первоначальные значения,
        в случае оформления заказа зарегистрированным пользователем
        """
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            for field in self.form_class.Meta.fields:
                if hasattr(self.request.user, field):
                    initial[field] = getattr(self.request.user, field)
        return initial


class OrderItemMixin:
    """Класс миксин добавляет обработку позиций заказа"""

    def form_valid(self, form):
        cart = Cart(self.request)
        try:
            with transaction.atomic():
                order = form.save()
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                if self.request.user.is_authenticated:
                    order.user = self.request.user
                order.save()
                self.create_order_item(order, cart)
                cart.clear()
                order_created.delay(order.id)
                self.request.session["order_id"] = order.id
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.render_to_response(self.get_context_data(form=form))
        messages.success(self.request, "Заказ оформлен")
        return super().form_valid(form)

    def create_order_item(self, order, cart):
        """Создание позиций товаров и привязка их к заказу."""
        items = []
        products = []
        for item in cart:
            items.append(
                OrderItem(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            )
            if item["product"].quantity < item["quantity"]:
                raise ValidationError(
                    f"Недостаточное количество товара {item['product'].name} "
                    "в наличие."
                )
            item["product"].quantity -= item["quantity"]
            products.append(item["product"])
        Product.objects.bulk_update(products, fields=["quantity"])
        OrderItem.objects.bulk_create(items)


class OrderCreateView(UserInitialFormMixin, OrderItemMixin, CreateView):
    """Создание заказа"""

    form_class = OrderCreateForm
    model = Order
    template_name = "orders/order/create.html"
    success_url = reverse_lazy("payment:process")


class AdminStaffRequiredMixin(UserPassesTestMixin):
    """Разрешаем доступ только персоналу"""

    def test_func(self):
        """Разрешаем доступ только персоналу (is_staff=True)."""
        return self.request.user.is_staff


class AdminOrderDetailView(AdminStaffRequiredMixin, DetailView):
    """
    Представление для показа информации о заказе для администратора.
    """

    model = Order
    template_name = "admin/orders/order/detail.html"


class AdminOrderPdfView(AdminStaffRequiredMixin, View):
    """Генерация счета-фактуры в формате PDF для панели администратора."""

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        pdf_content = generate_invoice_pdf(order)
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
        return response
