from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

from .models import InvoiceNumber

PACKAGE_DIR = Path(__file__).parent


def generate_invoice(order):
    """Return PDF bytes for a checked-out order."""
    html = render_to_string('invoices/invoice.html', {
        'invoice_number': InvoiceNumber.get_invoice_number(order.cart_id),
        'invoice_date': date.today(),
        'recipient_name': settings.INVOICE_RECIPIENT_NAME,
        'recipient_iban': settings.INVOICE_RECIPIENT_IBAN,
        'recipient_bic': settings.INVOICE_RECIPIENT_BIC,
        'address': order,
        'items': order.cart_data['items'],
        'subtotal': order.cart_data['summary'],
        'discount': order.cart_data['discount_amount'],
        'tax': order.cart_data['tax'],
        'shipping': order.cart_data['shipping'],
        'total': order.cart_data['total'],
    })

    css_path = PACKAGE_DIR / 'static' / 'css' / 'invoice.css'
    return HTML(string=html).write_pdf(stylesheets=[CSS(filename=str(css_path))])
