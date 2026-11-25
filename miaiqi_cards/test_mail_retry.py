import smtplib
from unittest import mock

from django.tasks import task
from django.tasks.backends.immediate import ImmediateBackend
from django.test import SimpleTestCase

from .mail_retry import MAX_ATTEMPTS, retry_on_temporary_error

ERRORS = dict(
    disconnected=smtplib.SMTPServerDisconnected('gone'),
    temporary=smtplib.SMTPResponseException(451, 'try later'),
    permanent=smtplib.SMTPResponseException(550, 'rejected'),
    other=ValueError('bug'),
)
calls = []


@task(takes_context=True)
@retry_on_temporary_error
def flaky(failures, error):
    calls.append(1)
    if len(calls) <= failures:
        raise ERRORS[error]


@mock.patch.object(ImmediateBackend, 'supports_defer', True)
class RetryOnTemporaryErrorTests(SimpleTestCase):
    def setUp(self):
        calls.clear()

    def test_temporary_error_is_retried_until_it_succeeds(self):
        result = flaky.enqueue(2, 'disconnected')
        self.assertEqual(len(calls), 3)
        self.assertEqual(result.status.name, 'SUCCESSFUL')

    def test_temporary_smtp_reply_is_retried(self):
        with self.assertLogs('miaiqi_cards.mail_retry', level='WARNING') as logs:
            flaky.enqueue(1, 'temporary')
        self.assertEqual(len(calls), 2)
        self.assertIn('retrying', logs.output[0])

    def test_gives_up_after_max_attempts(self):
        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR') as logs:
            flaky.enqueue(100, 'disconnected')
        self.assertEqual(len(calls), MAX_ATTEMPTS)
        self.assertIn('giving up', logs.output[0])

    def test_permanent_smtp_reply_is_not_retried(self):
        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR'):
            result = flaky.enqueue(100, 'permanent')
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status.name, 'FAILED')

    def test_other_errors_are_not_retried(self):
        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR'):
            flaky.enqueue(100, 'other')
        self.assertEqual(len(calls), 1)


class WithoutDeferSupportTests(SimpleTestCase):
    def test_error_is_raised_when_the_backend_cannot_delay(self):
        calls.clear()
        with self.assertLogs('miaiqi_cards.mail_retry', level='ERROR'):
            result = flaky.enqueue(100, 'disconnected')
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status.name, 'FAILED')
