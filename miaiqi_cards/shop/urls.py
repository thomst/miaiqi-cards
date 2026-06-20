from django.urls import path

from .views import ShopView

urlpatterns = [
    path('shop/<int:shop_id>/order/', ShopView.order, name='shop-order'),
    path('shop/<int:shop_id>/checkout/', ShopView.checkout, name='shop-checkout'),
    path('shop/<int:shop_id>/confirmation/', ShopView.confirmation, name='shop-confirmation'),
]
