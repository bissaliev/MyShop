from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Пользователь"""

    email = models.EmailField("Электронный адрес", unique=True)
    phone_number = models.CharField(
        max_length=10,
        verbose_name="Номер телефона",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{10}$",
                message=(
                    "Номер телефона должен быть в формате: '9999999999'. "
                    "Содержать 10 цифр."
                ),
            )
        ],
    )
