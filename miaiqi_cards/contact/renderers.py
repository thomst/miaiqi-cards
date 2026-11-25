import logging
import smtplib
from django.template.loader import render_to_string
from simple_page import renderers
from . import forms
from . import email
from . import models

logger = logging.getLogger(__name__)


@renderers.register(models.ContactSection)
class ContactRenderer(renderers.SectionRenderer):

    class Media:
        css = dict(all=['css/contact.css'])
        js = ['js/contact.js']

    def get_form_html(self, form=None):
        context = dict(contact=self.section, form=form or forms.ContactForm())
        return render_to_string('contact/contact.html', context, self.request)

    def get_confirmation_html(self):
        context = dict(contact=self.section)
        return render_to_string('contact/confirmation.html', context, self.request)

    def submit(self):
        form = forms.ContactForm(self.request.POST)
        if not form.is_valid():
            return self.get_form_html(form)
        try:
            email.send_contact_mail(**form.cleaned_data)
        except (smtplib.SMTPException, OSError):
            logger.exception('Sending the contact mail failed.')
            form.add_error(None, 'Die Nachricht konnte nicht gesendet werden.')
            return self.get_form_html(form)
        return self.get_confirmation_html()

    def get_context_data(self):
        context = super().get_context_data()
        context['contact_html'] = self.get_form_html()
        return context
