from django.urls import path
from . import views

urlpatterns = [
    path('', views.postcard_list, name='postcard_list'),
    path('<int:pk>/', views.postcard_detail, name='postcard_detail'),
]