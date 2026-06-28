from django.urls import path
from .views import order_view, checkout_view, confirmation_view


urlpatterns = [
    path('shop/<int:shop_id>/order/', order_view, name='shop-order'),
    path('shop/<int:shop_id>/checkout/', checkout_view, name='shop-checkout'),
    path('shop/<int:shop_id>/confirmation/', confirmation_view, name='shop-confirmation'),
]
