from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from simple_page import renderers
from cart.cart import Cart
from cart.models import Cart as CartModel
from . import models
from . import forms


def set_state(state):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.request.session['shop-state'] = state
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


@renderers.register(models.ShopSection)
class ShopRenderer(renderers.SectionRenderer):
    DESCRIPTION_STATE = 'description'
    ORDER_STATE = 'order'
    CHECKOUT_STATE = 'checkout'
    CONFIRMATION_STATE = 'confirmation'
    CONFIRMATION_CART_SESSION_KEY = 'shop-confirmation-cart-id'

    class Media:
        css = dict(all=['css/shop.css', 'css/product_widget.css'])
        js = ['js/shop.js']

    @property
    def state(self):
        return self.request.session.get('shop-state')

    @property
    def confirmation_cart(self):
        cart_id = self.request.session.get(self.CONFIRMATION_CART_SESSION_KEY)
        try:
            checked_out_cart = CartModel.objects.get(pk=cart_id, checked_out=True)
        except CartModel.DoesNotExist:
            return None
        else:
            cart = Cart(self.request)
            cart.cart = checked_out_cart
            return cart

    @confirmation_cart.setter
    def confirmation_cart(self, cart):
        if cart is None:
            self.request.session.pop(self.CONFIRMATION_CART_SESSION_KEY, None)
        else:
            self.request.session[self.CONFIRMATION_CART_SESSION_KEY] = cart.cart.pk

    @cached_property
    def cart(self):
        return Cart(self.request)

    @cached_property
    def formset_class(self):
        return formset_factory(forms.CartItemForm, extra=0, min_num=1, validate_min=True)

    def setup_cart(self, data):
        self.cart.clear()
        data = [dict(**d, unit_price=d['product'].price) for d in data if d]
        self.cart.add_bulk(data)

    def update_cart(self):
        formset = self.formset_class(self.request.POST)
        data = list()
        for form in formset.forms:
            if form.is_valid():
                data.append(form.cleaned_data)
        self.setup_cart(data)

    def get_quantities(self):
        """Return quantity and total price of the cart items by their product ids."""
        return {
            item.object_id: dict(quantity=item.quantity, total_price=str(item.total_price))
            for item in self.cart
        }

    def update_product(self, product_id, quantity):
        product = get_object_or_404(models.Product, pk=product_id)
        if product in self.cart:
            self.cart.update(product, quantity, unit_price=product.price)
        elif quantity:
            self.cart.add(product, unit_price=product.price, quantity=quantity)

    @set_state(DESCRIPTION_STATE)
    def get_description_html(self):
        context = dict(shop=self.section)
        return render_to_string('shop/description.html', context, self.request)

    @set_state(ORDER_STATE)
    def get_order_html(self, formset=None):
        if not formset and not self.cart.is_empty():
            initial = [dict(product=i.product.pk, quantity=i.quantity) for i in self.cart]
            formset = self.formset_class(initial=initial)
        else:
            formset = formset or self.formset_class()

        context = dict(shop=self.section, formset=formset)
        return render_to_string('shop/order.html', context, self.request)

    @set_state(CHECKOUT_STATE)
    def get_checkout_html(self, email_form=None):
        email_form = email_form or forms.EmailForm()
        context = dict(shop=self.section, cart=self.cart, email_form=email_form)
        return render_to_string('shop/checkout.html', context, self.request)

    @set_state(CONFIRMATION_STATE)
    def get_confirmation_html(self):
        cart = self.confirmation_cart
        if cart is None:
            cart = self.cart
        context = dict(shop=self.section, cart=cart)
        return render_to_string('shop/confirmation.html', context, self.request)

    def get_html(self):
        if not self.state or self.state == self.DESCRIPTION_STATE:
            return self.get_description_html()
        if self.state == self.ORDER_STATE:
            return self.get_order_html()
        if self.state == self.CHECKOUT_STATE:
            return self.get_checkout_html()
        elif self.state == self.CONFIRMATION_STATE:
            return self.get_confirmation_html()

    def get_context_data(self):
        context = super().get_context_data()
        context['shop_html'] = self.get_html()
        return context
