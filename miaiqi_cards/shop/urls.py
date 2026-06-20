from django.urls import path

from . import views

urlpatterns = [
    path('formset/', views.formset, name='shop-formset'),
    path('cart/', views.checkout, name='shop-cart'),
    path('confirmation/', views.buy, name='shop-confirmation'),
]
