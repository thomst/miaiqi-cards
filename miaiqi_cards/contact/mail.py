from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, get_connection


def get_connection_from_settings():
    """
    Return a connection for the satellite account configured in the settings.
    It is independent of django's default EMAIL_* settings.
    """
    return get_connection(
        backend=settings.CONTACT_EMAIL_BACKEND,
        host=settings.CONTACT_EMAIL_HOST,
        port=settings.CONTACT_EMAIL_PORT,
        username=settings.CONTACT_EMAIL_HOST_USER,
        password=settings.CONTACT_EMAIL_HOST_PASSWORD,
        use_tls=settings.CONTACT_EMAIL_USE_TLS,
        use_ssl=settings.CONTACT_EMAIL_USE_SSL,
    )


def send_contact_mail(email_address, subject, body):
    """
    Send the contact message to the configured recipient, using the
    visitor's email address as sender.
    """
    if not settings.CONTACT_RECIPIENT:
        raise ImproperlyConfigured('The CONTACT_RECIPIENT setting is empty.')
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=email_address,
        to=[settings.CONTACT_RECIPIENT],
        reply_to=[email_address],
        connection=get_connection_from_settings(),
    )
    message.send()
