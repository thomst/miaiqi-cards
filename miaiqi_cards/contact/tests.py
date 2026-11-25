from unittest.mock import patch

from django.core import mail
from django.tasks.base import TaskResultStatus
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from simple_page import renderers
from . import forms
from . import models
from .email import send_contact_mail
from .renderers import ContactRenderer

DATA = dict(email_address='visitor@example.com', subject='Hello', body='A message.')


@override_settings(
    CONTACT_RECIPIENT='owner@example.com',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class ContactTests(TestCase):
    def setUp(self):
        self.section = models.ContactSection.objects.create(
            title='Contact',
            confirmation_text='Thank you!',
        )
        self.url = reverse('contact-submit', args=[self.section.id])

    def test_form_rejects_line_break_in_subject(self):
        form = forms.ContactForm(dict(DATA, subject='Hello\nBcc: a@example.com'))
        self.assertIn('subject', form.errors)

    def test_submit_sends_mail_with_visitor_as_sender(self):
        response = self.client.post(self.url, DATA)
        self.assertContains(response, 'Thank you!')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.from_email, 'visitor@example.com')
        self.assertEqual(message.to, ['owner@example.com'])
        self.assertEqual(message.reply_to, ['visitor@example.com'])
        self.assertEqual(message.subject, 'Hello')
        self.assertEqual(message.body, 'A message.')

    def test_invalid_submit_redisplays_form_with_errors(self):
        response = self.client.post(self.url, dict(DATA, email_address='nope'))
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, 'class="error"')

    @patch('django.core.mail.EmailMessage.send', side_effect=ConnectionRefusedError('connection refused'))
    def test_send_failure_is_logged_by_task(self, send):
        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR') as logs:
            result = send_contact_mail.enqueue(**DATA)
        self.assertEqual(result.status, TaskResultStatus.FAILED)
        self.assertIn('send_contact_mail', logs.output[0])

        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR'):
            response = self.client.post(self.url, DATA)
        self.assertContains(response, 'Thank you!')

    @patch('miaiqi_cards.contact.renderers.email.send_contact_mail')
    def test_enqueue_failure_shows_error(self, task):
        task.enqueue.side_effect = OSError('queue unavailable')
        with self.assertLogs('miaiqi_cards.contact.renderers', level='ERROR'):
            response = self.client.post(self.url, DATA)
        self.assertContains(response, 'konnte nicht gesendet werden')

    def test_submit_requires_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_form_view_renders_form(self):
        response = self.client.get(reverse('contact-form', args=[self.section.id]))
        self.assertContains(response, 'name="body"')

    def test_registered_renderer_renders_section(self):
        request = RequestFactory().get('/')
        renderer_cls = renderers.get_renderer(self.section)
        self.assertIs(renderer_cls, ContactRenderer)
        renderer = renderer_cls(self.section, None, None, request)
        html = renderer.render()
        self.assertIn('<h2>Contact</h2>', html)
        self.assertIn('<div class="contact">', html)
        self.assertIn('contact.css', str(renderer.media))
        self.assertIn('contact.js', str(renderer.media))
