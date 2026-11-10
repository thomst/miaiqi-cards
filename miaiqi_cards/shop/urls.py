from django.urls import path
from . import views


urlpatterns = [
    path('shop/<int:shop_id>/remove-product/', views.remove_product, name='remove-product'),
    path('shop/<int:shop_id>/order/', views.order_view, name='shop-order'),
    path('shop/<int:shop_id>/checkout/', views.checkout_view, name='shop-checkout'),
    path('shop/<int:shop_id>/confirmation/', views.confirmation_view, name='shop-confirmation'),
]
