from django import forms


class ContactForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Deine Email Adresse'}),
        )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Betreff'}),
        )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Nachricht', 'rows': 8}),
        )

    def clean_subject(self):
        # Line breaks in the subject would allow mail header injection.
        subject = self.cleaned_data['subject']
        if '\n' in subject or '\r' in subject:
            raise forms.ValidationError('Line breaks are not allowed.')
        return subject
