from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.forms import RegisterForm
from django.contrib.auth.views import LoginView


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("shop:product_list")


class LoginUserView(LoginView):
    template_name = "users/login.html"
