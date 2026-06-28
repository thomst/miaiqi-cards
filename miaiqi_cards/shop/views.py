from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .renderers import ShopRenderer
from .models import ShopSection


def order_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, request)
    return HttpResponse(renderer.get_order_html())


def checkout_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, request)
    return HttpResponse(renderer.get_checkout_html())


def confirmation_view(request, shop_id):
    shop = get_object_or_404(ShopSection, pk=shop_id)
    renderer = ShopRenderer(shop, request)
    return HttpResponse(renderer.get_confirmation_html())
