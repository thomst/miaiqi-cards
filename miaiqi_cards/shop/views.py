from django.shortcuts import get_object_or_404
from django.forms import formset_factory, ModelChoiceField
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.http import HttpResponse
from cart.cart import Cart, InvalidDiscountError
from . import models
from . import forms


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

    @property
    def old_state(self):
        return self.request.session.get('old-shop-state')

    @state.setter
    def state(self, value):
        self.request.session['old-shop-state'] = self.state
        self.request.session['shop-state'] = value

    @cached_property
    def formset_class(self):
        # FIXME: Update limit_choices_to on formfield instead of creating new field and form.
        field = ModelChoiceField(self.shop.gallery.postcards.all(), required=True)
        form_class = type('CartItemForm', (forms.CartItemForm,), dict(product=field))
        extra = 1 if self.cart.is_empty() else 0
        return formset_factory(form_class, extra=extra, min_num=1, validate_min=True)

    @cached_property
    def formset(self):
        if self.request.POST and self.old_state == self.ORDER_STATE:
            return self.formset_class(self.request.POST)
        elif not self.cart.is_empty():
            initial = [dict(product=i.product.pk, quantity=i.quantity) for i in self.cart]
            return self.formset_class(initial=initial)
        else:
            return self.formset_class()

    @cached_property
    def email_form(self):
        if self.request.POST and self.old_state == self.CHECKOUT_STATE:
            return forms.EmailForm(self.request.POST)
        else:
            return forms.EmailForm()

    def checkout_cart(self, data):
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

    def get_order_html(self):
        self.state = self.ORDER_STATE
        return render_to_string('shop/order.html', dict(shop=self), self.request)

    def get_checkout_html(self):
        self.state = self.CHECKOUT_STATE
        if self.old_state in [self.CHECKOUT_STATE, self.CONFIRMATION_STATE]:
            return render_to_string('shop/checkout.html', dict(shop=self), self.request)
        elif self.formset.is_valid():
            self.checkout_cart(self.formset.cleaned_data)
            return render_to_string('shop/checkout.html', dict(shop=self), self.request)
        else:
            return self.get_order_html()

    def get_confirmation_html(self):
        self.state = self.CONFIRMATION_STATE
        if self.email_form.is_valid():
            # TODO: Send confirmation email.
            self.cart.checkout()
            render_to_string('shop/confirmation.html', dict(shop=self), self.request)
        else:
            return self.get_checkout_html()

    @cached_property
    def html(self):
        if not self.state or self.state == self.ORDER_STATE:
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
