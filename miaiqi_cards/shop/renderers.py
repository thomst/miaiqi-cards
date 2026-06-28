from django.forms import formset_factory, ModelChoiceField
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from simple_page import renderers
from cart.cart import Cart, InvalidDiscountError
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
        css = dict(all=['shop/shop.css'])
        js = ['shop/shop.js']

    @property
    def state(self):
        return self.request.session.get('shop-state')

    @cached_property
    def cart(self):
        return Cart(self.request)

    @cached_property
    def formset_class(self):
        # FIXME: Update limit_choices_to on formfield instead of creating new field and form.
        field = ModelChoiceField(self.obj.gallery.postcards.all(), required=True)
        form_class = type('CartItemForm', (forms.CartItemForm,), dict(product=field))
        return formset_factory(form_class, extra=0, min_num=1, validate_min=True)

    def setup_cart(self, data):
        self.cart.clear()
        self.cart.remove_discount()
        price = self.obj.prices.first().price  # FIXME: Selection should come from the forms.
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
            formset = self.formset_class()
        elif 'checkout' in self.request.GET:
            formset = self.formset_class(self.request.POST)
        elif not self.cart.is_empty():
            initial = [dict(product=i.product.pk, quantity=i.quantity) for i in self.cart]
            formset = self.formset_class(initial=initial)
        else:
            formset = self.formset_class()
        context = dict(shop=self.obj, formset=formset)
        return render_to_string('shop/order.html', context, self.request)

    @set_state(CHECKOUT_STATE)
    def get_checkout_html(self):
        if 'checkout' in self.request.GET:
            formset = self.formset_class(self.request.POST)
            if formset.is_valid():
                self.setup_cart(formset.cleaned_data)
                email_form = forms.EmailForm()
                context = dict(shop=self.obj, cart=self.cart, email_form=email_form)
                return render_to_string('shop/checkout.html', context, self.request)
            else:
                return self.get_order_html()
        elif 'buy' in self.request.GET:
            email_form = forms.EmailForm(self.request.POST)
            context = dict(shop=self.obj, cart=self.cart, email_form=email_form)
            return render_to_string('shop/checkout.html', context, self.request)
        else:
            email_form = forms.EmailForm()
            context = dict(shop=self.obj, cart=self.cart, email_form=email_form)
            return render_to_string('shop/checkout.html', context, self.request)

    @set_state(CONFIRMATION_STATE)
    def get_confirmation_html(self):
        if 'buy' in self.request.GET:
            email_form = forms.EmailForm(self.request.POST)
            if email_form.is_valid():
                # TODO: Send confirmation email.
                self.cart.checkout()
                context = dict(shop=self.obj, cart=self.cart)
                return render_to_string('shop/confirmation.html', context, self.request)
            else:
                return self.get_checkout_html()
        else:
            return self.get_order_html()


    def get_html(self):
        if self.state == self.ORDER_STATE or not self.state:
            return self.get_order_html()
        if self.state == self.CHECKOUT_STATE:
            return self.get_checkout_html()
        elif self.state == self.CONFIRMATION_STATE:
            return self.get_confirmation_html()

    def get_context(self):
        context = super().get_context()
        context['shop_html'] = self.get_html()
        return context
