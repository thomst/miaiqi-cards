from django import forms
from miaiqi_cards.postcards.models import Postcard


class EmailForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse'}),
        )
    repeated_email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse wiederholen'}),
        )


class CartItemForm(forms.Form):
    # Field will be updated by the shop-view.
    product = forms.ModelChoiceField(
        Postcard.objects.all(),
        widget=forms.Select(attrs={'placeholder': 'Postkarte'}),
        )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Anzahl'}),
        )
