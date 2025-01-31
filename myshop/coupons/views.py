from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import CouponApplyForm
from .models import Coupon


class CouponApplyView(View):
    """
    Представление выполняет валидацию купона и
    сохраняет его в сеансе пользователя.
    """

    def post(self, request):
        referer = request.META.get("HTTP_REFERER", reverse("cart:cart_detail"))
        now = timezone.now()
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                coupon = Coupon.objects.get(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True,
                )
                request.session["coupon_id"] = coupon.id
            except Coupon.DoesNotExist:
                messages.error(request, "Возможно купон истек")
                request.session["coupon_id"] = None
            else:
                messages.success(request, "Купон применен")
        return HttpResponseRedirect(referer)
