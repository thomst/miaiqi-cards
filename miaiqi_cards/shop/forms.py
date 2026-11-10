from django import forms
from .models import Product


class EmailForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse'}),
        )
    repeated_email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse wiederholen'}),
        )


class GroupedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, group_by_field, *args, **kwargs):
        self.group_by_field = group_by_field
        super().__init__(queryset, *args, **kwargs)

    @property
    def choices(self):
        if hasattr(self, '_choices'):
            return self._choices

        # Build a custom dictionary grouping the queryset
        grouped = {}
        for obj in self.queryset:
            group_label = obj.content_type.model_class()._meta.verbose_name.title()
            grouped.setdefault(group_label, []).append((obj.pk, str(obj)))

        # Transform to Django's expected nested format
        choices = [(group, options) for group, options in grouped.items()]

        # Include an empty label if required
        if self.empty_label:
            choices.insert(0, ('', self.empty_label))

        return choices


class CartItemForm(forms.Form):
    product = GroupedModelChoiceField(
        Product.objects.all(),
        group_by_field='content_type',
        widget=forms.Select(attrs={'placeholder': 'Produkt'}),
        )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Anzahl'}),
        )
