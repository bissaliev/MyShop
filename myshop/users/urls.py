from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("registration/", views.RegisterView.as_view(), name="registration"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("edit/", views.ProfileEditView.as_view(), name="profile_edit"),
]
