from django import forms
from django.forms.widgets import TextInput
from Rice.models import Rice_buy_order

class Rice_buy_order_form(forms.ModelForm):
    class Meta:
        model = Rice_buy_order
        fields = '__all__'
        widgets = {
            "order_price": TextInput(attrs={"style": "width:50px;", "placeholder": "请输入"}),
        }