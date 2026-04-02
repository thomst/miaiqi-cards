from django.urls import path
from . import views

urlpatterns = [
    path('', views.page, name='page'),
    path('postcard/<int:pk>/', views.postcard, name='postcard'),
]