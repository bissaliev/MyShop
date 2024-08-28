from cart.cart import Cart
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import OrderCreateForm
from .models import OrderItem
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            # очистить корзину
            cart.clear()
            order_created.delay(order.id)
            # задать заказ в сеансе
            request.session["order_id"] = order.id
            # перенаправить к платежу
            return redirect(reverse("payment:process"))
    else:
        form = OrderCreateForm()
    return render(
        request, "orders/order/create.html", {"cart": cart, "form": form}
    )
