from django import forms


class CouponApplyForm(forms.Form):
    """
    Форма для ввода пользователем кода купона
    """

    code = forms.CharField()
