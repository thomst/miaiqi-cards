from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from .renderers import ShopRenderer
from .models import ShopSection
from . import forms


@require_POST
def update_cart(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)

    renderer.update_cart()
    return HttpResponse(status=204)


@require_GET
def order_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)
    return HttpResponse(renderer.get_order_html())


@require_POST
def checkout_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)

    formset = renderer.formset_class(request.POST)
    if formset.is_valid():
        renderer.setup_cart(formset.cleaned_data)
        return HttpResponse(renderer.get_checkout_html())
    else:
        return HttpResponse(renderer.get_order_html(formset))


@require_POST
def confirmation_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)

    email_form = forms.EmailForm(request.POST)
    if email_form.is_valid():
        # TODO: Send confirmation email.
        renderer.cart.checkout()
        return HttpResponse(renderer.get_confirmation_html())
    else:
        return HttpResponse(renderer.get_checkout_html(email_form))


