from django.forms import formset_factory, ModelChoiceField
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from simple_page import renderers
from cart.cart import Cart
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
    ORDER_STATE = 'order'
    CHECKOUT_STATE = 'checkout'
    CONFIRMATION_STATE = 'confirmation'

    class Media:
        css = dict(all=['css/shop.css'])
        js = ['js/shop.js']

    @property
    def state(self):
        return self.request.session.get('shop-state')

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

    def update_product(self, product_id, quantity):
        if self.cart.has_product(product_id) and not quantity:
            self.cart.remove_product(product_id)
        elif self.cart.has_product(product_id) and quantity:
            self.cart.update_product(product_id, quantity)
        elif not self.cart.has_product(product_id) and quantity:
            self.cart.add_product(product_id, quantity)

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
        context = dict(shop=self.section, cart=self.cart)
        return render_to_string('shop/confirmation.html', context, self.request)

    def get_html(self):
        if not self.state or self.state == self.ORDER_STATE:
            return self.get_order_html()
        if self.state == self.CHECKOUT_STATE:
            return self.get_checkout_html()
        elif self.state == self.CONFIRMATION_STATE:
            return self.get_confirmation_html()

    def get_context_data(self):
        context = super().get_context_data()
        context['shop_html'] = self.get_html()
        return context
