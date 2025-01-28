from cart.forms import CartAddProductForm
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from .models import Category, Product


class ProductListView(ListView):
    """Список товаров с фильтрацией по категориям"""

    queryset = Product.objects.filter(available=True)
    template_name = "shop/product/list.html"

    def get_context_data(self, **kwargs):
        category = None
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
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


class ProductDetailView(FormMixin, DetailView):
    """Описание товара"""

    template_name = "shop/product/detail.html"
    queryset = Product.objects.filter(available=True)
    form_class = CartAddProductForm
