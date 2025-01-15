from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from orders.models import Order
from orders.services.pdf import generate_invoice_pdf


@shared_task
def payment_completed(order_id):
    """
    Отправка уведомления на email покупателя при успешной оплате заказа.
    """
    order = Order.objects.get(id=order_id)
    subject = f"My Shop – Счет-фактура заказа № {order.id}"
    message = (
        "Пожалуйста, ознакомьтесь с приложенной счетом-фактурой за вашу "
        "недавнюю покупку."
    )
    email = EmailMessage(
        subject, message, settings.EMAIL_HOST_USER, [order.email]
    )
    pdf_content = generate_invoice_pdf(order)
    email.attach(f"order_{order.id}.pdf", pdf_content, "application/pdf")
    email.send()
