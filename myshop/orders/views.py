from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from orders.services.pdf import generate_invoice_pdf

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


class OrderCreateView(View):
    """Размещение заказа"""

    form_class = OrderCreateForm

    def get(self, request):
        form = self.form_class()
        return render(request, "orders/order/create.html", {"form": form})

    def post(self, request):
        cart = Cart(request)
        form = self.form_class(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            self.create_order_item(order, cart)
            # очистить корзину
            cart.clear()
            order_created.delay(order.id)
            # задать заказ в сеансе
            request.session["order_id"] = order.id
            # перенаправить к платежу
            return redirect(reverse("payment:process"))

    def create_order_item(self, order, cart):
        items = []
        for item in cart:
            items.append(
                OrderItem(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            )
        OrderItem.objects.bulk_create(items)


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Представление для показа информации о заказе для администратора.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    """Генерация счета-фактуры в формате PDF для панели администратора."""
    order = get_object_or_404(Order, id=order_id)
    pdf_content = generate_invoice_pdf(order)
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    return response
