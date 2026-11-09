from django.urls import path
from .views import postcard_view


urlpatterns = [
    path('<str:gallery_slug>/<int:postcard_id>/', postcard_view, name='postcard'),
    path('<str:sets_section_slug>/<str:set_slug>/', postcard_view, name='postcard_set'),
    path('<str:sets_section_slug>/<str:set_slug>/<int:postcard_id>', postcard_view, name='set_postcard'),
]
