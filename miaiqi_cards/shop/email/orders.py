import base64
from io import BytesIO
from pathlib import Path

from cart.cart import Cart
from cart.models import Cart as CartModel
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from miaiqi_cards.shop.invoices.epc_qr import EPCPayment
from miaiqi_cards.shop.invoices.invoices import generate_invoice, invoice_number

CSS_PATH = Path(__file__).parent / 'static' / 'css' / 'order.css'


def epc_qr_data_uri(payment):
    buffer = BytesIO()
    payment.as_qr().save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')


def load_closed_cart(cart_pk):
    # Skips Cart.__init__, which needs a request and session; the pricing methods only use self.cart.
    cart = Cart.__new__(Cart)
    cart.cart = CartModel.objects.get(pk=cart_pk, checked_out=True)
    cart._cache = {}
    return cart


@task
def send_order_email(cart_pk, address, email_address):
    """Send the order details, EPC payment QR code and invoice PDF to the customer."""
    cart = load_closed_cart(cart_pk)
    number = invoice_number(cart)
    qr_data_uri = epc_qr_data_uri(EPCPayment(amount=cart.total(), remittance=number))
    html = render_to_string('email/order.html', {
        'cart': cart,
        'address': address,
        'invoice_number': number,
        'css': CSS_PATH.read_text(encoding='utf-8'),
        'qr_data_uri': qr_data_uri,
        'recipient_name': settings.INVOICE_RECIPIENT_NAME,
        'recipient_iban': settings.INVOICE_RECIPIENT_IBAN,
        'recipient_bic': settings.INVOICE_RECIPIENT_BIC,
    })

    sender = settings.CONTACT_RECIPIENT
    message = EmailMultiAlternatives(
        subject=f'Ihre Bestellung {number}',
        body=strip_tags(html),
        from_email=sender,
        to=[email_address],
        reply_to=[sender],
    )
    message.attach_alternative(html, 'text/html')
    message.attach(f'{number}.pdf', generate_invoice(cart, address), 'application/pdf')
    message.send()
