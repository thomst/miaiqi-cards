from django import forms
from django.forms import formset_factory


class EmailForm(forms.Form):
    email_address = forms.EmailField()


class CartItemForm(forms.Form):
    # Choices will be set by the shop section renderer.
    product = forms.ChoiceField(choices=[], required=True)
    quantity = forms.IntegerField(min_value=1, required=True)

    class Media:
        js = ['shop/shop.js']


CartItemFormset = formset_factory(CartItemForm, can_delete=True, extra=1)
