from unittest.mock import patch

from cart.cart import Cart
from django.test import RequestFactory, TestCase, override_settings

from miaiqi_cards.postcards.models import Postcard
from miaiqi_cards.shop.forms import AddressForm
from miaiqi_cards.shop.models import Product
from .invoices import generate_invoice
from .models import InvoiceNumber


class InvoiceNumberTests(TestCase):
    def create_cart(self):
        request = RequestFactory().get('/')
        request.session = {}
        return Cart(request)

    def test_numbers_are_consecutive_for_different_carts(self):
        first = InvoiceNumber.get_invoice_number(self.create_cart())
        second = InvoiceNumber.get_invoice_number(self.create_cart())
        self.assertEqual(second, first + 1)

    def test_the_same_cart_keeps_its_number(self):
        cart = self.create_cart()
        first = InvoiceNumber.get_invoice_number(cart)
        again = InvoiceNumber.get_invoice_number(cart)
        self.assertEqual(first, again)
        self.assertEqual(InvoiceNumber.objects.count(), 1)

    def test_numbers_start_at_one_each_year(self):
        InvoiceNumber.objects.create(cart_id=1000, year=2000, number=7)
        self.assertEqual(InvoiceNumber.get_invoice_number(self.create_cart()), 1)
        with patch('miaiqi_cards.shop.invoices.models.date') as mock_date:
            mock_date.today.return_value.year = 2000
            self.assertEqual(InvoiceNumber.get_invoice_number(self.create_cart()), 8)


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

    @override_settings(
        INVOICE_RECIPIENT_NAME='Miaiqi Cards',
        INVOICE_RECIPIENT_IBAN='DE123',
        INVOICE_RECIPIENT_BIC='TESTDEFF',
        INVOICE_NUMBER_PATTERN='TEST-{number:0>5}',
    )
    def test_generate_invoice_returns_pdf_for_checked_out_cart(self):
        cart = self.create_cart()
        cart.checkout()

        pdf = generate_invoice(cart, self.create_address())

        self.assertTrue(pdf.startswith(b'%PDF-'))

    @override_settings(
        INVOICE_RECIPIENT_NAME='Miaiqi Cards',
        INVOICE_RECIPIENT_IBAN='DE123',
        INVOICE_RECIPIENT_BIC='TESTDEFF',
        INVOICE_NUMBER_PATTERN='TEST-{number:0>5}',
    )
    @patch('miaiqi_cards.shop.invoices.invoices.HTML')
    def test_invoice_template_includes_order_and_address_data(self, html_class):
        cart = self.create_cart()
        cart.checkout()

        generate_invoice(cart, self.create_address())

        rendered_html = html_class.call_args.kwargs['string']
        self.assertIn('TEST-00001', rendered_html)
        self.assertIn('Miaiqi Cards', rendered_html)
        self.assertIn('DE123', rendered_html)
        self.assertIn('Test Customer', rendered_html)
        self.assertIn('Postcard Street 1', rendered_html)
        self.assertIn('10115 Berlin', rendered_html)
        self.assertIn('Invoice test postcard', rendered_html)

    def test_generate_invoice_rejects_an_open_cart(self):
        cart = self.create_cart()

        with self.assertRaises(ValueError):
            generate_invoice(cart, {})
