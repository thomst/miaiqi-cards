from django.core.mail import EmailMessage
from django.tasks import task


@task
def send_email(subject, body, from_email, to, reply_to=None, cc=None, bcc=None):
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
    )
    message.send()
