from django.urls import path
from .views import gallery


urlpatterns = [
    path('<str:gallery_slug>/', gallery, name='gallery'),
    path('<str:gallery_slug>/<int:postcard_id>/', gallery, name='postcard'),
]
