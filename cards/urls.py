from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('galery/', views.galery, name='galery'),
    path('<int:pk>/', views.postcard, name='postcard'),
]