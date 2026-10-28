from django.urls import path
from simple_page.views import page_view


urlpatterns = [
    path('<str:slug>/', page_view, name='first_postcard'),
    path('<str:slug>/<int:postcard_id>/', page_view, name='postcard'),
]
