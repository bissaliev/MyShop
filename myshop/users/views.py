from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from orders.signals import order_signal
from users.forms import RegisterForm, UserChangeForm

User = get_user_model()


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("shop:product_list")


class LoginUserView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        old_session_key = self.request.session.session_key
        response = super().form_valid(form)
        if old_session_key:
            order_signal.send(
                sender=self.request.user.__class__,
                user=self.request.user,
                session_key=old_session_key,
            )
        return response


class LogoutUserView(LogoutView):
    template_name = "users/logout.html"


class ProfileView(DetailView):
    queryset = User.objects.all()
    template_name = "users/profile.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.request.user.id)
        return obj


class ProfileEditView(UpdateView):
    queryset = User.objects.all()
    template_name = "users/profile_edit.html"
    form_class = UserChangeForm

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.request.user.id)

    def get_success_url(self):
        return reverse("users:profile")
