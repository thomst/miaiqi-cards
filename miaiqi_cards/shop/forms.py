from django import forms


class AddressForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Vorname'}),
        )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Nachname'}),
        )
    street = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Straße und Hausnummer'}),
        )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Stadt'}),
        )
    postal_code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Postleitzahl'}),
        )

    @property
    def name_fields(self):
        return [self['first_name'], self['last_name']]

    @property
    def address_fields(self):
        return [self['street'], self['city'], self['postal_code']]


class LegalForm(forms.Form):
    ts_and_cs_confirmation = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label='Ich stimme den AGBs zu.',
        )
    cancellation_confirmation = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label='Ich habe die Widerrufsbelehrung zur Kenntnis genommen.',
        )


class EmailForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse'}),
        )
    repeated_email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email Adresse wiederholen'}),
        )

    def clean_repeated_email_address(self):
        repeated_email = self.cleaned_data['repeated_email_address']
        email = self.cleaned_data.get('email_address')
        if email and repeated_email != email:
            raise forms.ValidationError('Die E-Mail-Adressen stimmen nicht überein.')
        return repeated_email
