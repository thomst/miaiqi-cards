from django.shortcuts import get_object_or_404
from django.forms import formset_factory, ModelChoiceField
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.http import HttpResponse
from cart.cart import Cart, InvalidDiscountError
from cart.session import DjangoSessionAdapter
from cart.cart import CART_ID
from . import models
from . import forms


def set_state(state):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.request.session['shop-state'] = state
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


class ShopView:
    ORDER_STATE = 'order'
    CHECKOUT_STATE = 'checkout'
    CONFIRMATION_STATE = 'confirmation'


    def __init__(self, request, shop_id):
        self.request = request
        self.shop = get_object_or_404(models.Shop, pk=shop_id)

    @cached_property
    def cart(self):
        return Cart(self.request)

    @property
    def state(self):
        return self.request.session.get('shop-state')

    # FIXME: Use a get_formset_class with extra argument.
    @property
    def formset_class(self):
        # FIXME: Update limit_choices_to on formfield instead of creating new field and form.
        field = ModelChoiceField(self.shop.gallery.postcards.all(), required=True)
        form_class = type('CartItemForm', (forms.CartItemForm,), dict(product=field))
        extra = 1 if self.cart.is_empty() else 0
        return formset_factory(form_class, extra=extra, min_num=1, validate_min=True)

    def setup_cart(self, data):
        self.cart.clear()
        self.cart.remove_discount()
        price = self.shop.prices.first().price  # FIXME: Selection should come from the forms.
        data = [dict(**d, unit_price=price) for d in data if d]
        self.cart.add_bulk(data)

        # Apply quantity discount.
        for discount in models.QuantityDiscount.objects.all():
            try:
                self.cart.apply_discount(discount.code)
            except InvalidDiscountError:
                pass
            else:
                break

    @set_state(ORDER_STATE)
    def get_order_html(self):
        if 'new' in self.request.GET:
            DjangoSessionAdapter(self.request).delete(CART_ID)
            formset = self.formset_class()
        elif 'checkout' in self.request.GET:
            formset = self.formset_class(self.request.POST)
        elif not self.cart.is_empty():
            initial = [dict(product=i.product.pk, quantity=i.quantity) for i in self.cart]
            formset = self.formset_class(initial=initial)
        else:
            formset = self.formset_class()
        context = dict(shop=self, formset=formset)
        return render_to_string('shop/order.html', context, self.request)

    @set_state(CHECKOUT_STATE)
    def get_checkout_html(self):
        if 'checkout' in self.request.GET:
            formset = self.formset_class(self.request.POST)
            if formset.is_valid():
                self.setup_cart(formset.cleaned_data)
                email_form = forms.EmailForm()
                context = dict(shop=self, cart=self.cart, email_form=email_form)
                return render_to_string('shop/checkout.html', context, self.request)
            else:
                return self.get_order_html()
        elif 'buy' in self.request.GET:
            email_form = forms.EmailForm(self.request.POST)
            context = dict(shop=self, cart=self.cart, email_form=email_form)
            return render_to_string('shop/checkout.html', context, self.request)
        else:
            email_form = forms.EmailForm()
            context = dict(shop=self, cart=self.cart, email_form=email_form)
            return render_to_string('shop/checkout.html', context, self.request)

    @set_state(CONFIRMATION_STATE)
    def get_confirmation_html(self):
        if 'buy' in self.request.GET:
            email_form = forms.EmailForm(self.request.POST)
            if email_form.is_valid():
                # TODO: Send confirmation email.
                self.cart.checkout()
                context = dict(shop=self, cart=self.cart)
                return render_to_string('shop/confirmation.html', context, self.request)
            else:
                return self.get_checkout_html()
        else:
            context = dict(shop=self, cart=self.cart)
            return render_to_string('shop/confirmation.html', context, self.request)

    @property
    def html(self):
        if self.state == self.ORDER_STATE or not self.state:
            return self.get_order_html()
        if self.state == self.CHECKOUT_STATE:
            return self.get_checkout_html()
        elif self.state == self.CONFIRMATION_STATE:
            return self.get_confirmation_html()

    @classmethod
    def order(cls, request, shop_id):
        shop = cls(request, shop_id)
        return HttpResponse(shop.get_order_html())

    @classmethod
    def checkout(cls, request, shop_id):
        shop = cls(request, shop_id)
        return HttpResponse(shop.get_checkout_html())

    @classmethod
    def confirmation(cls, request, shop_id):
        shop = cls(request, shop_id)
        return HttpResponse(shop.get_confirmation_html())
