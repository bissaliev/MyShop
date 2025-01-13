from cart.forms import CartAddProductForm
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Category, Product


class ProductListView(View):
    """Список товаров с фильтрацией по категориям"""

    def get(self, request, category_slug=None):
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(available=True)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        return render(
            request,
            "shop/product/list.html",
            {
                "category": category,
                "categories": categories,
                "products": products,
            },
        )


class ProductDetailView(View):
    """Детальная информации товара"""

    def get(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        cart_product_form = CartAddProductForm()
        return render(
            request,
            "shop/product/detail.html",
            {"product": product, "cart_product_form": cart_product_form},
        )
