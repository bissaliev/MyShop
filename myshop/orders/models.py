from django.conf import settings
from django.db import models
from shop.models import Product


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField("оплачен", default=False)
    stripe_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self):
        """
        Метод получает общую стоимость товаров, приобретенных в этом заказе.
        """
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        """
        Метод используется для возврата URL-адреса информационной панели Stripe
        для платежа, связанного с заказом.
        """
        if not self.stripe_id:
            # никаких ассоциированных платежей
            return ""
        path = "/test/" if "_test_" in settings.STRIPE_SECRET_KEY else "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("количество товаров", default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """
        Метод возвращает стоимость товара путем умножения цены товара
        на количество.
        """
        return self.price * self.quantity
