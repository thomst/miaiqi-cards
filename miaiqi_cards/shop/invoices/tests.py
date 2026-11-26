from unittest.mock import patch

from cart.cart import Cart
from django.test import RequestFactory, TestCase, override_settings

from miaiqi_cards.postcards.models import Postcard
from miaiqi_cards.shop.forms import AddressForm
from miaiqi_cards.shop.models import Product
from miaiqi_cards.shop.order.models import Order
from miaiqi_cards.shop.order.orders import serialize_cart
from .invoices import generate_invoice
from .models import InvoiceNumber


@override_settings(INVOICE_NUMBER_PATTERN='TEST-{year}-{number:0>5}')
class InvoiceNumberTests(TestCase):
    def create_cart(self):
        request = RequestFactory().get('/')
        request.session = {}
        return Cart(request)

    def test_numbers_are_consecutive_for_different_carts(self):
        with patch('miaiqi_cards.shop.invoices.models.date') as mock_date:
            mock_date.today.return_value.year = 2026
            first = InvoiceNumber.get_invoice_number(self.create_cart().cart.pk)
            second = InvoiceNumber.get_invoice_number(self.create_cart().cart.pk)
        self.assertEqual(first, 'TEST-2026-00001')
        self.assertEqual(second, 'TEST-2026-00002')

    def test_the_same_cart_keeps_its_number(self):
        cart = self.create_cart()
        first = InvoiceNumber.get_invoice_number(cart.cart.pk)
        again = InvoiceNumber.get_invoice_number(cart.cart.pk)
        self.assertEqual(first, again)
        self.assertEqual(InvoiceNumber.objects.count(), 1)

    def test_numbers_start_at_one_each_year(self):
        InvoiceNumber.objects.create(cart_id=1000, year=2000, number=7)
        with patch('miaiqi_cards.shop.invoices.models.date') as mock_date:
            mock_date.today.return_value.year = 2001
            self.assertEqual(InvoiceNumber.get_invoice_number(self.create_cart().cart.pk), 'TEST-2001-00001')
            mock_date.today.return_value.year = 2000
            self.assertEqual(InvoiceNumber.get_invoice_number(self.create_cart().cart.pk), 'TEST-2000-00008')

    def test_existing_cart_keeps_its_year_after_new_year(self):
        cart = self.create_cart()
        with patch('miaiqi_cards.shop.invoices.models.date') as mock_date:
            mock_date.today.return_value.year = 2026
            first = InvoiceNumber.get_invoice_number(cart.cart.pk)
            mock_date.today.return_value.year = 2027
            again = InvoiceNumber.get_invoice_number(cart.cart.pk)
        self.assertEqual(first, 'TEST-2026-00001')
        self.assertEqual(again, first)


class InvoiceTests(TestCase):
    def create_cart(self):
        request = RequestFactory().get('/')
        request.session = {}
        cart = Cart(request)
        postcard = Postcard.objects.create(title='Invoice test postcard')
        product = Product.objects.get_from_content(postcard)
        cart.add(product, unit_price=product.price, quantity=2)
        return cart

    def create_address(self):
        address_form = AddressForm({
            'first_name': 'Test',
            'last_name': 'Customer',
            'street': 'Postcard Street 1',
            'city': 'Berlin',
            'postal_code': '10115',
        })
        self.assertTrue(address_form.is_valid())
        return address_form.cleaned_data

    def create_order(self):
        cart = self.create_cart()
        cart.checkout()
        return Order.objects.create(
            cart_id=cart.cart.pk,
            cart_data=serialize_cart(cart),
            email_address='customer@example.com',
            **self.create_address(),
        )

    @override_settings(
        INVOICE_RECIPIENT_NAME='Miaiqi Cards',
        INVOICE_RECIPIENT_IBAN='DE123',
        INVOICE_RECIPIENT_BIC='TESTDEFF',
        INVOICE_NUMBER_PATTERN='TEST-{year}-{number:0>5}',
    )
    def test_generate_invoice_returns_pdf_for_order(self):
        pdf = generate_invoice(self.create_order())

        self.assertTrue(pdf.startswith(b'%PDF-'))

    @override_settings(
        INVOICE_RECIPIENT_NAME='Miaiqi Cards',
        INVOICE_RECIPIENT_IBAN='DE123',
        INVOICE_RECIPIENT_BIC='TESTDEFF',
        INVOICE_NUMBER_PATTERN='TEST-{year}-{number:0>5}',
    )
    @patch('miaiqi_cards.shop.invoices.invoices.HTML')
    def test_invoice_template_includes_order_and_address_data(self, html_class):
        order = self.create_order()
        Postcard.objects.filter(title='Invoice test postcard').update(title='Renamed postcard')

        with patch('miaiqi_cards.shop.invoices.models.date') as mock_date:
            mock_date.today.return_value.year = 2026
            generate_invoice(order)

        rendered_html = html_class.call_args.kwargs['string']
        self.assertIn('TEST-2026-00001', rendered_html)
        self.assertIn('Miaiqi Cards', rendered_html)
        self.assertIn('DE123', rendered_html)
        self.assertIn('Test Customer', rendered_html)
        self.assertIn('Postcard Street 1', rendered_html)
        self.assertIn('10115 Berlin', rendered_html)
        self.assertIn('Invoice test postcard', rendered_html)
        self.assertNotIn('Renamed postcard', rendered_html)
        self.assertNotIn('Rabatt', rendered_html)
        self.assertNotIn('Steuer', rendered_html)

    @patch('miaiqi_cards.shop.invoices.invoices.HTML')
    def test_invoice_template_includes_nonzero_discount_and_tax(self, html_class):
        order = self.create_order()
        order.cart_data['discount_amount'] = '1.25'
        order.cart_data['tax'] = '0.45'

        generate_invoice(order)

        rendered_html = html_class.call_args.kwargs['string']
        self.assertIn('Rabatt', rendered_html)
        self.assertIn('Steuer', rendered_html)
