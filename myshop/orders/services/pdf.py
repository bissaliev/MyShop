from io import BytesIO

import weasyprint
from django.conf import settings
from django.template.loader import render_to_string
from orders.models import Order


def generate_invoice_pdf(order: Order):
    """Генерация PDF для счета-фактуры"""
    html = render_to_string("orders/order/pdf.html", {"order": order})
    stylesheets = [
        weasyprint.CSS(settings.BASE_DIR / "static/css/pdf.css"),
        weasyprint.CSS(settings.BASE_DIR / "static/css/bootstrap.min.css"),
        weasyprint.CSS(settings.BASE_DIR / "static/css/custom.css"),
    ]
    pdf_buffer = BytesIO()
    weasyprint.HTML(string=html).write_pdf(pdf_buffer, stylesheets=stylesheets)
    pdf_buffer.seek(0)
    return pdf_buffer.read()
