from django.urls import path

from . import views

urlpatterns = [
    path('<int:postcard_id>/', views.postcard, name='postcard'),
]
