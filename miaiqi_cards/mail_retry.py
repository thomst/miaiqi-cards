import functools
import logging
import smtplib
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 5


def is_temporary(error):
    if isinstance(error, smtplib.SMTPResponseException):
        # 4xx replies mean "try again later", 5xx are permanent.
        return 400 <= error.smtp_code < 500
    return isinstance(error, (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, OSError))


def retry_on_temporary_error(func):
    """
    Re-enqueue an e-mail task with an exponential delay (2, 4, 8, ... minutes)
    if sending failed with a temporary error. Permanent errors and the error of
    the last attempt are raised as usual.

    Use it below a task that takes the context:

        @task(takes_context=True)
        @retry_on_temporary_error
        def send_something(...):

    The attempt number is passed to the task as the keyword argument 'attempt'.
    """
    @functools.wraps(func)
    def wrapper(context, *args, attempt=1, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            task = context.task_result.task
            # Only a backend with deferred execution can delay the next attempt.
            if (
                not is_temporary(error)
                or attempt >= MAX_ATTEMPTS
                or not task.get_backend().supports_defer
            ):
                # The arguments are not logged: they contain personal data.
                logger.exception('Task %s failed on attempt %s, giving up.', task.name, attempt)
                raise
            delay = timedelta(minutes=2 ** attempt)
            logger.warning(
                'Task %s failed on attempt %s with a temporary error (%r), retrying in %s.',
                task.name, attempt, error, delay,
            )
            task.using(run_after=timezone.now() + delay).enqueue(*args, attempt=attempt + 1, **kwargs)

    # Django inspects the signature for 'context'; hide the wrapped function.
    del wrapper.__wrapped__
    return wrapper
