from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from .renderers import ShopRenderer
from .models import ShopSection
from . import forms


@require_POST
def update_cart(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)

    shop.update_cart()
    return HttpResponse(status=204)


@require_GET
def order_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)
    return HttpResponse(shop.get_order_html())


@require_POST
def checkout_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)

    formset = shop.formset_class(request.POST)
    if formset.is_valid():
        shop.setup_cart(formset.cleaned_data)
        return HttpResponse(shop.get_checkout_html())
    else:
        return HttpResponse(shop.get_order_html(formset))


@require_POST
def confirmation_view(request, shop_id):
    section = get_object_or_404(ShopSection, pk=shop_id)
    shop = ShopRenderer(section, request)

    email_form = forms.EmailForm(request.POST)
    if email_form.is_valid():
        # TODO: Send confirmation email.
        shop.cart.checkout()
        return HttpResponse(shop.get_confirmation_html())
    else:
        return HttpResponse(shop.get_checkout_html(email_form))
