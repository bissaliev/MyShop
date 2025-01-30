from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    # admin
    path(
        "admin/orders/<int:pk>/",
        views.AdminOrderDetailView.as_view(),
        name="admin_order_detail",
    ),
    path(
        "admin/orders/<int:pk>/pdf/",
        views.AdminOrderPdfView.as_view(),
        name="admin_order_pdf",
    ),
]
