from cart.cart import CartException, MinimumOrderNotMet, InvalidDiscountError
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from .order.models import Order
from .order.orders import send_order_email, serialize_cart
from .renderers import ShopRenderer
from .models import ShopSection
from . import forms


@require_GET
def update_product(request, shop_id, product_id):
    try:
        quantity = int(request.GET['quantity'])
    except (KeyError, ValueError):
        return HttpResponseBadRequest('A numeric quantity is required.')
    if quantity < 0:
        return HttpResponseBadRequest('The quantity must not be negative.')

    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)

    shop.update_product(product_id, quantity)
    return JsonResponse(dict(
        html=shop.get_order_html(),
        data=shop.get_cart_data()
        ))


@require_GET
def description_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)
    shop.confirmation_cart = None
    return HttpResponse(shop.get_description_html())


@require_GET
def order_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)
    return HttpResponse(shop.get_order_html())


@require_GET
def cart_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)
    return HttpResponse(shop.get_cart_html())


@require_GET
def checkout_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)
    return HttpResponse(shop.get_checkout_html())


@require_POST
def confirmation_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)

    address_form = forms.AddressForm(request.POST)
    email_form = forms.EmailForm(request.POST)
    legal_form = forms.LegalForm(request.POST)
    if all(f.is_valid() for f in (address_form, email_form, legal_form)):
        if shop.cart.cart.checked_out:
            return HttpResponseBadRequest('Cart has already been checked out.')
        try:
            with transaction.atomic():
                shop.cart.checkout()
                order = Order.objects.create(
                    cart_id=shop.cart.cart.pk,
                    cart_data=serialize_cart(shop.cart),
                    first_name=address_form.cleaned_data['first_name'],
                    last_name=address_form.cleaned_data['last_name'],
                    street=address_form.cleaned_data['street'],
                    city=address_form.cleaned_data['city'],
                    postal_code=address_form.cleaned_data['postal_code'],
                    email_address=email_form.cleaned_data['email_address'],
                )
        except MinimumOrderNotMet:
            return HttpResponseBadRequest('The minimum order requirement is not met.')
        except InvalidDiscountError:
            return HttpResponseBadRequest('The discount applied is invalid.')
        except CartException:
            return HttpResponseBadRequest('The cart is empty.')

        transaction.on_commit(lambda: send_order_email.enqueue(order.pk))
        shop.confirmation_cart = shop.cart
        return HttpResponse(shop.get_confirmation_html())
    else:
        return HttpResponse(shop.get_checkout_html(
            address_form=address_form,
            email_form=email_form,
            legal_form=legal_form
        ))
