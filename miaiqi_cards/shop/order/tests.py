import json
from decimal import Decimal
from unittest.mock import patch

from cart.cart import Cart
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings

from miaiqi_cards.postcards.models import Postcard
from miaiqi_cards.shop.forms import AddressForm
from miaiqi_cards.shop.invoices.invoices import generate_invoice
from miaiqi_cards.shop.models import Product
from .models import Order
from .orders import epc_qr_data_uri, generate_email_content, send_order_email, serialize_cart


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
        self.order = Order.objects.create(
            cart_id=self.cart.cart.pk,
            cart_data=serialize_cart(self.cart),
            email_address='customer@example.com',
            **address_form.cleaned_data,
        )

    def test_cart_snapshot_is_json_safe_and_preserves_order_values(self):
        snapshot = json.loads(json.dumps(serialize_cart(self.cart)))
        self.assertEqual(snapshot['items'], [{
            'product': 'Order mail postcard',
            'quantity': 2,
            'unit_price': '2.50',
            'total_price': '5.00',
        }])
        for field, value in {
            'summary': '5.00',
            'discount_amount': '0.00',
            'tax': '0.00',
            'shipping': '2.00',
            'total': '7.00',
        }.items():
            self.assertIsInstance(snapshot[field], str)
            self.assertEqual(Decimal(snapshot[field]), Decimal(value))

        postcard = Postcard.objects.get(title='Order mail postcard')
        postcard.title = 'Renamed postcard'
        postcard.save()
        self.assertEqual(Order.objects.get(pk=self.order.pk).cart_data, snapshot)

    def test_cart_snapshot_includes_discount_and_tax(self):
        with (
            patch.object(self.cart, 'discount_amount', return_value=Decimal('1.25')),
            patch.object(self.cart, 'tax', return_value=Decimal('0.45')),
        ):
            snapshot = serialize_cart(self.cart)

        self.assertEqual(snapshot['discount_amount'], '1.25')
        self.assertEqual(snapshot['tax'], '0.45')

    @patch('miaiqi_cards.shop.order.orders.epc_qr_data_uri', wraps=epc_qr_data_uri)
    def test_html_body_contains_order_details_and_qr_code(self, qr_generator):
        Order.objects.filter(pk=self.order.pk).update(
            street='Updated Street 2',
            email_address='updated@example.com',
        )
        send_order_email.enqueue(self.order.pk)

        message = mail.outbox[0]
        self.assertEqual(message.to, ['updated@example.com'])
        html, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, 'text/html')
        self.assertIn('Order mail postcard', html)
        self.assertIn('<td>2</td>', html)
        number = 'TEST-2026-00001'
        self.assertEqual(message.subject, f'Ihre Bestellung {number}')
        self.assertIn(number, html)
        self.assertIn('Updated Street 2', html)
        self.assertIn('data:image/png;base64,', html)
        self.assertNotIn('Rabatt', html)
        self.assertNotIn('Steuer', html)
        payload = qr_generator.call_args.args[0].as_payload()
        self.assertIn('EUR7.00', payload)
        self.assertIn(number, payload)

    def test_email_includes_nonzero_discount_and_tax(self):
        self.order.cart_data['discount_amount'] = '1.25'
        self.order.cart_data['tax'] = '0.45'

        html = generate_email_content(self.order, 'TEST-2026-00001', 'qr')

        self.assertIn('Rabatt', html)
        self.assertIn('Steuer', html)

    @patch('miaiqi_cards.shop.order.orders.generate_invoice', wraps=generate_invoice)
    def test_invoice_pdf_is_attached(self, invoice_generator):
        send_order_email.enqueue(self.order.pk)

        filename, content, mimetype = mail.outbox[0].attachments[0]
        self.assertEqual(filename, 'TEST-2026-00001.pdf')
        self.assertEqual(mimetype, 'application/pdf')
        self.assertTrue(content.startswith(b'%PDF-'))
        self.assertEqual(invoice_generator.call_args.args[0], self.order)
