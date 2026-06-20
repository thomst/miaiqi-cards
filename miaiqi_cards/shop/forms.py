from django import forms
from miaiqi_cards.postcards.models import Postcard


class EmailForm(forms.Form):
    email_address = forms.EmailField()


class CartItemForm(forms.Form):
    # Choices will be set by the shop section renderer.
    product = forms.ModelChoiceField(Postcard.objects.all(), required=True)
    quantity = forms.IntegerField(min_value=1, required=True)

    class Media:
        js = ['shop/shop.js']
