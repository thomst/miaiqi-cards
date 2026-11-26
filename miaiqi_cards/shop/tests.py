import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.http import QueryDict
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from cart.cart import Cart, CartException, InvalidDiscountError, MinimumOrderNotMet
from cart.models import Cart as CartModel
from .forms import AddressForm, EmailForm, LegalForm
from miaiqi_cards.postcards.models import GallerySection, Postcard, PostcardSet, PostcardSetPostcard, SetsSection
from miaiqi_cards.website.models import MiaiqiCardsPage
from simple_page.models import PageSection
from .models import Product, ShopSection
from .order.models import Order
from .renderers import ShopRenderer
from .views import confirmation_view, description_view, update_product


class OrderTests(TestCase):
    def test_order_stores_address_and_email(self):
        address = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'street': 'Postcard Street 1',
            'city': 'Berlin',
            'postal_code': '01234',
        }
        order = Order.objects.create(
            cart_id=1,
            cart_data={'items': [], 'total': '0.00'},
            invoice_number='TEST-00001',
            email_address='customer@example.com',
            **address,
        )

        stored = Order.objects.get(pk=order.pk)
        self.assertEqual(stored.cart_id, 1)
        self.assertEqual(stored.cart_data, {'items': [], 'total': '0.00'})
        self.assertEqual(stored.invoice_number, 'TEST-00001')
        self.assertEqual(stored.email_address, 'customer@example.com')
        for field, value in address.items():
            self.assertEqual(getattr(stored, field), value)


class ProductTest(TestCase):
    def product_for(self, instance):
        return Product.objects.get_from_content(instance)

    def test_get_from_content_returns_the_product_of_a_postcard_or_set(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')

        self.assertEqual(Product.objects.get_from_content(postcard).content, postcard)
        self.assertEqual(Product.objects.get_from_content(postcard_set).content, postcard_set)

    def test_get_from_content_raises_without_a_product(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        Product.objects.all().delete()

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get_from_content(postcard)

    def test_saving_postcard_and_set_creates_products(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(
            title='Test Set',
            slug='test-set',
        )

        postcard_product = self.product_for(postcard)
        postcard_set_product = self.product_for(postcard_set)

        self.assertEqual(postcard_product.content, postcard)
        self.assertEqual(postcard_set_product.content, postcard_set)

        postcard.save()
        postcard_set.save()

        self.assertEqual(Product.objects.count(), 2)

    def test_only_one_product_can_point_to_each_object(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        product = self.product_for(postcard)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(
                content_type=product.content_type,
                object_id=product.object_id,
            )

    def test_deleting_postcard_or_set_deletes_its_product(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')

        postcard.delete()
        postcard_set.delete()

        self.assertFalse(Product.objects.exists())


class ShopStepsTests(TestCase):
    def setUp(self):
        self.shop = ShopSection.objects.create(
            title='Test Shop',
            description_text='All about **cards**',
            terms_and_conditions='legal_documents/terms.pdf',
            cancellation_policy='legal_documents/cancellation.pdf',
        )

    def request(self, session=None):
        request = RequestFactory().get('/')
        request.session = {} if session is None else session
        return request

    def test_description_is_the_initial_step(self):
        html = ShopRenderer(self.shop, self.request()).get_html()

        self.assertIn('<strong>cards</strong>', html)
        self.assertIn(f'data-url="/shop/{self.shop.pk}/order/"', html)
        self.assertNotIn('data-method="post"', html)
        self.assertNotIn('form-TOTAL_FORMS', html)

    def test_get_html_continues_with_the_step_stored_in_the_session(self):
        session = {'shop-state': ShopRenderer.ORDER_STATE}

        html = ShopRenderer(self.shop, self.request(session)).get_html()

        self.assertIn('Choose your postcards above...', html)

    def test_description_view_returns_the_description_and_stores_the_state(self):
        request = self.request()

        response = description_view(request, shop_id=self.shop.pk)

        self.assertContains(response, 'All about')
        self.assertEqual(request.session['shop-state'], ShopRenderer.DESCRIPTION_STATE)

    def test_every_step_names_itself_for_the_widgets(self):
        renderer = ShopRenderer(self.shop, self.request())

        for step, html in [
            ('description', renderer.get_description_html()),
            ('order', renderer.get_order_html()),
            ('cart', renderer.get_cart_html()),
            ('checkout', renderer.get_checkout_html()),
            ('confirmation', renderer.get_confirmation_html()),
        ]:
            self.assertIn(f'<div class="shop" data-step="{step}">', html)

    def test_checkout_renders_labels_for_legal_checkboxes(self):
        html = ShopRenderer(self.shop, self.request()).get_checkout_html()

        for field in LegalForm():
            self.assertIn(f'name="{field.name}"', html)
            self.assertIn(f'<label for="{field.id_for_label}">', html)
        self.assertIn(f'href="{self.shop.terms_and_conditions.url}"', html)
        self.assertIn(f'href="{self.shop.cancellation_policy.url}"', html)

    def test_cart_shows_shipping_for_a_nonempty_cart(self):
        request = self.request()
        cart = Cart(request)
        self.assertEqual(cart.shipping(), Decimal('0.00'))

        product = Product.objects.get_from_content(Postcard.objects.create(title='Test Postcard'))
        cart.add(product, unit_price=product.price)
        self.assertEqual(cart.shipping(), Decimal('2.00'))
        self.assertEqual(cart.total(), product.price + Decimal('2.00'))

        html = ShopRenderer(self.shop, request).get_cart_html()
        self.assertIn('<div>Shipping</div><div>2.00 €</div>', html)

    def test_order_step_has_back_and_cart_buttons(self):
        html = ShopRenderer(self.shop, self.request()).get_order_html()

        back = html[html.index('value="Zurück"'):]
        self.assertIn(f'data-url="/shop/{self.shop.pk}/description/"', back.split('>')[0])
        self.assertNotIn('data-method="post"', back.split('>')[0])
        cart_button = html[html.index('value="Weiter"'):]
        self.assertIn(f'data-url="/shop/{self.shop.pk}/cart/"', cart_button.split('>')[0])
        self.assertNotIn('data-method="post"', cart_button.split('>')[0])

    def test_cart_button_tracks_cart_contents(self):
        request = self.request()
        product = Product.objects.get_from_content(Postcard.objects.create(title='Test Postcard'))

        def cart_button(html):
            return html[html.index('value="Weiter"'):].split('>')[0]

        html = ShopRenderer(self.shop, request).get_order_html()
        self.assertIn('disabled', cart_button(html))

        request.GET = QueryDict('quantity=1')
        html = json.loads(update_product(request, self.shop.pk, product.pk).content)['html']
        self.assertNotIn('disabled', cart_button(html))

        request.GET = QueryDict('quantity=0')
        html = json.loads(update_product(request, self.shop.pk, product.pk).content)['html']
        self.assertIn('disabled', cart_button(html))

    def test_delete_url_uses_product_id_not_cart_item_id(self):
        Product.objects.get_from_content(Postcard.objects.create(title='Unused'))
        product = Product.objects.get_from_content(Postcard.objects.create(title='In cart'))
        request = self.request()
        cart = Cart(request)
        cart.add(product, unit_price=product.price)
        item = next(iter(cart))
        self.assertNotEqual(item.pk, product.pk)

        html = ShopRenderer(self.shop, request).get_order_html()

        self.assertIn(f'data-url="/shop/{self.shop.pk}/update-product/{product.pk}/"', html)

    def test_confirmation_leads_back_to_the_description(self):
        html = ShopRenderer(self.shop, self.request()).get_confirmation_html()

        self.assertIn(f'data-url="/shop/{self.shop.pk}/description/"', html)
        self.assertIn('value="Neue Bestellung"', html)


class ShopCartSessionTests(TestCase):
    def create_checkout(self):
        shop = ShopSection.objects.create(title='Test Shop')
        postcard = Postcard.objects.create(title='Test Postcard')
        product = Product.objects.get(
            content_type=ContentType.objects.get_for_model(postcard),
            object_id=postcard.pk,
        )

        session = {}
        request = RequestFactory().post(
            '/shop/',
            {
                'first_name': 'Test',
                'last_name': 'Customer',
                'street': 'Test Street 1',
                'city': 'Test City',
                'postal_code': '12345',
                'email_address': 'test@example.com',
                'repeated_email_address': 'test@example.com',
                'ts_and_cs_confirmation': 'on',
                'cancellation_confirmation': 'on',
            },
        )
        request.session = session
        cart = Cart(request)
        cart.add(product, unit_price=product.price)
        return shop, request, cart

    @patch('miaiqi_cards.shop.views.send_order_email')
    def test_confirmation_cart_is_retained_until_a_new_order(self, send_order_email):
        shop, request, cart = self.create_checkout()
        session = request.session
        checked_out_cart_id = cart.cart.pk

        with self.captureOnCommitCallbacks(execute=True):
            response = confirmation_view(request, shop_id=shop.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            session[ShopRenderer.CONFIRMATION_CART_SESSION_KEY],
            checked_out_cart_id,
        )
        self.assertTrue(CartModel.objects.get(pk=checked_out_cart_id).checked_out)
        order = Order.objects.get(cart_id=checked_out_cart_id)
        self.assertEqual(order.cart_data['items'][0]['product'], 'Test Postcard')
        self.assertEqual(order.cart_data['items'][0]['quantity'], 1)
        self.assertEqual(order.cart_data['total'], '4.50')
        self.assertEqual(order.email_address, 'test@example.com')
        self.assertEqual(order.first_name, 'Test')
        self.assertEqual(order.last_name, 'Customer')
        self.assertEqual(order.street, 'Test Street 1')
        self.assertEqual(order.city, 'Test City')
        self.assertEqual(order.postal_code, '12345')
        send_order_email.enqueue.assert_called_once_with(order.pk)

        confirmation_request = RequestFactory().get('/shop/')
        confirmation_request.session = session
        html = ShopRenderer(shop, confirmation_request).get_confirmation_html()
        self.assertIn('Test Postcard', html)

        description_request = RequestFactory().get('/shop/')
        description_request.session = session
        description_view(description_request, shop_id=shop.pk)
        self.assertNotIn(ShopRenderer.CONFIRMATION_CART_SESSION_KEY, session)
        self.assertTrue(Cart(description_request).is_empty())

    @patch('miaiqi_cards.shop.views.send_order_email')
    @patch('miaiqi_cards.shop.views.serialize_cart', side_effect=RuntimeError('snapshot failed'))
    def test_checkout_is_rolled_back_if_order_creation_fails(self, serialize_cart, send_order_email):
        shop, request, cart = self.create_checkout()

        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaisesRegex(RuntimeError, 'snapshot failed'):
                confirmation_view(request, shop_id=shop.pk)

        self.assertFalse(CartModel.objects.get(pk=cart.cart.pk).checked_out)
        self.assertFalse(Order.objects.filter(cart_id=cart.cart.pk).exists())
        send_order_email.enqueue.assert_not_called()

    @patch('miaiqi_cards.shop.views.send_order_email')
    def test_email_is_not_queued_when_outer_transaction_rolls_back(self, send_order_email):
        shop, request, cart = self.create_checkout()

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            with self.assertRaisesRegex(RuntimeError, 'rollback'):
                with transaction.atomic():
                    confirmation_view(request, shop_id=shop.pk)
                    send_order_email.enqueue.assert_not_called()
                    raise RuntimeError('rollback')

        self.assertEqual(callbacks, [])
        self.assertFalse(CartModel.objects.get(pk=cart.cart.pk).checked_out)
        self.assertFalse(Order.objects.filter(cart_id=cart.cart.pk).exists())
        send_order_email.enqueue.assert_not_called()

    def test_checkout_reports_specific_cart_errors(self):
        shop, request, cart = self.create_checkout()
        for error, message in (
            (CartException, 'The cart is empty.'),
            (MinimumOrderNotMet, 'The minimum order requirement is not met.'),
            (InvalidDiscountError, 'The discount applied is invalid.'),
        ):
            with self.subTest(error=error):
                with patch.object(Cart, 'checkout', side_effect=error):
                    response = confirmation_view(request, shop_id=shop.pk)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.content.decode(), message)


class ProductWidgetTests(TestCase):
    def setUp(self):
        self.shop = ShopSection.objects.create(title='Test Shop')
        self.page = MiaiqiCardsPage.objects.create(
            title='Home',
            slug='home',
            page_type=ContentType.objects.get_for_model(MiaiqiCardsPage),
        )

    def add_shop_to_page(self):
        PageSection.objects.create(page=self.page, section=self.shop, region='main', index=0)

    def render(self, content, request=None):
        template = Template('{% load shop %}{% product_widget content %}')
        return template.render(Context({'content': content, 'request': request, 'page': self.page}))

    def test_renders_readonly_quantity_between_minus_and_plus(self):
        self.add_shop_to_page()
        postcard = Postcard.objects.create(title='Test Postcard')
        product = Product.objects.get_from_content(postcard)

        html = self.render(postcard)

        self.assertIn(f'data-product="{product.pk}"', html)
        self.assertIn(f'data-url="/shop/{self.shop.pk}/update-product/{product.pk}/"', html)
        self.assertEqual(html.count('data-delta='), 2)
        self.assertIn('readonly', html)
        self.assertLess(html.index('product-minus'), html.index('product-quantity'))
        self.assertLess(html.index('product-quantity'), html.index('product-plus'))
        self.assertIn('value="0"', html)
        self.assertLess(html.index('product-price'), html.index('product-plus'))
        self.assertIn('class="product-price" value="" readonly', html)

    def test_shows_quantity_and_total_price_of_the_open_cart(self):
        self.add_shop_to_page()
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')
        product = Product.objects.get_from_content(postcard_set)
        request = RequestFactory().get('/')
        request.session = {}
        Cart(request).add(product, unit_price=product.price, quantity=3)

        html = self.render(postcard_set, request)

        self.assertIn('value="3"', html)
        self.assertIn(f'value="{3 * product.price} €"', html)

    def test_does_not_create_a_cart(self):
        self.add_shop_to_page()
        postcard = Postcard.objects.create(title='Test Postcard')
        request = RequestFactory().get('/')
        request.session = {}

        self.render(postcard, request)

        self.assertFalse(CartModel.objects.exists())

    def test_renders_nothing_without_a_shop_on_the_page(self):
        postcard = Postcard.objects.create(title='Test Postcard')

        self.assertNotIn('product-widget', self.render(postcard))

    def test_pages_of_single_postcard_sets_render_without_widgets(self):
        # Their page object has no shop section, so the templates skip the widget.
        sets_section = SetsSection.objects.create(title='Sets', slug='sets')
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')
        PostcardSetPostcard.objects.create(postcard_set=postcard_set, postcard=postcard, index=0)

        response = self.client.get(reverse(
            'postcard_set',
            kwargs={'sets_section_slug': sets_section.slug, 'set_slug': postcard_set.slug},
        ))

        self.assertContains(response, 'Test Postcard')
        self.assertNotContains(response, 'class="product-widget"')

    def test_widgets_are_rendered_for_the_gallery_and_the_sets_section(self):
        self.add_shop_to_page()
        gallery = GallerySection.objects.create(title='Gallery', slug='gallery')
        sets_section = SetsSection.objects.create(title='Sets', slug='sets')
        for index, section in enumerate((gallery, sets_section), start=1):
            PageSection.objects.create(page=self.page, section=section, region='main', index=index)
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')
        PostcardSetPostcard.objects.create(postcard_set=postcard_set, postcard=postcard, index=0)

        response = self.client.get(reverse('page'))

        for content in (postcard, postcard_set):
            product = Product.objects.get_from_content(content)
            self.assertContains(response, f'data-product="{product.pk}"')
        self.assertContains(response, 'class="product-widget"', count=2)
        self.assertContains(response, 'data-step="description"')

    def test_renders_nothing_without_a_product(self):
        self.add_shop_to_page()
        postcard = Postcard.objects.create(title='Test Postcard')
        Product.objects.all().delete()

        self.assertNotIn('product-widget', self.render(postcard))


class UpdateProductTests(TestCase):
    def test_sets_quantity_and_removes_product_with_zero(self):
        shop = ShopSection.objects.create(title='Test Shop')
        postcard = Postcard.objects.create(title='Test Postcard')
        product = Product.objects.get(
            content_type=ContentType.objects.get_for_model(postcard),
            object_id=postcard.pk,
        )
        request = RequestFactory().get('/')
        request.session = {}

        def update(quantity):
            request.GET = QueryDict(f'quantity={quantity}')
            update_product(request, shop.pk, product.pk)
            return Cart(request).count()

        request.GET = QueryDict('quantity=2')
        answer = json.loads(update_product(request, shop.pk, product.pk).content)
        self.assertIn('Test Postcard', answer['html'])
        self.assertEqual(
            answer['data'],
            {str(product.pk): {'quantity': 2, 'total_price': str(2 * product.price)}},
        )
        request.session.clear()

        self.assertEqual(update(2), 2)
        self.assertEqual(update(5), 5)
        self.assertEqual(update(0), 0)
        self.assertEqual(update(0), 0)
        self.assertTrue(Cart(request).is_empty())

        for query in ('', 'quantity=abc', 'quantity=-1'):
            request.GET = QueryDict(query)
            self.assertEqual(update_product(request, shop.pk, product.pk).status_code, 400)


class EmailFormTests(SimpleTestCase):
    def test_matching_emails_are_valid(self):
        form = EmailForm({
            'email_address': 'test@example.com',
            'repeated_email_address': 'test@example.com',
        })

        self.assertTrue(form.is_valid())

    def test_mismatch_marks_the_repeated_field_on_checkout(self):
        form = EmailForm({
            'email_address': 'test@example.com',
            'repeated_email_address': 'other@example.com',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('Die E-Mail-Adressen stimmen nicht überein.', form.errors['repeated_email_address'])
        html = render_to_string('shop/checkout.html', {
            'shop': SimpleNamespace(
                id=1,
                terms_and_conditions=SimpleNamespace(url='/terms.pdf'),
                cancellation_policy=SimpleNamespace(url='/cancellation.pdf'),
            ),
            'address_form': AddressForm(),
            'email_form': form,
            'legal_form': LegalForm(),
        }, RequestFactory().get('/'))
        self.assertIn('<div class="error"><input type="text" name="repeated_email_address"', html)

    def test_invalid_first_email_does_not_add_a_mismatch_error(self):
        form = EmailForm({
            'email_address': 'invalid',
            'repeated_email_address': 'test@example.com',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email_address', form.errors)
        self.assertNotIn('repeated_email_address', form.errors)
