from cart.cart import Cart
from coupons.forms import CouponApplyForm
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.db.models import F
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
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


class OrderItemCreateMixin:
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
                else:
                    order.session_key = self.request.session.session_key
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


class CouponFormContext:
    """Миксин добавления формы купона в контекст"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["coupon_form"] = CouponApplyForm
        return context


class OrderCreateView(
    CouponFormContext, UserInitialFormMixin, OrderItemCreateMixin, CreateView
):
    """Создание заказа"""

    form_class = OrderCreateForm
    model = Order
    template_name = "orders/order/create.html"


class OrderInvoiceView(View):
    """Генерация счета-фактуры в формате PDF."""

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        pdf_content = generate_invoice_pdf(order)
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
        return response


class OwnerFilterMixin:
    """Миксин позволяет фильтровать заказы по владельцу заказа"""

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        session_key = self.request.session.session_key
        return queryset.filter(session_key=session_key)


class OrderUsersListView(OwnerFilterMixin, ListView):
    """Список заказов пользователя"""

    queryset = Order.objects.prefetch_related("items", "items__product")


class UpdateProductQuantityMixin:
    """Миксин позволяет восстановить количество товаров после отмены заказа"""

    def form_valid(self, form):
        referer = self.request.META.get("HTTP_REFERER", self.success_url)
        try:
            with transaction.atomic():
                items = self.object.items.values("product_id", "quantity")
                for item in items:
                    Product.objects.filter(id=item["product_id"]).update(
                        quantity=F("quantity") + item["quantity"]
                    )
                response = super().form_valid(form)
            messages.success(self.request, "Заказ удален")
            return response
        except Exception:
            return HttpResponseRedirect(referer)


class OrderDeleteView(UpdateProductQuantityMixin, DeleteView):
    """Удаление неоплаченных заказов"""

    queryset = Order.objects.filter(paid=False)
    success_url = reverse_lazy("orders:order_user_list")


class OrderDetailView(DetailView):
    """Детальная информация заказа"""

    queryset = Order.objects.select_related("coupon").prefetch_related(
        "items", "items__product"
    )


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


class AdminOrderPdfView(AdminStaffRequiredMixin, OrderInvoiceView):
    """Генерация счета-фактуры в формате PDF для панели администратора."""

    pass
