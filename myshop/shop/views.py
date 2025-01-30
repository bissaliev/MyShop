from cart.cart import Cart
from cart.forms import CartAddProductForm
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from shop.models import Category, Product


class CategoryFilterMixin:
    """Миксин добавляющий фильтрацию товаров по категориям"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            context["category"] = category
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class ProductListView(CategoryFilterMixin, ListView):
    """Список товаров с фильтрацией по категориям"""

    queryset = Product.objects.filter(available=True)
    template_name = "shop/product/list.html"
    paginate_by = 24


class CartFormMixin(FormMixin):
    """Миксин для добавления формы добавления товара в корзину"""

    form_class = CartAddProductForm

    def get_initial(self):
        """
        Устанавливаем начальные значения для формы,
        в случае нахождения продукта в корзине,
        """
        initial = super().get_initial()
        obj = self.get_object()
        product_id = str(obj.id)
        cart = Cart(self.request)
        if product_id in cart:
            initial["quantity"] = cart[product_id]["quantity"]
            initial["override"] = True
        return initial


class ProductDetailView(CartFormMixin, DetailView):
    """Описание товара"""

    template_name = "shop/product/detail.html"
    queryset = Product.objects.filter(available=True)
