from coupons.forms import CouponApplyForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from shop.models import Product

from .cart import Cart
from .forms import CartAddProductForm


class CartAddView(View):
    """
    Добавление товаров в корзину или обновления количества
    существующих товаров.
    """

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product,
                quantity=cd["quantity"],
                override_quantity=cd["override"],
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Товар добавлен в корзину",
                    "cart_total": len(cart),
                }
            )
        return JsonResponse(
            {"success": False, "message": "Ошибка добавления товара"},
            status=400,
        )


class CartDeleteView(View):
    """Удаление товаров из корзины"""

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect("cart:cart_detail")


class CartClearView(View):
    """Очистка корзины"""

    def post(self, request):
        cart = Cart(request)
        cart.clear()
        return redirect("cart:cart_detail")


class CartDetailView(View):
    """Отображение корзины и ее товаров."""

    def get(self, request):
        cart = Cart(request)
        for item in cart:
            item["update_quantity_form"] = CartAddProductForm(
                initial={"quantity": item["quantity"], "override": True}
            )

        coupon_apply_form = CouponApplyForm()
        return render(
            request,
            "cart/detail.html",
            {"cart": cart, "coupon_apply_form": coupon_apply_form},
        )
