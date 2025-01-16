from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("registration/", views.RegisterView.as_view(), name="registration"),
    path("login/", views.LoginUserView.as_view(), name="login"),
]
