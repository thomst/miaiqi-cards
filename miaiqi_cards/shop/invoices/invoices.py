from datetime import date
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

from miaiqi_cards.shop.models import InvoiceNumber

PACKAGE_DIR = Path(__file__).parent


def invoice_number(cart):
    pattern = settings.INVOICE_NUMBER_PATTERN
    return pattern.format(number=InvoiceNumber.get_invoice_number(cart))


def generate_invoice(cart, address):
    """Return PDF bytes for a checked-out cart."""
    if not cart.cart.checked_out:
        raise ValueError('An invoice can only be generated for a checked-out cart.')

    html = render_to_string('invoices/invoice.html', {
        'invoice_number': invoice_number(cart),
        'invoice_date': date.today(),
        'recipient_name': settings.INVOICE_RECIPIENT_NAME,
        'recipient_iban': settings.INVOICE_RECIPIENT_IBAN,
        'recipient_bic': settings.INVOICE_RECIPIENT_BIC,
        'address': address,
        'items': [{
            'product': item.product,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total_price': item.total_price,
        } for item in cart],
        'subtotal': cart.summary(),
        'discount': cart.discount_amount(),
        'tax': cart.tax(),
        'shipping': cart.shipping(),
        'total': cart.total(),
    })

    css_path = PACKAGE_DIR / 'static' / 'css' / 'invoice.css'
    return HTML(string=html).write_pdf(stylesheets=[CSS(filename=str(css_path))])