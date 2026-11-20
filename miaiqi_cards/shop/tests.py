import json
from django.http import QueryDict
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from cart.cart import Cart
from cart.models import Cart as CartModel
from .forms import CartItemForm
from miaiqi_cards.postcards.models import GallerySection, Postcard, PostcardSet, PostcardSetPostcard, SetsSection
from miaiqi_cards.website.models import MiaiqiCardsPage
from simple_page.models import PageSection
from .models import Product, ShopSection
from .renderers import ShopRenderer
from .views import confirmation_view, description_view, order_view, update_cart, update_product


class ProductTest(TestCase):
    def test_grouped_product_choices_are_lazy(self):
        field = CartItemForm.base_fields['product']

        choices = field.choices

        self.assertIsNone(field.queryset._result_cache)
        self.assertEqual(list(choices), [('', '---------')])

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
        self.shop = ShopSection.objects.create(title='Test Shop', description_text='All about **cards**')

    def request(self, session=None):
        request = RequestFactory().get('/')
        request.session = {} if session is None else session
        return request

    def test_description_is_the_initial_step(self):
        html = ShopRenderer(self.shop, self.request()).get_html()

        self.assertIn('<strong>cards</strong>', html)
        self.assertIn(f'data-url="/shop/{self.shop.pk}/order/"', html)
        self.assertIn('data-method="get"', html)
        self.assertNotIn('form-TOTAL_FORMS', html)

    def test_get_html_continues_with_the_step_stored_in_the_session(self):
        session = {'shop-state': ShopRenderer.ORDER_STATE}

        html = ShopRenderer(self.shop, self.request(session)).get_html()

        self.assertIn('form-TOTAL_FORMS', html)

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
            ('checkout', renderer.get_checkout_html()),
            ('confirmation', renderer.get_confirmation_html()),
        ]:
            self.assertIn(f'<div class="shop" data-step="{step}">', html)

    def test_order_step_has_the_add_button_in_the_header_and_a_back_button_below(self):
        html = ShopRenderer(self.shop, self.request()).get_order_html()

        self.assertEqual(html.count('class="add-form"'), 1)
        self.assertLess(html.index('class="add-form"'), html.index('class="row form"'))
        back = html[html.index('value="Back"'):]
        self.assertIn(f'data-url="/shop/{self.shop.pk}/description/"', back.split('>')[0])
        self.assertIn('data-method="get"', back.split('>')[0])

    def test_confirmation_leads_back_to_the_description(self):
        html = ShopRenderer(self.shop, self.request()).get_confirmation_html()

        self.assertIn(f'data-url="/shop/{self.shop.pk}/description/"', html)
        self.assertIn('value="Back"', html)


class ShopCartSessionTests(TestCase):
    def test_confirmation_cart_is_retained_until_a_new_order(self):
        shop = ShopSection.objects.create(title='Test Shop')
        postcard = Postcard.objects.create(title='Test Postcard')
        product = Product.objects.get(
            content_type=ContentType.objects.get_for_model(postcard),
            object_id=postcard.pk,
        )

        session = {}
        request = RequestFactory().post(
            '/shop/',
            {'email_address': 'test@example.com', 'repeated_email_address': 'test@example.com'},
        )
        request.session = session
        cart = Cart(request)
        cart.add(product, unit_price=product.price)
        checked_out_cart_id = cart.cart.pk

        response = confirmation_view(request, shop_id=shop.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            session[ShopRenderer.CONFIRMATION_CART_SESSION_KEY],
            checked_out_cart_id,
        )
        self.assertTrue(CartModel.objects.get(pk=checked_out_cart_id).checked_out)

        confirmation_request = RequestFactory().get('/shop/')
        confirmation_request.session = session
        html = ShopRenderer(shop, confirmation_request).get_confirmation_html()
        self.assertIn('Test Postcard', html)

        description_request = RequestFactory().get('/shop/')
        description_request.session = session
        description_view(description_request, shop_id=shop.pk)
        self.assertNotIn(ShopRenderer.CONFIRMATION_CART_SESSION_KEY, session)
        self.assertTrue(Cart(description_request).is_empty())


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
        template = Template('{% load product %}{% product_widget content %}')
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
        self.assertIn('form-TOTAL_FORMS', answer['html'])
        self.assertEqual(
            answer['quantities'],
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


class UpdateCartTests(TestCase):
    def test_returns_the_quantities_of_the_saved_cart_by_product_id(self):
        # The last row of a repeated product wins and invalid rows are skipped.
        shop = ShopSection.objects.create(title='Test Shop')
        first = Product.objects.get_from_content(Postcard.objects.create(title='First'))
        second = Product.objects.get_from_content(Postcard.objects.create(title='Second'))
        request = RequestFactory().post('/', {
            'form-TOTAL_FORMS': '4',
            'form-INITIAL_FORMS': '0',
            'form-0-product': first.pk,
            'form-0-quantity': '2',
            'form-1-product': second.pk,
            'form-1-quantity': '1',
            'form-2-product': first.pk,
            'form-2-quantity': '3',
            'form-3-product': '',
            'form-3-quantity': '',
        })
        request.session = {}

        response = update_cart(request, shop.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                str(first.pk): {'quantity': 3, 'total_price': str(3 * first.price)},
                str(second.pk): {'quantity': 1, 'total_price': str(second.price)},
            },
        )
