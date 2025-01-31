from django import forms


class CouponApplyForm(forms.Form):
    """
    Форма для ввода пользователем кода купона
    """

    code = forms.CharField(
        label="Код купона",
        widget=forms.TextInput(attrs={"placeholder": "Промо код"}),
    )
