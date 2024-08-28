from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    """Модель купонов."""

    code = models.CharField("код купона", max_length=50, unique=True)
    valid_from = models.DateTimeField("дата и время начала действия купона")
    valid_to = models.DateTimeField("дата и время окончания действия купона")
    discount = models.IntegerField(
        "процент скидки",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Процентное значение (от 0 до 100)",
    )
    active = models.BooleanField("активен")

    class Meta:
        verbose_name = "Купон"
        verbose_name_plural = "Купоны"

    def __str__(self):
        return self.code
