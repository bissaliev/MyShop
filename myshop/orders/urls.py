from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.OrderUsersListView.as_view(), name="order_user_list"),
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path(
        "<int:pk>/invoice/",
        views.OrderInvoiceView.as_view(),
        name="order_invoice",
    ),
    path(
        "<int:pk>/delete/",
        views.OrderDeleteView.as_view(),
        name="order_delete",
    ),
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
