# from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from django.dispatch import Signal, receiver
from orders.models import Order

User = get_user_model()

order_signal = Signal()


@receiver(order_signal, sender=User)
def preserve_session_data(sender, **kwargs):
    """"""
    user = kwargs["user"]
    session_key = kwargs["session_key"]
    Order.objects.filter(session_key=session_key, user__isnull=True).update(
        user=user, session_key=None
    )
