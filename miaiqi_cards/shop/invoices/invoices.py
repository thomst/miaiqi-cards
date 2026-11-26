from datetime import date
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

PACKAGE_DIR = Path(__file__).parent


def generate_invoice(order):
    """Return PDF bytes for a checked-out order."""
    html = render_to_string('invoices/invoice.html', {
        'invoice_number': order.invoice_number,
        'invoice_date': date.today(),
        'recipient_name': settings.INVOICE_RECIPIENT_NAME,
        'recipient_iban': settings.INVOICE_RECIPIENT_IBAN,
        'recipient_bic': settings.INVOICE_RECIPIENT_BIC,
        'address': order,
        'cart': order.cart_data,
    })

    css_path = PACKAGE_DIR / 'static' / 'css' / 'invoice.css'
    return HTML(string=html).write_pdf(stylesheets=[CSS(filename=str(css_path))])
