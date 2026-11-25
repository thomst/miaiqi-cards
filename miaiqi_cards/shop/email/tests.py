from unittest.mock import patch

from cart.cart import Cart
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings

from miaiqi_cards.postcards.models import Postcard
from miaiqi_cards.shop.forms import AddressForm
from miaiqi_cards.shop.models import Product
from .orders import send_order_email


@override_settings(
    INVOICE_NUMBER_PATTERN='TEST-{year}-{number:0>5}',
    INVOICE_RECIPIENT_ADDRESS='info@example.com',
    INVOICE_UPLOAD_ADDRESS='upload@example.com',
)
class OrderEmailTests(TestCase):
    def setUp(self):
        date_patch = patch('miaiqi_cards.shop.invoices.models.date')
        self.addCleanup(date_patch.stop)
        date_patch.start().today.return_value.year = 2026
        request = RequestFactory().get('/')
        request.session = {}
        self.cart = Cart(request)
        postcard = Postcard.objects.create(title='Order mail postcard')
        product = Product.objects.get_from_content(postcard)
        self.cart.add(product, unit_price=product.price, quantity=2)
        self.cart.checkout()
        address_form = AddressForm({
            'first_name': 'Test',
            'last_name': 'Customer',
            'street': 'Postcard Street 1',
            'city': 'Berlin',
            'postal_code': '10115',
        })
        self.assertTrue(address_form.is_valid())
        self.address = address_form.cleaned_data

    def test_html_body_contains_order_details_and_qr_code(self):
        send_order_email.enqueue(self.cart.cart.pk, self.address, 'customer@example.com')

        message = mail.outbox[0]
        self.assertEqual(message.to, ['customer@example.com'])
        html, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, 'text/html')
        self.assertIn('Order mail postcard', html)
        number = 'TEST-2026-00001'
        self.assertEqual(message.subject, f'Ihre Bestellung {number}')
        self.assertIn(number, html)
        self.assertIn('Postcard Street 1', html)
        self.assertIn('data:image/png;base64,', html)

    def test_invoice_pdf_is_attached(self):
        send_order_email.enqueue(self.cart.cart.pk, self.address, 'customer@example.com')

        filename, content, mimetype = mail.outbox[0].attachments[0]
        self.assertEqual(filename, 'TEST-2026-00001.pdf')
        self.assertEqual(mimetype, 'application/pdf')
        self.assertTrue(content.startswith(b'%PDF-'))
