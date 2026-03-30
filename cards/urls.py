from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('galery/', views.postcard_list, name='postcard_list'),
    path('<int:pk>/', views.postcard_detail, name='postcard_detail'),
]