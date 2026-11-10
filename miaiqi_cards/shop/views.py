from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .renderers import ShopRenderer
from .models import Product, ShopSection


def remove_product(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    cart = ShopRenderer(shop, None, None, request).cart
    product = get_object_or_404(Product, pk=request.POST['product'])
    if product in cart:
        cart.remove(product)
    return HttpResponse(status=204)


def order_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)
    return HttpResponse(renderer.get_order_html())


def checkout_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)
    return HttpResponse(renderer.get_checkout_html())


def confirmation_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, None, None, request)
    return HttpResponse(renderer.get_confirmation_html())
