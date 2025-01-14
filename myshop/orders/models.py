from decimal import Decimal

from coupons.models import Coupon
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from shop.models import Product


class Order(models.Model):
    """Заказ"""

    first_name = models.CharField("имя", max_length=50)
    last_name = models.CharField("фамилия", max_length=50)
    email = models.EmailField("электронный адрес")
    address = models.CharField("адрес доставки", max_length=250)
    postal_code = models.CharField("почтовый индекс", max_length=20)
    city = models.CharField("город", max_length=100)
    created = models.DateTimeField("время и дата создания", auto_now_add=True)
    updated = models.DateTimeField("время и дата обновления", auto_now=True)
    paid = models.BooleanField("оплачен", default=False)
    stripe_id = models.CharField(
        "идентификатор платежа", max_length=250, blank=True
    )
    coupon = models.ForeignKey(
        Coupon,
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="купон",
    )
    discount = models.IntegerField(
        "скидка",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self) -> Decimal:
        """Общая сумма заказа с учетом скидки"""
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_total_cost_before_discount(self):
        """Общая сумма заказа без скидки"""
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self) -> Decimal:
        """Скидочная сумма заказа"""
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_stripe_url(self) -> str:
        """Получение URL-адреса информационной панели Stripe оплаты заказа"""
        if not self.stripe_id:
            # никаких ассоциированных платежей
            return ""
        path = "/test/" if "_test_" in settings.STRIPE_SECRET_KEY else "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"


class OrderItem(models.Model):
    """Позиция товара в заказе"""

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("количество товаров", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return str(self.id)

    def get_cost(self) -> Decimal:
        """Получение общей суммы позиций определенного товара"""
        return self.price * self.quantity
