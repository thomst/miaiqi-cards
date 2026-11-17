from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage


def send_contact_mail(email_address, subject, body):
    """
    Send the contact message to the configured recipient, using the
    visitor's email address as sender. The mail is sent with django's
    standard EMAIL_* settings.
    """
    if not settings.CONTACT_RECIPIENT:
        raise ImproperlyConfigured('The CONTACT_RECIPIENT setting is empty.')
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=email_address,
        to=[settings.CONTACT_RECIPIENT],
        reply_to=[email_address],
    )
    message.send()
