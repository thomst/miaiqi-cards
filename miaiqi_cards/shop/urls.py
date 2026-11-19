from django.urls import path
from . import views


urlpatterns = [
    path('shop/<int:shop_id>/update-cart/', views.update_cart, name='update-cart'),
    path('shop/<int:shop_id>/update-product/<int:product_id>/', views.update_product, name='update-product'),
    path('shop/<int:shop_id>/description/', views.description_view, name='shop-description'),
    path('shop/<int:shop_id>/order/', views.order_view, name='shop-order'),
    path('shop/<int:shop_id>/checkout/', views.checkout_view, name='shop-checkout'),
    path('shop/<int:shop_id>/confirmation/', views.confirmation_view, name='shop-confirmation'),
]
