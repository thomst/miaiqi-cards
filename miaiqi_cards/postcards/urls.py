from django.urls import path

from . import views

urlpatterns = [
    path('postcard/<int:postcard_id>/', views.postcard, name='postcard'),
]
