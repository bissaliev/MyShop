from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("название категории", max_length=200)
    slug = models.SlugField("слаг категории", max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name="категория товара",
    )
    name = models.CharField("название товара", max_length=200)
    slug = models.SlugField("слаг товара", max_length=200)
    image = models.ImageField(
        "изображение товара", upload_to="products/%Y/%m/%d", blank=True
    )
    description = models.TextField("описание товара", blank=True)
    price = models.DecimalField("цена товара", max_digits=10, decimal_places=2)
    available = models.BooleanField("наличие товара", default=True)
    created = models.DateTimeField("дата создания", auto_now_add=True)
    updated = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created"]),
        ]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.id, self.slug])
