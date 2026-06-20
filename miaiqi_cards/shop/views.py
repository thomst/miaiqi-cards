from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.forms import formset_factory, ModelChoiceField
from django.template.loader import render_to_string
from django.http import HttpResponse
from cart.cart import Cart, InvalidDiscountError
from . import models
from . import forms


class ShopView:
    def __init__(self, request, shop_id):
        self.request = request
        self.shop = get_object_or_404(models.Shop, pk=shop_id)

    @property
    def cart(self):
        return Cart(self.request)

    @property
    def formset_class(self):
        field = ModelChoiceField(self.shop.gallery.postcards.all(), required=True)
        form_class = type('CartItemForm', (forms.CartItemForm,), dict(product=field))
        return formset_factory(form_class, can_delete=True, extra=1)

    @property
    def formset(self):
        if not self.cart.is_empty():
            initial = [dict(procuct=i.product, quantity=i.quantity) for i in self.cart]
            self.cart.clear()
            return self.formset_class(initial=initial)
        elif self.request.POST:
            return self.formset_class(self.request.POST)
        else:
            return self.formset_class()

    @property
    def email_form(self):
        return forms.EmailForm(self.request.POST)

    def checkout_cart(self):
        self.cart.clear()
        price = self.shop.prices.first().price  # FIXME: Selection should come from the forms.
        data = [dict(**d, unit_price=price) for d in self.formset.cleaned_data]
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
        return render_to_string('shop/order.html', dict(shop=self))

    def get_checkout_html(self):
        if self.formset.is_valid():
            self.checkout_cart()
            return render_to_string('shop/checkout.html', dict(shop=self))
        else:
            return self.get_order_html()

    def get_confirmation_html(self):
        if self.email_form.is_valid():
            # TODO: Send confirmation email.
            self.cart.checkout()
            render(self.request, 'shop/confirmation.html', dict(shop=self))
        else:
            return self.get_checkout_html()

    @property
    def html(self):
        if self.cart.is_empty():
            return self.get_order_html()
        elif not self.cart.cart.checked_out:
            return self.get_checkout_html()
        else:
            return self.get_confirmation_html()

    @classmethod
    def order(cls, request, shop_id):
        shop = cls.__init__(request, shop_id)
        return HttpResponse(shop.get_order_html())

    @classmethod
    def checkout(cls, request, shop_id):
        shop = cls.__init__(request, shop_id)
        return HttpResponse(shop.get_checkout_html())

    @classmethod
    def confirmation(cls, request, shop_id):
        shop = cls.__init__(request, shop_id)
        return HttpResponse(shop.get_confirmation_html())
