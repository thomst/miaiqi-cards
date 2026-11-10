from django import forms
from django.forms.models import ModelChoiceIterator
from .models import Product


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ('', self.field.empty_label)

        grouped = {}
        queryset = self.queryset.select_related(self.field.group_by_field)
        for obj in queryset.iterator():
            group_object = getattr(obj, self.field.group_by_field)
            group_label = group_object.model_class()._meta.verbose_name.title()
            grouped.setdefault(group_label, []).append(self.choice(obj))

        yield from grouped.items()


class GroupedModelChoiceField(forms.ModelChoiceField):
    iterator = GroupedModelChoiceIterator

    def __init__(self, queryset, group_by_field, *args, **kwargs):
        self.group_by_field = group_by_field
        super().__init__(queryset, *args, **kwargs)


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


class EmailForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse'}),
        )
    repeated_email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse wiederholen'}),
        )
