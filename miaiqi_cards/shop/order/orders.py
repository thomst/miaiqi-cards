import base64
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from miaiqi_cards.mail_retry import retry_on_temporary_error
from miaiqi_cards.shop.invoices.epc_qr import EPCPayment
from miaiqi_cards.shop.invoices.invoices import generate_invoice
from miaiqi_cards.shop.invoices.models import InvoiceNumber
from .models import Order

CSS_PATH = Path(__file__).parent / 'static' / 'css' / 'order.css'


def serialize_cart(cart):
    return {
        'items': [{
            'product': str(item.product),
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'total_price': str(item.total_price),
        } for item in cart],
        'summary': str(cart.summary()),
        'discount_amount': str(cart.discount_amount()),
        'tax': str(cart.tax()),
        'shipping': str(cart.shipping()),
        'total': str(cart.total()),
    }


def epc_qr_data_uri(payment):
    buffer = BytesIO()
    payment.as_qr().save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')


def generate_email_content(order, number, qr_data_uri):
    cart = {
        **order.cart_data,
        'discount_amount': Decimal(order.cart_data['discount_amount']),
        'tax': Decimal(order.cart_data['tax']),
    }
    return render_to_string('order/order.html', {
        'cart': cart,
        'address': order,
        'invoice_number': number,
        'css': CSS_PATH.read_text(encoding='utf-8'),
        'qr_data_uri': qr_data_uri,
        'recipient_name': settings.INVOICE_RECIPIENT_NAME,
        'recipient_iban': settings.INVOICE_RECIPIENT_IBAN,
        'recipient_bic': settings.INVOICE_RECIPIENT_BIC,
    })


@task(takes_context=True)
@retry_on_temporary_error
def send_order_email(order_id):
    """Send the order details, EPC payment QR code and invoice PDF to the customer."""
    order = Order.objects.get(pk=order_id)
    number = InvoiceNumber.get_invoice_number(order.cart_id)
    qr_data_uri = epc_qr_data_uri(EPCPayment(amount=Decimal(order.cart_data['total']), remittance=number))
    html = generate_email_content(order, number, qr_data_uri)

    sender = settings.INVOICE_RECIPIENT_ADDRESS
    message = EmailMultiAlternatives(
        subject=f'Ihre Bestellung {number}',
        body=strip_tags(html),
        from_email=sender,
        to=[order.email_address],
        bcc=[sender, settings.INVOICE_UPLOAD_ADDRESS],
        reply_to=[sender],
    )
    message.attach_alternative(html, 'text/html')
    message.attach(f'{number}.pdf', generate_invoice(order), 'application/pdf')
    message.send()
